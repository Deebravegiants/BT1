### Title
Global request-ID collision in `ConfidentialRelayHandler` allows unprivileged callers to DoS other users' gateway requests - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
The Confidential Relay gateway handler maintains a single, global `activeRequests` map keyed only by the caller-supplied `req.ID`, with no per-caller/tenant namespacing and no ownership check performed before the ID is used as the map key. Any unprivileged caller who can guess or observe another caller's `req.ID` (e.g. sequential counters, replayed/observed values, or values with low entropy) can pre-register that ID first, causing the legitimate caller's subsequent request to be rejected outright. This mirrors the reported bug class: a predictable, unnamespaced identifier that is externally observable/guessable lets an attacker "squat" on it before the legitimate owner, producing a denial of service for that identifier.

### Finding Description
`HandleJSONRPCUserMessage` accepts a JSON-RPC request from any caller and immediately calls `newActiveRequest`, which checks/records the request purely by the raw `req.ID` string in a handler-wide map shared by all callers/DON members: [1](#0-0) 

```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	...
``` [2](#0-1) 

Unlike the vault gateway path, which stamps and namespaces the ID with the authorized owner *before* using it as a lookup key (`authorizedOwner + RequestIDSeparator + originalRequestID`) via `authorizeAndStamp`: [3](#0-2) 

the confidential relay handler performs no such authorization/namespacing step before the collision check. The test `TestConfidentialRelayHandler_DuplicateRequestID` explicitly documents that a second request with the same raw ID is rejected with "request ID already exists": [4](#0-3) 

Because `req.ID` is attacker-supplied and the collision check happens against a single shared map (not scoped to the caller's identity), any party able to submit a JSON-RPC user message to the gateway can preemptively occupy an ID that another legitimate caller is expected to use, causing that caller's genuine request to fail with an error rather than being routed to the DON.

### Impact Explanation
This is a Denial of Service against a specific in-flight relay request: an unprivileged caller who predicts or observes another caller's `req.ID` can block that particular request from being processed by the confidential relay DON, forcing a request failure (`"request ID already exists"`) instead of legitimate execution. Repeated for freshly retried IDs, this can degrade availability of the confidential relay path for a targeted caller. There is no evidence of fund theft or cross-user data leakage since the map only gates admission, and `addResponseForNode`/response routing is separately keyed per DON node — so this analog only supports the DoS half of the reported bug class, not the "steal deposit" half.

### Likelihood Explanation
Exploitability depends on how unpredictable caller-chosen `req.ID`s are in practice (e.g., UUIDs would make blind guessing infeasible, but any caller who can observe pending traffic, or callers using low-entropy/sequential IDs, remain vulnerable). No authentication or per-caller scoping is applied prior to the map lookup in this handler, so the front-running primitive itself is present in the code regardless of ID entropy assumptions.

### Recommendation
Namespace the `activeRequests` key by the authenticated/authorized caller identity (similar to the vault gateway's owner-prefixed ID scheme in `authorizeAndStamp`) before performing the existence check, so that ID collisions can only occur within a single caller's own request stream rather than globally across all gateway clients.

### Proof of Concept
1. Caller A prepares to send a confidential relay JSON-RPC request with `ID = "req-123"`.
2. Attacker observes/guesses this ID (e.g., via low-entropy IDs, timing, or side channel) and sends `HandleJSONRPCUserMessage` with the same `ID = "req-123"` first.
3. `newActiveRequest` succeeds for the attacker's request, inserting `"req-123"` into `h.activeRequests`.
4. Caller A's legitimate request with the same ID arrives and `newActiveRequest` returns `errors.New("request ID already exists: req-123")`, as demonstrated by `TestConfidentialRelayHandler_DuplicateRequestID` [4](#0-3) , denying Caller A service for that request.

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-293)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}

	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}

	p.lggr.Debugw("authorized gateway vault request", "method", req.Method, "requestID", req.ID, "owner", authorizedOwner, "orgID", authResult.OrgID(), "workflowOwner", authResult.WorkflowOwner())
	return &AuthorizedGatewayVaultRequest{
		Req:        *req,
		AuthResult: authResult,
	}, nil
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
