## Title
Cross-user request-ID squatting can permanently block a victim's gateway request from completing - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

## Summary
The confidential relay gateway handler (and analogously the vault gateway handler) keys in-flight requests in a single global `activeRequests` map by the JSON-RPC `req.ID` field, which is fully attacker-controlled and not scoped per caller/owner in this handler. This mirrors the report's bug class: an unprivileged party can pre-empt a resource identifier so that a legitimate operation targeting the same identifier permanently fails, blocking completion of that flow — the same "attacker griefs a specific in-flight operation, causing the whole flow to fail" pattern as the `fulfillQuery` refund-revert issue.

## Finding Description
`HandleJSONRPCUserMessage` validates only that `req.ID` is non-empty and ≤200 characters, then calls `h.newActiveRequest(req, labels, callback)`: [1](#0-0) 

`newActiveRequest` stores the request keyed purely by `req.ID` in a handler-wide map and rejects the request outright if that key is already present: [2](#0-1) 

There is no per-owner/per-sender namespacing of `req.ID` in this handler — unlike the vault gateway handler's `GatewayVaultRequestProcessor`, which explicitly prefixes/strips `owner::id` to avoid exactly this kind of collision: [3](#0-2) 

Because `activeRequests` in the confidential relay handler has no such owner-scoping, any unprivileged caller who can predict or learn another user's chosen `req.ID` (e.g. a client-generated UUID/execution ID that may be logged, echoed, or otherwise observable) can submit a request with the identical ID first. The legitimate user's subsequent request with that same ID is rejected with `"request ID already exists"`, and — just as importantly — the attacker can keep the ID "occupied" by never letting quorum/timeout release it in a timely fashion (or by repeating this once the entry is reaped), effectively performing self-inflicted or targeted denial-of-service against the victim's specific request/executionID. This directly parallels the reported pattern: an unprivileged actor manipulates a shared, un-isolated per-request identifier/resource to force failure of someone else's specific operation.

The `TestConfidentialRelayHandler_DuplicateRequestID` test confirms this exact behavior is by design/expected for same-ID resubmission and returns `"request ID already exists"`: [4](#0-3) 

## Impact Explanation
Medium: this does not leak secrets or bypass authentication, but it allows an unprivileged client to deny service to a specific execution/workflow request by squatting its request ID before the legitimate request is fanned out to nodes, causing `newActiveRequest` to reject the real request with an error rather than completing the workflow's relay call. Since `req.ID` drives which in-flight relay operation is tracked and eventually returned to the caller, this can block completion of a specific request in a way structurally analogous to the on-chain refund-revert DoS (attacker action blocks a specific target flow from completing).

## Likelihood Explanation
Medium: exploitation requires the attacker to learn or predict the victim's `req.ID` before the victim's own request lands (a race), and `req.ID` values are often client-chosen (e.g., UUIDs), which somewhat limits guessability. However, if `req.ID` is derived from something predictable/observable (e.g., correlated with execution IDs surfaced elsewhere, as suggested by `requestLogger`'s correlation comments), the race becomes feasible for a determined unprivileged attacker with network access to the gateway's user-facing endpoint.

## Recommendation
Scope `activeRequests` (and equivalent maps in other gateway handlers that don't already do this, e.g. this confidential relay handler) by a composite key of `(sender/owner, req.ID)` rather than `req.ID` alone — mirroring the owner-prefixing approach already implemented in `GatewayVaultRequestProcessor`/`stripPrefixedVaultRequestID`. This prevents one caller's ID choice from colliding with another caller's identically-named but logically distinct request.

## Proof of Concept
1. Attacker learns/predicts a `req.ID` value that a victim intends to use for a `MethodCapabilityExec`/`MethodSecretsGet` relay request (e.g., a deterministic execution ID).
2. Attacker submits a JSON-RPC user message with that `req.ID` to the confidential relay handler first, causing `newActiveRequest` to insert it into `h.activeRequests`.
3. Victim's legitimate request with the same `req.ID` arrives and is rejected via `errors.New("request ID already exists: " + req.ID)`, as reproduced in `TestConfidentialRelayHandler_DuplicateRequestID`.
4. The victim's flow fails to complete for as long as the attacker's entry occupies that key (until timeout/eviction), denying that specific request.

Note: I was unable to fully verify how/whether `req.ID` values are generated or made predictable to external, unprivileged clients in production deployments (e.g., whether IDs are UUIDs chosen client-side vs. derivable from public execution metadata) — this affects the practical guessability/likelihood and would benefit from further review of the calling client code (outside the confidential relay handler package) that constructs these JSON-RPC requests.

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-429)
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
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L67-89)
```go
// ProcessRequest runs validate structure → authorize → prefix ID → stamp params → validate owner-scoped limits.
// In node mode (stripOwnerPrefixForAuth), the envelope ID received from the gateway (owner::id)
// is restored on error so error responses remain matchable by the gateway, which tracks active
// requests by the exact envelope ID it forwarded to the nodes.
func (p *GatewayVaultRequestProcessor) ProcessRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	publicKey *tdh2easy.PublicKey,
) (*AuthorizedGatewayVaultRequest, error) {
	if !p.stripOwnerPrefixForAuth {
		return p.processRequest(ctx, req, publicKey)
	}

	envelopeID := req.ID
	strippedID, _ := stripPrefixedVaultRequestID(req.ID)
	req.ID = strippedID
	authorized, err := p.processRequest(ctx, req, publicKey)
	if err != nil {
		req.ID = envelopeID
		return nil, err
	}
	return authorized, nil
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
