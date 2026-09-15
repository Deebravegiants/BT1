## Analog Vulnerability Found

### Title
Unauthenticated request replay of allowlisted Vault requests permits front-run denial-of-service and response hijacking - (File: `core/capabilities/vault/allow_list_based_auth.go`)

### Summary
The Vault gateway's `AllowListBasedAuth` path authorizes a JSON-RPC request purely by recomputing a digest over the request's public `method`/`ID`/`params` fields and checking that digest against an on-chain allowlist, with **no signature or secret binding the caller to the request**. Because the allowlisting transaction and its digest are public, and the deterministic digest can be reconstructed by anyone who observes the request content, an unprivileged actor can replay the exact same request through the gateway before the legitimate owner does. The single-use, in-memory `RequestReplayGuard` then marks that digest "seen," permanently rejecting the real owner's subsequent submission — the same front-running/nonce-consumption DoS pattern described in the external report (attacker observes a pending, permit-gated action and race-consumes it, causing the legitimate transaction to revert).

### Finding Description
`allowListBasedAuth.AuthorizeRequest` computes `req.Digest()` from the request's method, ID, and params [1](#0-0) , and treats a match against the on-chain `GetAllowlistedRequests()` result as sufficient authorization — there is no signature check, and this path is explicitly used "for backwards compatibility" whenever `req.Auth == ""` [2](#0-1) .

The allowlisting itself happens via a public on-chain call `wfRegistryContract.AllowlistRequest(...)` that records the `requestDigest` and expiry [3](#0-2) . Since Ethereum transactions are visible before/при mining (mempool) and the digest/params are derivable from public on-chain or gateway-observable data, an attacker can reconstruct byte-identical JSON-RPC request content (method + ID + params) for a not-yet-submitted, allowlisted request.

Once the attacker submits this replicated request to the gateway first:
1. `allowListBasedAuth.AuthorizeRequest` succeeds, returning an `AuthResult` bound to the **real owner's address** (since the digest matches the on-chain entry authorized for that owner) [4](#0-3) .
2. The generic `authorizer.AuthorizeRequest` then calls `a.replayGuard.CheckAndRecord(authResult.Digest(), ...)`, which records the digest as "seen" globally, in memory, keyed only by digest [5](#0-4) ; [6](#0-5) .
3. `validateSecretOwnersMatchAuthorized` passes because the attacker used the exact original params, which already match the authorized owner [7](#0-6) .
4. The gateway then **executes the operation** (`SecretsCreate`/`Update`/`Delete`/`List`) as if it came from the owner, and returns the response over the attacker's own gateway connection [8](#0-7) .
5. When the legitimate owner subsequently submits their real request with the same digest, `CheckAndRecord` returns `ErrRequestAlreadySeen`, permanently rejecting the intended action for the remainder of the allowlist expiry window [9](#0-8) .

This is the same root-cause pattern as the reported issue: a permission/authorization decision is bound to a publicly observable, deterministic value (there: a Permit2 order/nonce; here: a request digest over public request content) with no signer-specific binding, so any unprivileged party who can reproduce that value can consume it first.

### Impact Explanation
- **Denial of service**: an attacker can front-run any allowlisted Vault request and irreversibly consume its single-use replay slot, blocking the legitimate owner's `SecretsCreate`/`Update`/`Delete`/`List` operation until the on-chain allowlist entry expires and is re-allowlisted.
- **Cross-user response confusion / unauthorized execution**: because the attacker's replayed request is authorized as the real owner (owner comes from the on-chain allowlist entry, not from anything the attacker controls), the side effect (e.g., a `SecretsList` response containing secret identifiers, or a `SecretsCreate`/`Update` mutation) is executed and its response delivered to the attacker's gateway connection instead of the legitimate owner's — this is a concrete case of request impersonation / cross-user response confusion in the internet-facing gateway.
- This only applies to the legacy no-`req.Auth` (allowlist-based) path; the JWT-based path (`req.Auth != ""`) binds the digest to a signed OAuth token and is not affected the same way.

### Likelihood Explanation
Likelihood is high for any deployment still relying on the backwards-compatible allowlist-only path: the attacker needs no privileged credentials, only the ability to (a) observe or reconstruct the exact request content matching a soon-to-be-submitted allowlisted digest (via the on-chain `AllowlistRequest` transaction/mempool, or via any other visibility into the request), and (b) send it to the gateway before the legitimate client. No signature, secret, or session token is required to exploit this path.

### Recommendation
- Deprecate/remove the auth-less allowlist-based path (`authorizeAllowListBasedAuth`) or require it to also validate a caller-specific credential (e.g., signature over the digest) in addition to the on-chain allowlist entry, so that being able to reproduce the digest is not sufficient to be authorized.
- Bind replay-guard consumption to the authenticated caller identity (not just the digest) so a third party cannot consume another party's allowlisted slot.
- Consider making allowlist consumption idempotent to the legitimate signer only, e.g., require the request to be submitted from the same session/connection or signed by a key controlled by the allowlisted owner.

### Proof of Concept
1. Owner submits `wfRegistryContract.AllowlistRequest(digest, expiry)` on-chain for a `vault.secrets.list` request with `method="vault.secrets.list"`, `id="req-1"`, `params={"namespace":"main","owner":"0xOwner"}`.
2. Attacker observes this on-chain call (or otherwise learns the exact method/ID/params) before the owner submits the corresponding request to the Gateway, and reconstructs the identical JSON-RPC request bytes.
3. Attacker sends this exact JSON-RPC request (with `Auth=""`) to the Gateway first.
   - `allowListBasedAuth.AuthorizeRequest` finds the digest allowlisted for `0xOwner` and returns `AuthResult{workflowOwner: "0xOwner", digest: ..., expiresAt: ...}` [4](#0-3) .
   - `replayGuard.CheckAndRecord(digest, expiresAt)` succeeds and marks the digest "seen" [6](#0-5) .
   - The `SecretsList` request executes and the response (list of secret identifiers for `0xOwner`) is sent back to the attacker's gateway connection [10](#0-9) .
4. Owner subsequently submits the same request; `CheckAndRecord` now returns `ErrRequestAlreadySeen`, and the owner's legitimate request is rejected [11](#0-10) .

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-46)
```go
func (r *allowListBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	r.lggr.Debugw("AllowListBasedAuth authorizing request", "method", req.Method, "requestID", req.ID)
	requestDigest, err := req.Digest()
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to create digest", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to decode digest", "method", req.Method, "requestID", req.ID, "requestDigest", requestDigest, "error", err)
		return nil, err
	}
	requestDigestBytes32 := [32]byte(requestDigestBytes)
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L70-76)
```go
	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
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

**File:** core/capabilities/vault/authorizer.go (L121-127)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
```

**File:** core/capabilities/vault/authorizer.go (L148-163)
```go
// validateSecretOwnersMatchAuthorized checks that secret identifiers in the request payload
// match the authorized workflow owner. This is read-only validation; owner prefixing and
// param stamping happen later in GatewayVaultRequestProcessor.
func validateSecretOwnersMatchAuthorized(req jsonrpc.Request[json.RawMessage], workflowOwner string) error {
	switch req.Method {
	case vaulttypes.MethodPublicKeyGet:
		return nil
	case vaulttypes.MethodSecretsCreate:
		if req.Params == nil {
			return errors.New("request params must not be nil")
		}
		var createReq vaultcommon.CreateSecretsRequest
		if err := json.Unmarshal(*req.Params, &createReq); err != nil {
			return err
		}
		return validateEncryptedSecretOwnerMismatch(createReq.EncryptedSecrets, workflowOwner)
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1510-1521)
```go
func allowlistRequest(t *testing.T, owner string, request jsonrpc.Request[json.RawMessage], sethClient *seth.Client, wfRegistryContract *workflow_registry_v2_wrapper.WorkflowRegistry) {
	requestDigest, err := request.Digest()
	require.NoError(t, err, "failed to get digest for request")
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	require.NoError(t, err, "failed to decode digest")
	reqDigestBytes := [32]byte(requestDigestBytes)
	_, err = wfRegistryContract.AllowlistRequest(sethClient.NewTXOpts(), reqDigestBytes, uint32(time.Now().Add(1*time.Hour).Unix())) //nolint:gosec // disable G115
	require.NoError(t, err, "failed to allowlist request")

	framework.L.Info().Msgf("Allowlisting request digest at contract %s, for owner: %s, digestHexStr: %s", wfRegistryContract.Address().Hex(), owner, requestDigest)
	allowedList, err := wfRegistryContract.GetAllowlistedRequests(&bind.CallOpts{}, big.NewInt(0), big.NewInt(100))
	require.NoError(t, err, "failed to validate allowlisted request")
```

**File:** core/capabilities/vault/request_replay_guard.go (L9-9)
```go
var ErrRequestAlreadySeen = errors.New("request was already authorized previously")
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

**File:** core/capabilities/vault/gw_handler.go (L180-224)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}

	if response == nil {
		switch req.Method {
		case vaulttypes.MethodSecretsCreate:
			response = h.handleSecretsCreate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsUpdate:
			response = h.handleSecretsUpdate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsDelete:
			response = h.handleSecretsDelete(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsList:
			response = h.handleSecretsList(ctx, gatewayID, req, authResult)
		}
	}
```
