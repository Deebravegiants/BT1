### Title
Unauthenticated request front-running of Vault gateway's single-use replay guard causes denial-of-service to legitimate submitters - ([File: core/capabilities/vault/authorizer.go])

### Summary
The Vault gateway's `AllowListBasedAuth` authorization path grants authorization to *any* caller whose JSON-RPC request content happens to hash to a digest that a workflow owner has posted on-chain — it never verifies that the caller possesses any secret or session tied to that specific submission. Authorization success then permanently consumes a single-use replay slot (`RequestReplayGuard.CheckAndRecord`) and a single-use `activeRequests[req.ID]` map entry. Because nothing binds "who is allowed to submit this exact request" to a specific principal, an unprivileged caller who can obtain or reconstruct the exact request body ahead of the legitimate submitter can front-run it, causing the legitimate submitter's later, identical, otherwise-valid request to be rejected.

### Finding Description
`allowListBasedAuth.AuthorizeRequest` in [1](#0-0)  authorizes a request purely by checking whether the request's content digest matches an entry the workflow owner previously posted on-chain via `AllowlistRequest` (visible to anyone via `GetAllowlistedRequests`, as used in [2](#0-1) ). Unlike the JWT-based path, this path performs **no proof-of-possession check on the caller** — the comment in `authorizer.go` explicitly notes "Requests without req.Auth continue using the allowlist-based path for backwards compatibility" [3](#0-2) .

Once `AuthorizeRequest` succeeds, `authorizer.AuthorizeRequest` immediately calls the single-use `RequestReplayGuard.CheckAndRecord`, which permanently records the digest and rejects any subsequent request with the same digest with `ErrRequestAlreadySeen` ("request was already authorized previously") [4](#0-3) [5](#0-4) . A second, independent single-use guard exists at the internet-facing gateway handler layer: `newActiveRequest` rejects any request whose `req.ID` is already an in-flight key in `activeRequests`, returning "request ID already exists" [6](#0-5) . This exact failure mode ("request was already authorized previously" on a duplicate submission) is demonstrated in the handler's own test suite [7](#0-6) .

`HandleJSONRPCUserMessage` on the vault gateway handler is the internet-facing entry point that accepts requests from any external caller — there is no requirement that the caller be the legitimate workflow/DON node that the owner intended to authorize [8](#0-7) . The root cause parallels the `NFTFilter.verifyLoanValidity()` bug: authorization success (analogous to "signed by the oracle") is checked and a single-use state slot is consumed (analogous to "nonce increment") *before* verifying that the actual intended submitter — not merely "someone who reconstructed matching content" — is the one making the call. Any party able to reconstruct or observe the exact request body that will match a legitimate owner's on-chain-allowlisted digest (e.g. via low-entropy/predictable `RequestId`s, request logging, or intermediary visibility) can pre-consume the replay-guard/`activeRequests` slot ahead of the legitimate submission.

### Impact Explanation
If exploited, a legitimate workflow's Vault request (secrets create/update/delete/list) is rejected outright with "request was already authorized previously" or "request ID already exists," even though the request itself was correctly formed and properly allowlisted on-chain by its rightful owner. This is a genuine denial-of-service against a specific, targeted workflow owner's secret operations, mirroring the impact in the reference report (a legitimate transaction failing because an attacker pre-consumed a single-use protection mechanism).

### Likelihood Explanation
Likelihood depends heavily on how unpredictable/secret the full request content (particularly `RequestId`, which is folded into the digest) is in real deployments, and on whether an external party can ever observe or predict that content before the legitimate submission completes. The AllowList-based auth path is explicitly a "backwards compatibility" fallback lacking any caller-authentication (unlike the JWT path), which is the structural weakness enabling this class of attack; however, I could not fully verify within the available index how `RequestId` values are generated/distributed in production workflows, which affects how easily an outside party could reconstruct a matching request ahead of time. This uncertainty should be resolved with deeper investigation (ideally in a full Devin session with complete repository access) before treating this as a confirmed, immediately-exploitable issue.

### Recommendation
Require that every authorized submission also be bound to a caller-specific credential/session (as already done for the JWT path) rather than allowing authorization to succeed solely because request content matches a public on-chain digest. At minimum, do not let an unauthenticated caller consume the single-use replay-guard/`activeRequests` slot for a request they did not originate; consider requiring `req.Auth` universally, or binding the on-chain allowlist digest check to a request that must be relayed to the gateway by the recognized DON node rather than by any arbitrary internet caller.

### Proof of Concept
Not independently reproduced; the existing test `TestVaultHandler_HandleJSONRPCUserMessage/"unhappy path - duplicate requestId"` [7](#0-6)  demonstrates the mechanics: submitting the same request twice causes the second submission to fail with "request was already authorized previously," confirming the single-use nature of the guard that an unauthenticated first-submitter could exploit against a legitimate second (intended) submitter.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L34-77)
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
}
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1510-1527)
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
	for _, req := range allowedList {
		if req.RequestDigest == reqDigestBytes {
			framework.L.Info().Msgf("Request digest found in allowlist")
		}
		framework.L.Info().Msgf("Allowlisted request digestHexStr: %s, owner: %s, expiry: %d", hex.EncodeToString(req.RequestDigest[:]), req.Owner.Hex(), req.ExpiryTimestamp)
	}
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

**File:** core/capabilities/vault/authorizer.go (L121-128)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
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

**File:** core/services/gateway/handlers/vault/handler.go (L394-434)
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L707-751)
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
