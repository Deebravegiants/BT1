### Title
Unprivileged clients can front-run/squat gateway request IDs to block other users' confidential-relay requests - (File: `core/services/gateway/handlers/confidentialrelay/handler.go`)

### Summary
The `TunnlTwitterOffers.createOffer` bug class (user-supplied ID checked for existence before creation, allowing an attacker to front-run and "claim" the ID first, permanently blocking the legitimate caller) has a structural analog in the Chainlink gateway's `confidentialrelay` handler, which is directly reachable by unprivileged HTTP/gateway clients.

### Finding Description
`HandleJSONRPCUserMessage` accepts a client-supplied `req.ID` with only length/emptiness validation, and does not scope it to the caller's identity in the in-memory map: [1](#0-0) 

The ID is registered via `newActiveRequest`, which stores it in a single global map (`h.activeRequests`) keyed purely by `req.ID` and rejects any second registration with the same ID, regardless of who submitted it: [2](#0-1) 

This is functionally identical to `TunnlTwitterOffers.createOffer`'s `require(s_offers[offerId].creationDate == 0, ...)` check: whoever submits a given ID first "wins," and every subsequent legitimate submitter with the same ID is rejected (`"request ID already exists: " + req.ID"`). Because there is no per-caller/per-owner namespacing of the ID (unlike the Vault gateway handler, which prefixes IDs with the authorized workflow owner before checking for collisions/replay — see `gateway_vault_request_processor.go`'s "Prefix ID" step), any unprivileged client that can predict or observe another user's intended request ID ahead of time can preemptively submit a request with that same ID to block the legitimate request.

### Impact Explanation
An attacker can deny a specific user's confidential-relay request (e.g., a capability execution tied to a specific workflow/execution) by squatting the request ID before the legitimate client submits it. This is a targeted denial-of-service against a specific counterparty's request — mirroring the "Medium" severity/DoS-only nature of the original finding (no direct fund loss, but disruption of legitimate use and reputational/competitive risk). It does not expose secrets or bypass authentication, so it is analogous in kind and severity to the original: availability/griefing rather than fund or auth compromise.

### Likelihood Explanation
Likelihood depends on whether an attacker can learn or guess the victim's request ID before it is submitted to this specific gateway/handler instance. Unlike the on-chain mempool front-running scenario (where the transaction, including the offer ID, is publicly visible before inclusion), there is no public "mempool" here — the request ID is only known to the calling node/client until it is actually POSTed to the gateway. This significantly lowers likelihood versus the original report, since exploiting it requires either a predictable/derivable ID scheme or some other side channel to learn the ID in advance, which was not verified in the available code. I could not find (within index limits) how `req.ID` values are generated for confidential-relay requests, so I cannot confirm whether they are unpredictable (e.g., random UUIDs) or derivable from public data.

### Recommendation
- Scope `activeRequests` keys by both request ID and caller identity (e.g., prefix with the authenticated workflow owner/org, as already done in the Vault gateway handler's `gateway_vault_request_processor.go` "Prefix ID" step) so one caller cannot collide with another caller's namespace.
- Alternatively/additionally, require request IDs to be authenticated/derived server-side (e.g., signed or derived from the authenticated caller's key) rather than accepting an arbitrary client-supplied string as the sole collision key.

### Proof of Concept
Conceptual PoC (not verified end-to-end against a running gateway, based on `handler_test.go` patterns such as `TestConfidentialRelayHandler_DuplicateRequestID`):
1. Attacker observes/guesses the request ID that a legitimate user's node/client is about to submit for `MethodCapabilityExec` (or otherwise picks a low-entropy/predictable value).
2. Attacker submits their own `jsonrpc.Request[json.RawMessage]{ID: <victimID>, Method: MethodCapabilityExec, ...}` to `HandleJSONRPCUserMessage` first.
3. When the legitimate user then submits their request with the same ID, `newActiveRequest` returns `errors.New("request ID already exists: " + req.ID)` and the legitimate request is rejected, exactly as demonstrated in the existing test: [3](#0-2) 

**Caveat:** I was unable to fully verify the exact ID-generation scheme used by real clients/nodes for this handler (whether IDs are random/unpredictable or derivable), which materially affects real-world exploitability. Due to index size limits, some file contents (e.g., the full request-construction path used by legitimate callers) may not be available — a Devin session with full repository access would be needed to confirm ID predictability before treating this as a high-confidence, exploitable finding.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-411)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	labels := h.extractRequestLabels(req)
	l := h.requestLogger(req, labels)
	l.Debugw("handling confidential relay request", "nodes", len(h.donConfig.Members), "f", h.donConfig.F)

	ar, err := h.newActiveRequest(req, labels, callback)
	if err != nil {
		return err
	}

	return h.fanOutToNodes(ctx, l, ar)
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-430)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		labels:    labels,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L863-881)
```go
func TestConfidentialRelayHandler_DuplicateRequestID(t *testing.T) {
	t.Parallel()
	h, cb, don, _ := setupHandler(t, 4)
	don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

	params := json.RawMessage(`{"workflow_id":"wf1"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-dup",
		Method: MethodCapabilityExec,
		Params: &params,
	}

	err := h.HandleJSONRPCUserMessage(t.Context(), req, cb)
	require.NoError(t, err)

	cb2 := common.NewCallback()
	err = h.HandleJSONRPCUserMessage(t.Context(), req, cb2)
	require.ErrorContains(t, err, "request ID already exists")
}
```
