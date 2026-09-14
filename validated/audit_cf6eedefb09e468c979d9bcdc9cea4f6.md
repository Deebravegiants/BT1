### Title
Unauthenticated, attacker-controlled `request.ID` collision enables denial-of-service on in-flight confidential-relay requests - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The gateway's confidential-relay handler deduplicates in-flight requests using only the client-supplied JSON-RPC `req.ID` as the map key, with no authentication, no owner binding, and no tie to the request's actual content (`workflow_id`/`execution_id`). Any unprivileged caller who can submit (or predict/observe) the same `ID` as another in-flight request can register it first and cause the legitimate request to be rejected with `"request ID already exists"`, denying that specific execution — the same root-cause pattern as the reported `_deduplicateOrder` bug, where a replay-guard key is derived from attacker-controllable values that are not bound to the actual value/owner of the operation being protected.

### Finding Description
`handler.HandleJSONRPCUserMessage` in the confidential-relay gateway handler performs no authorization at all before registering the request: [1](#0-0) 

Request registration/dedup is implemented in `newActiveRequest`, keyed purely on `req.ID`: [2](#0-1) 

This is confirmed by the existing test, which shows that a second submission with the same `ID` — regardless of differing content — is unconditionally rejected: [3](#0-2) 

Contrast this with the sibling `vault` gateway handler, which requires the request to pass through `GatewayVaultRequestProcessor.ProcessRequest` (authorization + owner-prefixing of the ID) before it ever reaches `newActiveRequest`: [4](#0-3) [5](#0-4) 

In the vault handler, the dedup key is `owner + separator + requestID`, so an attacker cannot collide with another owner's request without already being authorized as that owner (the digest/allowlist check gates this). The confidential-relay handler has no such gate — the raw, caller-supplied `ID` is trusted as-is and used directly as the dedup/routing key for the entire request lifecycle (`activeRequests`, `HandleNodeMessage` routing by `resp.ID`, and eventual response delivery).

### Impact Explanation
Because the dedup key is not bound to any authenticated identity or to the semantic content of the request (e.g., `workflow_id`/`execution_id`), an attacker who can guess, predict, or otherwise learn a victim's `request.ID` in advance of the victim's submission can pre-register that ID, causing the victim's genuine request to be rejected outright (`newActiveRequest` returns an error, and `HandleJSONRPCUserMessage` propagates it without ever calling `don.SendToNode`). This is a targeted denial-of-service against a specific confidential-relay operation — directly analogous to the reported LevelMinting `_deduplicateOrder` DoS, where a low-value/attacker-chosen but colliding key blocks a legitimate high-value operation from ever executing.

### Likelihood Explanation
The attack requires the attacker to know or predict the target's `request.ID` before submitting to the gateway. If callers use unpredictable identifiers (e.g., random UUIDs, as most in-repo callers do), this is hard to exploit blind. However, nothing in the handler enforces ID unpredictability or binds the ID to caller identity — any external, unauthenticated caller of this gateway handler can attempt collisions, and any deployment/integration that uses sequential, predictable, or otherwise observable request IDs is immediately exploitable. The structural weakness (no auth, no owner binding, pure client-supplied key) is the same root cause the external report flags, even though real-world exploitability depends on the ID generation scheme used by callers.

### Recommendation
Bind the in-flight request dedup key to something the caller cannot forge/predict on behalf of another party — e.g., derive the key from a hash of the full request digest (method + params + ID) similar to `RequestReplayGuard`/`req.Digest()` used elsewhere in the vault capability, or require the same authorization/owner-prefixing step the vault gateway handler already performs before calling `newActiveRequest`. At minimum, do not let an unauthenticated caller's raw `ID` alone gate whether another party's request can proceed.

### Proof of Concept
The existing unit test already demonstrates the exact primitive an attacker would use: [3](#0-2) 
1. Attacker learns/predicts the victim's intended `request.ID` (e.g., `"req-dup"`).
2. Attacker submits a `HandleJSONRPCUserMessage` call with that `ID` first (no authentication required by this handler).
3. When the victim's legitimate request with the same `ID` arrives, `newActiveRequest` returns `"request ID already exists: req-dup"`, and the victim's request is never forwarded to the relay DON — a targeted DoS.

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

**File:** core/services/gateway/handlers/vault/handler.go (L426-441)
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L457-472)
```go
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
