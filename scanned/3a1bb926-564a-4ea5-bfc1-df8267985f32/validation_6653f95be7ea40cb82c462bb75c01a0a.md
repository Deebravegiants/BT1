Confirmed key finding: the confidentialrelay gateway handler's `HandleJSONRPCUserMessage` in `core/services/gateway/handlers/confidentialrelay/handler.go` performs no authentication/authorization check before claiming a globally-shared `req.ID` key in `h.activeRequests`. Any caller reaching this gateway service can pre-claim a request ID before the legitimate owner submits it, causing a persistent denial of that ID for the remainder of its TTL — an analog of the "lock in a value/claim for a window, blocking legitimate updates" pattern from the oracle report. The HTTP trigger handler's `setupCallback` in `capabilities/v2/http_trigger_handler.go` has the same request-ID map shape, but it is guarded by `authorizeRequest` (JWT ownership check) before `setupCallback`, so squatting there requires already being authorized for a workflow — much weaker/likely intended. The confidentialrelay path, by contrast, claims the ID before any authorization/attestation check (attestation is validated later at `core/capabilities/confidentialrelay/handler.go handleCapabilityExecute`, which runs on the DON member node, not at the gateway's initial dispatch).

### Title
Unauthenticated Request-ID Squatting Causes Denial of Service on Confidential Relay Requests - (`core/services/gateway/handlers/confidentialrelay/handler.go`)

### Summary
`handler.HandleJSONRPCUserMessage` accepts a caller-supplied `req.ID` and stores it as the sole key into a global `activeRequests` map without any prior authentication, authorization, or per-caller/per-workflow scoping. Because the ID is globally unique across all callers and workflows, and a duplicate ID is rejected outright, an attacker can pre-claim (front-run) any request ID it expects a legitimate caller to use next, denying that caller's subsequent legitimate submission for the lifetime of the pending/active request (bounded by `requestTimeout`/cleanup, similar in spirit to the "locked for the epoch" behavior in the reported oracle bug).

### Finding Description
`HandleJSONRPCUserMessage` only validates that `req.ID` is non-empty and ≤200 characters, then calls `newActiveRequest`: [1](#0-0) 

`newActiveRequest` locks a global map keyed purely by the attacker-controlled `req.ID` and rejects any second registration under that same ID, regardless of which caller or workflow it belongs to: [2](#0-1) 

There is no check tying `req.ID` ownership to a workflow, owner, or any prior authentication step at this layer — labels like `workflow_id`/`execution_id` are extracted only for logging and are not verified: [3](#0-2) 

This mirrors the root cause pattern in the oracle report: a shared, update-once state keyed by an attacker-influenceable value (`epoch` there, `req.ID` here) that — once claimed by an unprivileged actor — blocks the legitimate actor from taking effect until the claim naturally expires. The test suite explicitly documents the reject-on-duplicate behavior: [4](#0-3) 

By contrast, the analogous `capabilities/v2` HTTP trigger handler performs `authorizeRequest` (JWT-based workflow ownership check) *before* claiming the request ID in `setupCallback`, meaning only an already-authorized caller for that workflow can attempt ID squatting there: [5](#0-4) [6](#0-5) 

### Impact Explanation
Any unauthenticated/unprivileged party who can send a JSON-RPC message to the gateway's confidential-relay service (`MethodSecretsGet`, `MethodCapabilityExec`) can deny a specific victim's request from ever being processed by pre-registering the same `req.ID` first. Since request IDs are often deterministic or predictable within a workflow/execution lifecycle (e.g., derived from execution ID or a retry sequence known to the enclave/relay retry loop, per the comments about "the enclave's retry loop"), this is a plausible targeted denial-of-service against specific workflow executions relying on the confidential relay (secrets retrieval / capability execution), potentially stalling secret-dependent capability executions until timeout.

### Likelihood Explanation
Reaching this code path requires only the ability to submit a JSON-RPC user message to the gateway that gets routed to the confidentialrelay handler — `gateway.ProcessRequest` dispatches based on service name/DON ID with no authentication gate visible before `HandleJSONRPCUserMessage` is invoked. No signature, JWT, or attestation is verified before the ID claim occurs. The main uncertainty is exactly how request IDs are chosen/exposed to a would-be attacker in production deployments (predictability of IDs is not fully verified from the indexed code); this affects exploitability but not the underlying missing-authorization root cause.

### Recommendation
Scope `activeRequests` keys by an authenticated/attested identity (e.g., a combination that includes a verified caller/DON/workflow identity) rather than the raw client-supplied `req.ID` alone, or require authentication/attestation before the ID is claimed in `newActiveRequest`, mirroring the `authorizeRequest`-before-`setupCallback` ordering already used in the HTTP trigger handler.

### Proof of Concept
Not independently reproduced against a live gateway; based on `TestConfidentialRelayHandler_DuplicateRequestID`, which demonstrates that a second `HandleJSONRPCUserMessage` call with a previously-registered `req.ID` is rejected with `"request ID already exists"` regardless of caller identity: [4](#0-3) 

An attacker simply needs to submit a request with the target's `req.ID` first (no auth token required at this layer) to trigger this rejection for the legitimate submitter.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L80-108)
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
func (h *handler) extractRequestLabels(req jsonrpc.Request[json.RawMessage]) requestLabels {
	var labels requestLabels
	if req.Params == nil {
		return labels
	}
	if err := json.Unmarshal(*req.Params, &labels); err != nil {
		h.lggr.Debugw("could not decode relay request params for logging labels",
			"method", req.Method, "requestID", req.ID, "err", err)
	}
	return labels
}
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-144)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}

	strippedWorkflowID := strings.TrimPrefix(workflowID, "0x")
	legacyExecutionID, err := workflows.EncodeExecutionID(strippedWorkflowID, req.ID) //nolint:staticcheck // legacy ID kept for observability comparison
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID: " + err.Error())
	}
	// Workflows shouldn't use more than one HTTP trigger. If we ever need to support multiple triggers, we'd need to pass
	// trigger index to the Gateway handler and somehow allow senders to pick. For now, we use trigger index 0.
	// Execution IDs here are used only for logging.
	executionIDWithTriggerIndex, err := workflows.GenerateExecutionIDWithTriggerIndex(strippedWorkflowID, req.ID, 0)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID with trigger index: " + err.Error())
	}
	h.lggr.Debugw("processing request",
		"legacyExecutionID", legacyExecutionID,
		"executionIDWithTriggerIndex", executionIDWithTriggerIndex,
		"requestID", req.ID,
		"workflowID", workflowID)

	reqWithKey, err := reqWithAuthorizedKey(triggerReq, *key)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error marshaling trigger request: " + err.Error())
	}

	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-426)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
```
