### Title
Front-running an allowlisted Vault request digest via the public gateway can block a workflow's legitimate secrets request - (File: `core/capabilities/vault/authorizer.go`)

### Summary
The Vault gateway's `AllowListBasedAuth` flow authorizes a JSON-RPC request purely by matching its content digest against an on-chain `WorkflowRegistryOwnerAllowlistedRequest` entry, and the shared `RequestReplayGuard` then permits each digest to be consumed exactly once before its expiry. Because the digest is derived only from public request fields (`method`, `id`, `params`) and the allowlist entry itself is created by a publicly visible on-chain transaction *before* the workflow's off-chain client submits the matching request to the gateway, an unprivileged attacker who observes the on-chain allowlisting event can pre-submit an identical request to the gateway's unauthenticated user endpoint. This consumes the single-use replay-guard slot first, causing the legitimate owner's subsequent (correct) request to be rejected with `ErrRequestAlreadySeen` until the allowlist entry expires.

### Finding Description
The relevant flow:
1. A workflow owner registers a specific request (identified by its digest) as allowlisted on-chain via `WorkflowRegistryOwnerAllowlistedRequest`, giving it an `ExpiryTimestamp`. [1](#0-0) 
2. The gateway's public entrypoint, `handler.HandleJSONRPCUserMessage`, accepts any inbound JSON-RPC request from unauthenticated internet clients and forwards it to the request processor for authorization. [2](#0-1) 
3. `AllowListBasedAuth.AuthorizeRequest` computes `req.Digest()` from the request's public content and checks it against the allowlisted entries; if it matches and is not expired, it is authorized. [3](#0-2) 
4. The generic `authorizer.AuthorizeRequest` then calls `replayGuard.CheckAndRecord(digest, expiresAt)`, which allows the digest to be authorized only once until it expires. [4](#0-3) [5](#0-4) 

The comment in the test file explicitly documents that "replay protection lives in the generic Authorizer," meaning `AllowListBasedAuth` itself does nothing to bind the *first* successful submission to the legitimate owner. [6](#0-5) 

Because:
- the allowlist entry (digest + owner + expiry) is public on-chain data created *before* the off-chain client sends the matching gateway request, and
- the gateway's user-facing endpoint requires no authentication for the allowlist-based flow (`req.Auth == ""` path), and
- the replay guard is a single, global "first submitter wins" cache keyed only by the digest,

any unprivileged party who reads the on-chain allowlisting event can race the legitimate owner's client and submit the identical JSON-RPC request (method/id/params) to the gateway first. The replay guard then records that digest as consumed, and the legitimate owner's genuine request is rejected with `ErrRequestAlreadySeen` for the remaining lifetime of the allowlist entry — this is functionally the same "front-run a permission/entitlement check to block a legitimate actor's follow-up action" pattern described in the report (there, burning an NFT front-ran `accept()`; here, submitting a copycat request front-runs the real owner's `secrets.create/update/delete` gateway call).

### Impact Explanation
This is a denial-of-service on legitimate Vault operations (create/update/delete/list secrets) for any workflow owner whose allowlisted request digest can be observed on-chain before it is redeemed at the gateway. Since secret creation/update calls carry no useful payload benefit for the attacker (the ciphertext is encrypted to the vault's public key), the attacker cannot exfiltrate secrets this way, but they can reliably block the owner's operation until the allowlist entry's `ExpiryTimestamp` passes, forcing the owner to re-register a new allowlisted digest on-chain. Repeated griefing is possible each time the owner tries again with a freshly-allowlisted request.

### Likelihood Explanation
Exploitation requires only:
- Monitoring the public chain for `WorkflowRegistryOwnerAllowlistedRequest` events (no privileged access needed).
- Reconstructing the exact `method`, `id`, and `params` used for the digest (these are often deterministic/predictable for a given workflow's registered request, since the owner must have committed to this exact digest on-chain).
- Sending one HTTP/JSON-RPC request to the gateway's public, unauthenticated endpoint before the legitimate client does.

This is comparable in cost/complexity to the original report's front-running of `burn()`/`accept()` and doesn't require any privileged role, making it a realistic unprivileged-actor DoS vector on the CRE Vault gateway path.

### Recommendation
Bind the replay-guard/authorization success to more than just the request's raw digest — e.g., require that the *first* successful authorization also be tied to a proof of ownership (signature) rather than allowing any anonymous submitter of matching plaintext content to consume the allowlist slot. Alternatively, make the on-chain allowlist entry itself single-use and bound to a specific sender/session, or require the gateway to authenticate the caller (e.g., via signature over the digest) before consulting the replay guard, so a third party cannot race the legitimate owner's first submission.

### Proof of Concept
1. Workflow owner registers an allowlisted request on-chain (`WorkflowRegistryOwnerAllowlistedRequest`) with digest `D` for a `vault.secrets.create` call with fixed `method`/`id`/`params`, expiring in `N` seconds. This transaction and its logs are public.
2. Attacker observes the event, extracts `method`, `id`, `params` needed to reconstruct a request whose `Digest()` equals `D` (these are the values the owner is expected to send verbatim, and are visible or derivable from the on-chain registration data/off-chain workflow metadata).
3. Attacker sends this identical JSON-RPC request (no `Auth` field) directly to the gateway's public HTTP endpoint before the legitimate owner's client does. `AllowListBasedAuth.AuthorizeRequest` matches digest `D`, and `authorizer.replayGuard.CheckAndRecord(D, expiry)` records it as consumed (as demonstrated by the existing duplicate-request test path). [7](#0-6) 
4. When the legitimate owner's client subsequently submits the real request with the same digest, `CheckAndRecord` returns `ErrRequestAlreadySeen`, and the gateway responds with `"request not authorized: request was already authorized previously"`, blocking the owner's operation until the allowlist entry expires.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth_test.go (L166-184)
```go
	// Happy path
	digest, err := allowlistedRequest.Digest()
	require.NoError(t, err)
	digestBytes, err := hex.DecodeString(digest)
	require.NoError(t, err)
	expiry := time.Now().UTC().Unix() + 100
	allowlisted := []workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{
		{
			RequestDigest:   [32]byte(digestBytes),
			Owner:           owner,
			ExpiryTimestamp: uint32(expiry), //nolint:gosec // it is a safe conversion
		},
	}
	mockSyncer.On("GetAllowlistedRequests", mock.Anything).Return(allowlisted)
	authResult, err := auth.AuthorizeRequest(t.Context(), allowlistedRequest)
	require.NoError(t, err)
	require.Equal(t, owner.Hex(), authResult.AuthorizedOwner())
	require.Equal(t, expiry, authResult.ExpiresAt())
	require.NotEmpty(t, authResult.Digest())
```

**File:** core/capabilities/vault/allow_list_based_auth_test.go (L185-189)
```go

	// Same request is still authorized here; replay protection lives in the generic Authorizer.
	authResult, err = auth.AuthorizeRequest(t.Context(), allowlistedRequest)
	require.NoError(t, err)
	require.Equal(t, owner.Hex(), authResult.AuthorizedOwner())
```

**File:** core/services/gateway/handlers/vault/handler.go (L394-427)
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
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-76)
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
	if r.workflowRegistrySyncer == nil {
		r.lggr.Errorw("AllowListBasedAuth workflowRegistrySyncer is nil", "method", req.Method, "requestID", req.ID)
		return nil, errors.New("internal error: workflowRegistrySyncer is nil")
	}
	allowlistedRequest, allowedRequestsStrs, err := r.findAllowlistedItemWithRetry(ctx, req, requestDigest, requestDigestBytes32)
	if err != nil {
		return nil, err
	}
	if allowlistedRequest == nil {
		r.lggr.Debugw("AllowListBasedAuth request digest not allowlisted",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"allowedRequestsStrs", allowedRequestsStrs)
		return nil, errors.New("request not allowlisted")
	}

	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}

	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
```

**File:** core/capabilities/vault/authorizer.go (L99-119)
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
	if ownerErr := validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner()); ownerErr != nil {
		a.lggr.Errorw("owner binding rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "hasAuth", req.Auth != "", "error", ownerErr)
		return nil, ownerErr
	}
	a.lggr.Debugw("request authorized", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "")
	return authResult, nil
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L707-750)
```go
	t.Run("unhappy path - duplicate requestId", func(t *testing.T) {
		h, callback, don, _ := setupHandler(t)
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

		requestID := "1"
		reqData := &vaultcommon.ListSecretIdentifiersRequest{
			RequestId: requestID,
			Owner:     owner,
		}
		reqDataBytes, err := json.Marshal(reqData)
		require.NoError(t, err)

		validJSONRequest := jsonrpc.Request[json.RawMessage]{
			ID:     requestID,
			Method: vaulttypes.MethodSecretsList,
			Params: (*json.RawMessage)(&reqDataBytes),
		}

		responseData := &vaultcommon.ListSecretIdentifiersResponse{
			Identifiers: []*vaultcommon.SecretIdentifier{
				{
					Key:       "foo",
					Owner:     owner,
					Namespace: "default",
				},
			},
		}
		resultBytes, err := json.Marshal(responseData)
		require.NoError(t, err)
		expectedRequestID := owner + vaulttypes.RequestIDSeparator + requestID
		response := jsonrpc.Response[json.RawMessage]{
			ID:     expectedRequestID,
			Result: (*json.RawMessage)(&resultBytes),
			Method: vaulttypes.MethodSecretsList,
		}
		resultBytes, err = json.Marshal(responseData)
		require.NoError(t, err)

		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.NoError(t, err)

		// send duplicate request
		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.ErrorContains(t, err, "request was already authorized previously")
```
