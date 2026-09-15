Found the analog: `HandleJSONRPCUserMessage` in the vault gateway handler registers a request purely by client-supplied `req.ID` in `h.activeRequests` **before** any binding to an authenticated identity, and rejects duplicates unconditionally.

### Title
Unauthenticated request-ID front-running can block legitimate Vault gateway requests - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The Vault gateway handler's `newActiveRequest` keys in-flight requests solely by the caller-supplied JSON-RPC `req.ID` and rejects any second request carrying the same ID with `"request ID already exists"`, mirroring the `AmbireAccount`/`DKIMRecoverySigValidator` pattern where a mapping keyed on an attacker-controllable value (there, `accountAddress`; here, `req.ID`) is claimed by whoever submits first, blocking the legitimate caller's later, correctly-authorized request with the same identifier.

### Finding Description
`HandleJSONRPCUserMessage` validates only that `req.ID` is non-empty and ≤200 chars, then calls `h.requestProcessor.ProcessRequest` for authorization, and only afterwards calls `h.newActiveRequest(req, callback)`, which does: [1](#0-0) 

For `MethodPublicKeyGet`, however, `newActiveRequest` is invoked with no authorization step at all (public-key requests explicitly skip authorization): [2](#0-1) 

This means any unauthenticated caller can submit a `MethodPublicKeyGet`-style request (or any request whose params they merely need to guess) using the exact same `req.ID` value that a legitimate client is about to use, claiming the slot in `h.activeRequests` map first. When the legitimate client's subsequent, properly-authorized request with that same ID arrives, `newActiveRequest` returns `"request ID already exists: " + req.ID"`, and `HandleJSONRPCUserMessage` propagates that as a hard error to the legitimate caller — the request is rejected outright, exactly as `AmbireAccount`'s DKIM recovery reverted with `"recovery already done"` when an attacker front-ran the `recoveries[identifier]` write using the same externally-supplied `accountAddress`/payload.

Similarly, in `core/services/gateway/handlers/confidentialrelay/handler.go`, `HandleJSONRPCUserMessage` rejects duplicate `req.ID` with `"request ID already exists"` before quorum/authorization state is fully settled, per the test: [3](#0-2) 

### Impact Explanation
If request IDs used by legitimate clients are predictable or observable ahead of time (e.g., sequential IDs, UUIDs echoed from other public interactions, or IDs tied to workflow/execution identifiers known to third parties), an unauthenticated or unauthorized party can pre-claim the ID slot and cause the real request to be rejected, denying service to that specific legitimate client call — analogous to the "recovery functionality won't be usable" impact in the original report, but scoped here to gateway request availability rather than fund recovery.

### Likelihood Explanation
Exploitability depends entirely on whether `req.ID` values used by legitimate clients are predictable/guessable by an unprivileged actor; the code itself performs no binding between `req.ID` and the caller's authenticated identity before the ID collision check fires. I could not confirm from the indexed code whether SDK/client-side ID generation is guaranteed to be unpredictable (e.g., cryptographically random) in all call paths, which is necessary to fully assess likelihood.

### Recommendation
Scope the in-flight-request map key to the authenticated identity (e.g., `owner + separator + req.ID`, as already done for node responses via `vaulttypes.RequestIDSeparator` in `sendSuccessResponse`/`errorResponse`) rather than the raw client-supplied `req.ID` alone, and/or perform the duplicate-ID check only after authorization succeeds and bind it to the authorized owner so an unauthenticated request cannot occupy another owner's ID space.

### Proof of Concept
1. Attacker learns/guesses the `req.ID` value ("X") a legitimate client will use for `MethodSecretsList` or similar.
2. Attacker sends `MethodPublicKeyGet` (no auth required) with `ID: "X"` to the gateway; `newActiveRequest` inserts `h.activeRequests["X"]`.
3. Legitimate client sends its authorized request with `ID: "X"`; `newActiveRequest` finds the slot occupied and returns `"request ID already exists: X"`, and `HandleJSONRPCUserMessage` fails the legitimate call. [4](#0-3)

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L394-442)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}

	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

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
