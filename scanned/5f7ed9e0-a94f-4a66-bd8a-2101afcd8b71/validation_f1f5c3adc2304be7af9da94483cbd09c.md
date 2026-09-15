### Title
Unauthenticated request-ID collision causes cross-caller griefing/DoS in `ConfidentialRelayHandler` - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
The gateway's confidential-relay handler registers a caller-supplied JSON-RPC request ID into a shared, un-namespaced map (`activeRequests`) with **no authentication or authorization step and no per-caller/per-owner prefixing** before the ID is used as the sole collision key. Any request whose ID is already active is rejected outright. This is the same root cause as the reported `createAccount` bug: a value fully controlled by the caller and reused as a unique identifier is not validated/scoped, so a second, unrelated party can "front-run" the ID and cause the legitimate request to fail.

### Finding Description
`HandleJSONRPCUserMessage` validates only that `req.ID` is non-empty and ≤200 chars, then immediately calls `h.newActiveRequest(req, labels, callback)`: [1](#0-0) 

`newActiveRequest` uses the raw, attacker-controlled `req.ID` as the map key with no ownership prefix, no signature/auth check, and no scoping to the caller: [2](#0-1) 

If an entry for that ID already exists, the call fails immediately with `"request ID already exists: " + req.ID`, confirmed by the handler's own test: [3](#0-2) 

This is structurally identical to the report's `createAccount` bug class: a user-supplied identifier (`accountId` in the report, `req.ID` here) is used unchanged as a global uniqueness key with no validation that it is bound to the caller's identity (e.g., hashed with owner/workflow/execution identity), and no authentication gate exists before the ID is "claimed." Compare this to the sibling `vault` handler, which defends against exactly this by requiring `AuthorizeRequest` to succeed and then rewriting the ID to `authorizedOwner + separator + originalID` via `GatewayVaultRequestProcessor.authorizeAndStamp` *before* it is ever inserted into `activeRequests`: [4](#0-3) [5](#0-4) 

The confidential-relay handler has no such authorization/prefixing step in its own logic — `newActiveRequest` is called directly on the raw, unauthenticated request. Because `req.ID` in this protocol correlates to workflow execution retries (see the comment "The request id changes per enclave retry; the execution identity does not"), and the workflow/execution identifiers are visible in the request's own params (`extractRequestLabels`), an unprivileged party observing or guessing an in-flight request's ID (e.g., from telemetry, logs, or by racing predictable/short IDs) can submit a colliding request first and cause the legitimate caller's real request to be rejected before ever reaching the DON — exactly mirroring the report's "attacker copies accountId from the pending tx and front-runs createAccount" pattern, where the legitimate user's transaction fails and gas/relay-slot resources are wasted.

### Impact Explanation
This maps to unbounded/griefing impact classes explicitly in scope:
- **Griefing with no profit motive**: any unauthenticated caller reaching `HandleJSONRPCUserMessage` (the gateway's internet-facing user-message entrypoint) can deny a specific legitimate request by reserving its ID first, causing that caller's real workflow-relay request to fail immediately with an error rather than being forwarded to the DON.
- **Unbounded resource claim**: because there's no per-caller/per-owner namespace on the ID, a single malicious actor can also pre-register many arbitrary or predictable IDs to broadly deny future requests before the requester ever calls in, without incurring meaningful cost (the check happens purely in-process, before any DON fan-out or rate-limit consumption tied to the victim).
- Distinct from a routine duplicate-request UX safeguard because there is no verification that the second submitter is the same principal as the first — the "duplicate" check doubles as an unauthenticated claim-check on someone else's identifier.

### Likelihood Explanation
High for anyone who can reach the gateway's confidential relay method endpoint and either predict or observe a pending request ID (e.g., via logs/telemetry that include `requestID`, or by racing a small ID space) before the legitimate call is registered. No credentials, allowlist membership, or node compromise is required — this is purely an unprivileged internet-facing gateway interaction, consistent with the required threat model (no operator/node/peer compromise needed).

### Recommendation
Do not use the raw caller-supplied `req.ID` as the sole global uniqueness/ownership key. Apply the same pattern already used by the vault handler:
1. Authenticate/authorize the request before registering it in `activeRequests`.
2. Derive the map key by combining the authenticated caller/owner identity with the caller-supplied ID (e.g., `ownerOrWorkflowID + separator + req.ID`), so collisions can only occur within the same authenticated principal's own namespace.
3. Strip the prefix again before returning the response to preserve JSON-RPC ID echo semantics, exactly as `sendSuccessResponse`/`errorResponse` do in the vault handler.

### Proof of Concept
Conceptual PoC (analogous to the report's front-run of `createAccount`):
1. Attacker observes or predicts the JSON-RPC `id` a legitimate workflow execution will use for `MethodCapabilityExec`/`MethodSecretsGet` (e.g., derived from a workflow/execution ID visible in logs or telemetry).
2. Attacker sends their own `HandleJSONRPCUserMessage` request with that same `id` value first — no authentication is required to reach this call.
3. `newActiveRequest` registers the ID under the attacker's request.
4. When the legitimate caller's request with the same `id` arrives, `newActiveRequest` returns `"request ID already exists: <id>"` and the real request is dropped, exactly as demonstrated by the existing unit test `TestConfidentialRelayHandler_DuplicateRequestID`: [3](#0-2) 

This test already proves the mechanism; the missing piece exploited by an attacker is that step 2 requires no authorization and no binding of the ID to the caller, unlike the vault handler's owner-prefixed equivalent.

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-292)
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L426-472)
```go
	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
	}

	switch req.Method {
	case vaulttypes.MethodSecretsCreate:
		return h.handleSecretsCreate(ctx, ar)
	case vaulttypes.MethodSecretsUpdate:
		return h.handleSecretsUpdate(ctx, ar)
	case vaulttypes.MethodSecretsDelete:
		return h.handleSecretsDelete(ctx, ar)
	case vaulttypes.MethodSecretsList:
		return h.handleSecretsList(ctx, ar)
	default:
		return h.sendResponse(ctx, ar, h.errorResponse(req, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method), nil))
	}
}

func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```
