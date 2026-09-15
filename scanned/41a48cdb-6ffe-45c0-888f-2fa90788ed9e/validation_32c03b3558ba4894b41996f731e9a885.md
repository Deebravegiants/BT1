### Title
Vault gateway request replay guard is consumed before the underlying secrets operation succeeds, permanently locking out legitimate retries on downstream failure - ([File: core/capabilities/vault/gateway_vault_request_processor.go])

### Summary
The Vault gateway request pipeline records a request's digest in the `RequestReplayGuard` as "seen" during authorization, **before** the corresponding secrets operation (`CreateSecrets`, `UpdateSecrets`, `DeleteSecrets`) is actually executed against `secretsService`. If that later operation fails for any reason unrelated to the validity of the request itself, the user has no way to resubmit the identical request until the digest naturally expires, because the replay guard will reject it as already-seen.

### Finding Description
`GatewayHandler.HandleGatewayMessage` first calls `h.requestProcessor.ProcessRequest(ctx, req, publicKey)` [1](#0-0) , which internally authorizes the request via `AuthorizeRequest`. That call performs `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` [2](#0-1) , permanently marking the request's digest as consumed for the lifetime of the auth token/expiry window.

Only *after* this consumption does the handler dispatch to the actual state-changing operation, e.g. `h.secretsService.CreateSecrets(ctx, &vaultCapRequest)` [3](#0-2)  or the analogous `UpdateSecrets`/`DeleteSecrets` calls [4](#0-3) . If any of these downstream calls return an error — which is returned to the caller as `api.FatalError` — the request has already been "spent" from the replay guard's perspective.

The `RequestReplayGuard.CheckAndRecord` implementation confirms this ordering: once a digest is recorded it cannot be recorded again until it expires [5](#0-4) , and this is exactly the mechanism exercised by `TestAuthorizer_RejectsJWTReplay`/`TestAuthorizer_RejectsAllowListBasedAuthReplay`, which show a second call with the identical digest is rejected with `ErrRequestAlreadySeen` regardless of what happened with the first call's outcome [6](#0-5) .

This mirrors the reported bug class: a resource/state is "consumed" (assets pulled / digest marked used) prior to confirming that the dependent operation (vault update / secrets write) actually succeeds, so a downstream revert/error leaves the caller stuck rather than free to retry.

### Impact Explanation
A legitimate, authenticated workflow owner whose `CreateSecrets`/`UpdateSecrets`/`DeleteSecrets` call fails transiently (e.g., a storage backend hiccup, a DON-side error, network partition to the secrets store, or any non-malicious failure in `secretsService`) cannot resubmit the exact same request (same `request_id`/digest) until the auth token/JWT authorization window naturally expires. This can strand a user's secret-management operation in a stuck state — unable to complete the create/update/delete they intended, and unable to simply retry with the same parameters, for the remaining lifetime of that authorization's expiry window. This is a legitimate-actor availability/correctness bug reachable directly from an unprivileged, authenticated gateway client request.

### Likelihood Explanation
Likelihood is a function of how often `secretsService.CreateSecrets`/`UpdateSecrets`/`DeleteSecrets` fail after authorization succeeds — any transient storage/backend error, timeout, or partial DON failure on the node side triggers this. Since this is a normal request path (not an attacker-crafted one), any operational hiccup on the secrets backend after auth is sufficient to trigger the stuck state for a legitimate caller.

### Recommendation
Defer replay-guard consumption (or make it revocable/undoable) until after the underlying secrets operation has been confirmed to succeed, or make the replay guard's negative record removable when the downstream call fails with a retryable/non-user error. Concretely, `AuthorizeRequest` (or the caller of `authorizeAndStamp` in `gateway_vault_request_processor.go`) should not treat `CheckAndRecord` as final until the corresponding `secretsService` call in `gw_handler.go` returns success — e.g., by rolling back / releasing the digest entry if `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete` return an `api.FatalError` that is not attributable to the request's own validity.

### Proof of Concept
1. A workflow owner sends a valid `vault.secrets.create` request through the gateway with `request_id = "req-1"`.
2. `GatewayHandler.HandleGatewayMessage` → `requestProcessor.ProcessRequest` → `AuthorizeRequest` succeeds and calls `replayGuard.CheckAndRecord(digest, expiresAt)`, recording `digest` as seen [7](#0-6) .
3. `handleSecretsCreate` then calls `h.secretsService.CreateSecrets(ctx, &vaultCapRequest)`, which returns a transient error (e.g., simulated storage failure) [8](#0-7) ; the handler returns `api.FatalError` to the gateway/user.
4. The user resends the exact same request (`request_id = "req-1"`, same params/auth) hoping to retry.
5. `AuthorizeRequest` recomputes the same digest and `replayGuard.CheckAndRecord` returns `ErrRequestAlreadySeen` [9](#0-8) , so the retry is rejected — the user cannot complete their originally intended, legitimate operation until the digest's expiry window passes.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L194-199)
```go
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
```

**File:** core/capabilities/vault/gw_handler.go (L281-285)
```go
	h.lggr.Debugw("Processing authorized create secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.CreateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
	}
```

**File:** core/capabilities/vault/gw_handler.go (L294-325)
```go
func (h *GatewayHandler) handleSecretsUpdate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.UpdateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized update secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.UpdateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
	}

	jsonResponse, err := toJSONResponse(vaultCapResponse, req.Method)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}
	return jsonResponse
}

func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized delete secrets request", "request", r.String())
	resp, err := h.secretsService.DeleteSecrets(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to delete secrets: %w", err))
	}

	resultBytes, err := resp.ToJSONRPCResult()
```

**File:** core/capabilities/vault/authorizer.go (L99-112)
```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	if authResult == nil {
		err = errors.New("auth mechanism returned nil auth result")
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
		return nil, err
	}
	if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
		a.lggr.Debugw("replay guard rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "", "error", err)
		return nil, err
	}
```

**File:** core/capabilities/vault/request_replay_guard.go (L35-47)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}
```

**File:** core/capabilities/vault/authorizer_test.go (L88-109)
```go
func TestAuthorizer_RejectsJWTReplay(t *testing.T) {
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "1",
		Method: vaulttypes.MethodPublicKeyGet,
		Auth:   "jwt-token",
	}
	digest, err := req.Digest()
	require.NoError(t, err)

	jwtBasedAuth := vaultmocks.NewAuthorizer(t)
	jwtBasedAuth.EXPECT().AuthorizeRequest(mock.Anything, req).Return(vault.NewAuthResult("org-1", "", digest, time.Now().Add(time.Minute).Unix()), nil).Twice()

	a := vault.NewAuthorizer(nil, jwtBasedAuth, logger.TestLogger(t))

	authResult, err := a.AuthorizeRequest(t.Context(), req)
	require.NoError(t, err)
	require.Empty(t, authResult.AuthorizedOwner())

	authResult, err = a.AuthorizeRequest(t.Context(), req)
	require.Nil(t, authResult)
	require.ErrorIs(t, err, vault.ErrRequestAlreadySeen)
}
```
