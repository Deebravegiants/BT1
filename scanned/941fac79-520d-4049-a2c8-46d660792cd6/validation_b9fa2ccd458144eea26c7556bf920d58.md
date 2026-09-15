Confirmed: `HandleJSONRPCUserMessage` in the confidential relay gateway handler registers the request into `activeRequests` keyed by the raw, client-supplied, unauthenticated `req.ID`, before any authorization/authentication of the caller takes place. This mirrors the reported bug class — an attacker "front-running" with a cheap/attacker-controlled input to poison shared state keyed by a value the victim also controls, causing the victim's legitimate request to fail.

### Title
Unauthenticated request-ID collision allows front-running griefing of legitimate relay requests - (File: `core/services/gateway/handlers/confidentialrelay/handler.go`)

### Summary
`HandleJSONRPCUserMessage` accepts a JSON-RPC request from any HTTP client and immediately calls `newActiveRequest`, which keys the in-memory `activeRequests` map solely by the caller-supplied `req.ID` string [1](#0-0) . This lookup/insert happens before any authentication, JWT check, or workflow-owner verification runs for this method — there is no `AuthorizeRequest`/allowlist call in this path, unlike the vault handler's pipeline. Any unauthenticated caller who learns or guesses a victim's about-to-be-used request ID can submit it first and cause the victim's real request to be rejected.

### Finding Description
`newActiveRequest` performs a simple existence check and insert under a mutex: [2](#0-1) 
If `h.activeRequests[req.ID] != nil`, the function returns `"request ID already exists: " + req.ID"` and `HandleJSONRPCUserMessage` propagates that error, aborting the legitimate caller's request entirely [3](#0-2) . Crucially, this check occurs strictly before any authorization: the only pre-checks in `HandleJSONRPCUserMessage` are ID emptiness and length [4](#0-3) . This is confirmed by the test `TestConfidentialRelayHandler_DuplicateRequestID`, which shows two unauthenticated-looking requests with the same ID racing for the same map slot and the second one failing outright [5](#0-4) .

This is directly analogous to the reported `LockedStakingPools.participate` bug: in both cases, a shared piece of state (a map keyed by a user-influenced/user-supplied identifier) is written by an unprivileged/unauthenticated actor first, and a later, legitimate caller's write is rejected because the check-then-act guard (`if position.amount != 0` / `if h.activeRequests[req.ID] != nil`) sees the attacker's entry already occupying that slot.

The comment in `requestLabels`/`extractRequestLabels` states params are "not otherwise interpreted" and are only used for logging, confirming the gateway performs no authentication of the caller for `MethodCapabilityExec`/`MethodSecretsGet` at this layer [6](#0-5) . Contrast this with the vault handler, where `newActiveRequest` is only reached after `requestProcessor.ProcessRequest` authorizes the caller and rewrites `req.ID` into an owner-prefixed ID (`authorizedOwner + separator + originalRequestID`), so collisions there are scoped to the same authenticated owner [7](#0-6) . The confidential relay handler has no equivalent owner-prefixing/authorization step before the map write.

### Impact Explanation
An unauthenticated network client can deny service to a legitimate workflow execution's relay/capability request by submitting a request with the same `req.ID` first. Because request IDs for this flow are workflow/execution-derived and may be predictable or observable (e.g., reused across enclave retries, as referenced in `TestHandler_RetryWhileInFlightWaits`'s reasoning about retries hitting "the remote request server's duplicate-requester check"), an attacker can grief a specific victim's request, causing it to error out with "request ID already exists" rather than being serviced by the relay DON. This can disrupt confidential relay / capability execution results, a high-value internet-facing gateway path, without any privileged access.

### Likelihood Explanation
Likelihood is high given that:
- The gateway HTTP endpoint accepting user JSON-RPC requests is internet-facing (`ProcessRequest` in `core/services/gateway/gateway.go`), so any client can send crafted `req.ID` values.
- No authentication gate exists before the collision check for this handler.
- The only requirement is knowledge or prediction of the target `req.ID`, which is feasible if IDs are derived from workflow/execution identifiers that are not secret.

### Recommendation
Namespace `activeRequests` by an authenticated identity (e.g., the caller's verified owner/workflow identity, similar to the vault pipeline's `authorizedOwner + separator + requestID` stamping) rather than the raw client-supplied ID, and/or require successful authorization before performing the existence check/insert into shared state. This prevents an unauthenticated caller from occupying another party's request-ID slot.

### Proof of Concept
1. Attacker observes/predicts a victim's forthcoming request ID (e.g., `wf-1/executionID/uuid`-style IDs referenced in test helpers).
2. Attacker sends a `MethodCapabilityExec`/`MethodSecretsGet` JSON-RPC request to the gateway's public HTTP endpoint with `ID` set to that value and arbitrary/garbage params, before the victim's real request arrives.
3. `newActiveRequest` succeeds and inserts the attacker's entry into `h.activeRequests[req.ID]` [2](#0-1) .
4. When the victim's legitimate request with the same ID arrives, `newActiveRequest` returns `"request ID already exists: " + req.ID"`, and `HandleJSONRPCUserMessage` returns this error immediately, denying the victim's request without ever reaching the relay DON [3](#0-2) , matching the behavior demonstrated in `TestConfidentialRelayHandler_DuplicateRequestID` [5](#0-4) .

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L80-97)
```go
// requestLabels are the identifiers the gateway pulls out of a relay request's
// params purely for logging, so a gateway line can be correlated with the
// relay-DON's and the enclave's lines for the same workflow execution. The
// gateway stays a dumb relay: it does not otherwise interpret params.
type requestLabels struct {
	WorkflowID  string `json:"workflow_id"`
	ExecutionID string `json:"execution_id"`
}

// extractRequestLabels best-effort decodes the logging identifiers from a
// request's params. Both relay methods' params carry these fields. A decode
// failure leaves them empty and is only logged: these labels are for
// correlation, and the params themselves are validated by the relay nodes,
// not here, so a request whose params do not decode is still fanned out and
// rejected there. ProcessRequest has already parsed the envelope as valid
// JSON by this point, so a failure here means params is not an object or
// carries non-string identifiers — malformed input rather than a gateway bug,
// hence debug level to avoid handing a caller a log-spam lever.
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-412)
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
}
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L278-286)
```go
	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}
```
