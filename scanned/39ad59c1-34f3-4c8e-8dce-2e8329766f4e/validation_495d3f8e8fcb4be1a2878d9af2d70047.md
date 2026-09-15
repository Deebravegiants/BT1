This is exactly the analog of the reported bug class: an unprivileged request can consume a one-time authorization credential (nonce/digest) that legitimately belongs to another user's specific request, causing a griefing/DoS impact against the legitimate user.

### Title
Unprivileged caller can pre-consume another workflow owner's allowlisted request digest via `AllowListBasedAuth`, permanently blocking that legitimate request - (File: core/capabilities/vault/allow_list_based_auth.go)

### Summary
The Vault gateway's `allowListBasedAuth.AuthorizeRequest` (`core/capabilities/vault/allow_list_based_auth.go`, lines 34-77) computes a digest purely from the *content* of an incoming `jsonrpc.Request`, matches it against an on-chain allowlist entry (`fetchAllowlistedItem`), and, if found and unexpired, hands back an `AuthResult` whose `Digest()` is then unconditionally recorded as "seen" by `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/authorizer.go` (lines 99-119, specifically line 109). Because this whole flow is reachable by any unauthenticated caller sending a raw JSON-RPC message to the gateway (no signature, no ownership binding at this stage — that's identical to Sherlock's `CrabNetting.checkOrder(Order)` which required no `msg.sender == order.trader` check), any actor who can reconstruct or guess the exact request body/ID that a legitimate workflow owner intends to send (a value that is public on-chain, since it is registered via `AllowlistRequest` on the `WorkflowRegistry` contract, see `deployment/cre/workflow_registry/v2/changeset/user_workflow_registry_test.go` `allowlistRequest`) can submit it first through `HandleJSONRPCUserMessage` (`core/services/gateway/handlers/vault/handler.go` lines 394-434). This consumes the one-time replay-guard slot for that digest before the real owner's request arrives.

### Finding Description
The bug-class match to the report is: "everyone can check/consume an order/state item that does not belong to them, and doing so mutates shared state (nonce/digest) that should only be spendable by the legitimate owner."

- `RequestReplayGuard.CheckAndRecord` (`core/capabilities/vault/request_replay_guard.go` lines 35-47) is a global map keyed only by `digest`; the first caller to present a request whose computed digest matches an on-chain allowlisted digest "wins" the slot, exactly like `_useNonce` in the Sherlock report which lets anyone burn a nonce belonging to another trader.
- The allowlist digest itself (`WorkflowRegistryOwnerAllowlistedRequest.RequestDigest`) is set via an on-chain, publicly-readable `AllowlistRequest` call (see `allowlistRequest` helper in `deployment/cre/workflow_registry/v2/changeset/user_workflow_registry_test.go` lines 881-911) and the digest is a public, non-secret hash of request contents (`req.Digest()`), not a value requiring possession of a private key or session token in the allowlist path (`req.Auth == ""` branch, `authorizer.go` line 124-126).
- `HandleJSONRPCUserMessage` in `core/services/gateway/handlers/vault/handler.go` is the internet-facing gateway entrypoint for unprivileged clients and passes the raw request straight to `requestProcessor.ProcessRequest` → `authorizeAndStamp` → `AuthorizeRequest` (`core/capabilities/vault/gateway_vault_request_processor.go` lines 260-293) with no requirement that the caller is the workflow owner referenced by the allowlist entry.
- The only protection preventing impersonation of the *result* (secret ownership) is `validateSecretOwnersMatchAuthorized` (`authorizer.go` lines 148-197), which runs **after** the replay guard has already recorded the digest as consumed (line 109 executes before line 113). So even if the attacker's crafted request is subsequently rejected for owner mismatch on `EncryptedSecrets`/`Ids`/`Owner` fields, the digest slot has already been permanently marked "seen," so the real owner's legitimate subsequent submission of that exact allowlisted request will be rejected by `ErrRequestAlreadySeen`.

### Impact Explanation
This is a request-impersonation / quota-bypass style denial of service: a third party who observes or predicts an on-chain allowlisted request digest (which is intentionally public, since `AllowlistRequest` is an on-chain transaction) can front-run the legitimate owner and permanently burn that authorization before the intended user submits their genuine, signed/allowlisted Vault operation (e.g., `secrets.create`, `secrets.delete`). The victim's authorized, time-boxed one-shot secret operation becomes unusable, and because allowlist entries are single-use by digest with no re-allowlisting self-service path abstracted here, this can block secret management operations for the affected workflow owner until a new allowlist entry with a new nonce/digest is registered on-chain (an MCMS/timelock-governed action based on `UserAllowlistRequest` changesets).

### Likelihood Explanation
Likelihood is constrained by the fact that the attacker must know/derive the exact JSON-RPC request body corresponding to the allowlisted digest (the digest is a hash over request content, not merely an ID) before the legitimate owner submits it, and the allowlisted digest and expiry are visible on-chain via `WorkflowRegistry.OwnerAllowlistedRequest` events/state, which are the pieces the report's "anyone can call checkOrder for someone else's order" class depends on (the order is also intended to be known/prepared off-chain by any observer). Given that allowlist entries are typically prepared and often broadcast/relayed by tooling before submission, and the digest computation is deterministic from public parameters, this is plausibly reachable by an unprivileged network client.

### Recommendation
Bind the replay-guard consumption to the request's already-authorized `workflowOwner`/original submitter, or defer `CheckAndRecord` until *after* `validateSecretOwnersMatchAuthorized` succeeds and the caller has been confirmed to be an authorized party for that specific `Owner`. At minimum, do not treat digest allowlisting alone as authorization to consume the nonce — require that the caller's derived `AuthorizedOwner()` matches the request's actual secret owner fields (as already done later) before calling `replayGuard.CheckAndRecord`, so an unrelated caller cannot pre-empt another owner's allowlisted digest.

### Proof of Concept
1. Workflow owner `O` registers an allowlisted request on-chain via `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)` for a `secrets.create` payload they intend to submit later (`deployment/cre/workflow_registry/v2/changeset/user_workflow_registry_test.go`, `allowlistRequest` helper).
2. Attacker `A` reads the on-chain `WorkflowRegistryOwnerAllowlistedRequest` entries (public state/events) and reconstructs the exact `jsonrpc.Request[json.RawMessage]` body whose `req.Digest()` equals `requestDigest` (the digest depends only on request content, per `req.Digest()` used in `allow_list_based_auth.go` line 36).
3. `A` submits this crafted request to the gateway's `HandleJSONRPCUserMessage` before `O` does. `allowListBasedAuth.AuthorizeRequest` finds the matching allowlisted entry and returns a valid `AuthResult`; `authorizer.AuthorizeRequest` then calls `replayGuard.CheckAndRecord(digest, expiresAt)` (line 109), which succeeds and marks the digest consumed.
4. Only afterwards does `validateSecretOwnersMatchAuthorized` potentially reject `A`'s request due to owner mismatch on the secrets payload — but the digest is already burned.
5. When `O` submits their genuine matching request, `AuthorizeRequest` → `replayGuard.CheckAndRecord` returns `ErrRequestAlreadySeen` (`core/capabilities/vault/request_replay_guard.go` line 42), and `O`'s legitimate, allowlisted operation is permanently denied (confirmed by the existing test `"unhappy path - duplicate requestId"` in `core/services/gateway/handlers/vault/handler_test.go` lines 707-750, which demonstrates that a duplicate presentation of the same digest is rejected regardless of who submits it first). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** deployment/cre/workflow_registry/v2/changeset/user_workflow_registry_test.go (L881-911)
```go

```
