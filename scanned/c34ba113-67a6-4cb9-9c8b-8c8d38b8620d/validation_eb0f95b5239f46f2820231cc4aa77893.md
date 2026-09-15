### Title
Unauthenticated request-ID squatting causes griefing DoS in Confidential Relay gateway handler - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The `confidentialrelay` gateway handler accepts a client-chosen `req.ID` (JSON-RPC request ID) and uses it as a global, unscoped map key to track in-flight requests, with no authentication or per-owner namespacing performed before the ID is claimed. Any actor able to reach the gateway's public JSON-RPC ingress for this handler can pre-register (front-run) an arbitrary request ID, causing a legitimate caller's subsequent request with the same ID to be rejected outright — the same "user-chosen unique ID, first writer wins, transaction reverts for the real user" pattern described in the external report for `AccountManager.createAccount`.

### Finding Description
`HandleJSONRPCUserMessage` in `core/services/gateway/handlers/confidentialrelay/handler.go` (lines 394-412) performs only trivial format checks on `req.ID` (non-empty, ≤200 chars) and then immediately calls `h.newActiveRequest(req, labels, callback)`: [1](#0-0) 

`newActiveRequest` registers the request under the raw, unscoped `req.ID` in the handler-wide `h.activeRequests` map, and rejects the call outright if that ID is already present: [2](#0-1) 

Critically, unlike the sibling `vault` gateway handler — which authorizes/binds the request via `h.requestProcessor.ProcessRequest` and then re-keys the in-flight map entry to `owner + RequestIDSeparator + requestID` before checking for collisions (`core/services/gateway/handlers/vault/handler.go:394-441`) — the `confidentialrelay` handler performs **no authorization or per-caller namespacing at all**. The code comment at line 93 explicitly documents this as intentional: "the gateway stays a dumb relay: it does not otherwise interpret params." Because the map key is the bare client-supplied string, any caller reaching this handler can claim any ID before the intended requester's message arrives.

This mirrors the reported vulnerability class precisely: a user-selectable identifier is used as a global uniqueness key with "first submission wins, second submission reverts/errors" semantics, and no ownership binding prevents an unrelated actor from claiming another user's chosen ID first.

### Impact Explanation
An attacker who can observe or predict a legitimate confidential-relay request ID (e.g., an execution/workflow ID that is deterministic, retried, or reused — the handler's own comments note "the request id changes per enclave retry; the execution identity does not," implying some IDs are foreseeable) can submit a decoy request with that ID first. The legitimate request is then rejected with `"request ID already exists"` (line 419) and the corresponding `jsonrpc.ErrConflict` is returned to the real caller's callback, causing that workflow execution's confidential-relay action to fail. Repeating this griefing is low-cost for the attacker and requires no privileged access, no funds, and no profit motive — a direct, no-signature-required DoS against a specific workflow/enclave interaction, analogous in mechanism and severity class to the reported account-creation front-running griefing.

### Likelihood Explanation
Likelihood is contingent on: (1) whether the gateway's public HTTP/WS ingress permits any external client to reach `HandleJSONRPCUserMessage` for the `MethodSecretsGet`/`MethodCapabilityExec` methods without prior allowlisting at a layer above this handler, and (2) whether request IDs used by legitimate nodes/workflows are predictable or reusable by an outside party. I was not able to fully confirm within the available tool budget whether an upstream allowlist/auth layer (e.g., in `core/services/gateway/gateway.go` or `multihandler.go`) filters callers before dispatch to this specific handler — the grep results show `HandleJSONRPCUserMessage` is invoked generically by `multihandler.go` without visible per-handler authorization gating in the code reviewed. This is a material gap in my analysis: if an allowlist step upstream restricts callers to only the legitimate request originator, the practical exploitability is reduced to same-caller races rather than cross-user griefing. I could not verify this due to iteration limits.

### Recommendation
1. Bind the in-flight request key to an authenticated identity (as the `vault` handler already does via `owner + RequestIDSeparator + requestID`), not the bare client-supplied `req.ID`, so unrelated callers cannot collide with each other's IDs.
2. Add an authorization/authentication step to `HandleJSONRPCUserMessage` in `confidentialrelay/handler.go` prior to `newActiveRequest`, consistent with the vault handler's `requestProcessor.ProcessRequest` pattern, rather than treating the relay purely as a "dumb relay."
3. Alternatively, generate/derive the in-flight tracking key server-side (e.g., hash of authenticated sender + client ID) instead of trusting the raw client-supplied string as a global uniqueness key.

### Proof of Concept
Given the existing test `TestConfidentialRelayHandler_DuplicateRequestID` (`core/services/gateway/handlers/confidentialrelay/handler_test.go:863-881`), which shows that any second caller using the same `req.ID` value is rejected with `"request ID already exists"` regardless of caller identity: [3](#0-2) 
An attacker script would:
1. Predict/observe a target `req.ID` (e.g., tied to a workflow execution retry) for method `MethodCapabilityExec`.
2. Submit a `HandleJSONRPCUserMessage` request with that exact `ID` before the legitimate caller does.
3. The legitimate caller's subsequent identical-ID request is rejected with `"request ID already exists"`, denying that user's relay action — reproducing the "front-run and grief" pattern from the external report, but here at the gateway ingress layer rather than in a smart contract.

### Citations

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
