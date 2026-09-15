### Title
Vault `AllowListBasedAuth` authorizes any request whose *content digest* matches a publicly on‑chain‑registered value, with no signature/possession check — allowing an unprivileged actor to front‑run and permanently deny a legitimate owner's Vault request - ([File: core/capabilities/vault/allow_list_based_auth.go])

### Summary
`AllowListBasedAuth.AuthorizeRequest` authorizes a Vault JSON‑RPC request purely by checking whether the request's content-hash ("digest") matches an entry that was previously registered on-chain via `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)`. There is no signature over the request body from the caller, no possession proof, and no binding to the actual sender — the digest and the associated `Owner` come solely from public on-chain state. [1](#0-0) [2](#0-1) 

### Finding Description
The `WorkflowRegistry.AllowlistRequest(requestDigest, expiryTimestamp)` call is a normal on-chain transaction, so the `(digest, owner, expiry)` tuple it registers is/becomes public information (visible pending in mempool, and permanently readable afterward via `GetActiveAllowlistedRequestsReverse`). [3](#0-2) [4](#0-3) 

`allowListBasedAuth.AuthorizeRequest` only recomputes the digest of the *incoming* request and looks it up against this on-chain-sourced list; if it matches, the request is authorized as belonging to `allowlistedRequest.Owner` — regardless of who actually sent the HTTP/JSON-RPC request to the gateway: [5](#0-4) 

Authorization results then feed into a single-use `RequestReplayGuard` keyed only by the digest, so the *first* request bearing a matching digest that reaches the DON consumes the on-chain-approved slot for good (until `ExpiryTimestamp`): [6](#0-5) [7](#0-6) 

This is directly analogous to the reported `permit2`/`_afterAllocate` bug class: in the original report, a front-runner replays a *captured, still-valid, single-use authorization* (the `permit2` signature) ahead of the legitimate holder, causing the real transaction to permanently fail due to replay protection while the intended state update never happens. Here, the "single-use authorization" is the on-chain-registered `requestDigest`, and — critically — unlike a `permit2` signature, this digest is not bound to a specific sender at all; there is no signature check tying the JSON-RPC caller to the workflow owner. Anyone who can reconstruct (or predict/guess) the exact JSON-RPC request body that hashes to the publicly-known allowlisted digest can submit it to the Vault gateway. Whichever request (attacker's forged copy or the legitimate workflow's real submission) arrives first at `RequestReplayGuard.CheckAndRecord` wins; the other is rejected with `ErrRequestAlreadySeen` and can never be authorized again for that digest until the on-chain `ExpiryTimestamp` elapses. [8](#0-7) 

For predictable request shapes (e.g. `vault.secrets.list`/`vault.secrets.delete` where the owner address is public and namespace/key values follow conventional naming), an attacker does not need to see any secret to reconstruct the exact byte content that hashes to the observed on-chain digest — unlike the original permit2 case, they don't even need mempool visibility of the actual gateway HTTP request; the trigger (the on-chain `AllowlistRequest` transaction) is itself public and durable state, not an ephemeral mempool artifact.

### Impact Explanation
If an attacker wins the race, the legitimate workflow owner's authorized Vault operation (secrets create/update/delete/list, public key retrieval) can never be executed for that pre-approved digest, causing a denial of service on that operation until the on-chain allowlist entry expires (`ExpiryTimestamp`), and if the attacker's forged request is a different operation, they could effectively impersonate the owner and cause `secretsService` to execute state changes credited to that owner (subject to the additional `validateSecretOwnersMatchAuthorized` check, which validates owner fields embedded in params, not authenticity of the sender). This satisfies "request impersonation" / "unauthorized job run" categories: the DON treats an attacker-submitted request as authorized on behalf of another party purely because its content hash matches public on-chain data.

### Likelihood Explanation
Exploitability depends on the attacker being able to reconstruct the exact request bytes that hash to the known digest. This is trivial for the many methods whose parameters are largely deterministic/public (owner address, namespace, key naming, `vault.secrets.list`), moderate for others requiring the plaintext of `EncryptedSecrets`/`request_id`. Likelihood is therefore method-dependent, but the underlying control gap — authorization requires no signature over the request body — makes the class real for any request whose content is fully guessable from public data.

### Recommendation
`AllowListBasedAuth` should not treat digest match alone as proof of sender identity. Bind allowlisted-request authorization to a signature from the workflow owner over the request (similar to the `JWTBasedAuth` path, which does verify a signed token whose claims are cryptographically tied to the digest and owner), or require the caller to additionally prove possession of the owner's key when submitting a request that matches an on-chain digest. At minimum, the replay guard's first-writer-wins behavior for `AllowListBasedAuth`-authorized digests should not be exploitable by parties other than the actual key holder.

### Proof of Concept
1. Workflow owner calls `WorkflowRegistry.AllowlistRequest(digest, expiry)` on-chain for a `vault.secrets.list` request with `{owner: <public address>, namespace: "main"}`. [9](#0-8) 
2. An attacker observes this transaction (pending or confirmed) and reconstructs the exact JSON-RPC body (`owner` is public, `namespace` is a conventional value), computing the same digest.
3. Attacker submits this JSON-RPC request to the Vault gateway before the legitimate owner's client does.
4. `allowListBasedAuth.AuthorizeRequest` finds the digest allowlisted and returns an `AuthResult` for `Owner`; `authorizer.AuthorizeRequest` calls `replayGuard.CheckAndRecord(digest, expiry)` which succeeds for the attacker's request. [10](#0-9) 
5. When the legitimate owner's real request subsequently arrives with the identical digest, `CheckAndRecord` returns `ErrRequestAlreadySeen`, and the owner's operation is rejected for the lifetime of the allowlist entry, exactly mirroring the "digest consumed, real party locked out" pattern in the reported `permit2` issue. [8](#0-7) 

**Note on confidence**: I could not fully trace the exact network-facing entry point (`core/services/gateway/handlers/vault/handler.go`'s `HandleJSONRPCUserMessage`) to confirm whether any additional per-connection/mTLS/session authentication is enforced before a request reaches `AllowListBasedAuth.AuthorizeRequest` — the tool budget was exhausted before I could read that file in full. If the gateway enforces sender-bound authentication upstream of the authorizer (e.g., only accepting requests already tied to a specific workflow's signed transport), this finding's likelihood would be substantially reduced. I recommend a Devin session with full file access to verify the exact gateway ingress path and any upstream authentication before treating this as confirmed-exploitable.

### Citations

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-77)
```go
// AuthorizeRequest authorizes a request using AllowListBasedAuth.
// It does NOT check if the request method is allowed.
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

**File:** core/services/workflows/syncer/v2/workflow_registry.go (L1302-1308)
```go
		for _, request := range response.AllowlistedRequests {
			newAllowlistedRequests = append(newAllowlistedRequests, workflow_registry_wrapper_v2.WorkflowRegistryOwnerAllowlistedRequest{
				RequestDigest:   request.RequestDigest,
				Owner:           request.Owner,
				ExpiryTimestamp: request.ExpiryTimestamp,
			})
		}
```

**File:** deployment/cre/workflow_registry/v2/changeset/operations/contracts/user_workflow_registry_ops.go (L360-375)
```go
var UserAllowlistRequestOp = operations.NewOperation(
	"user-allowlist-request-op",
	semver.MustParse("1.0.0"),
	"User Allowlist Request in WorkflowRegistry V2",
	func(b operations.Bundle, deps WorkflowRegistryOpDeps, input UserAllowlistRequestOpInput) (UserAllowlistRequestOpOutput, error) {
		// Execute the transaction using the strategy
		operation, _, err := deps.Strategy.Apply(func(opts *bind.TransactOpts) (*types.Transaction, error) {
			tx, err := deps.Registry.AllowlistRequest(opts, input.RequestDigest, input.ExpiryTimestamp)
			if err != nil {
				return nil, fmt.Errorf("failed to call AllowlistRequest: %w", err)
			}
			return tx, nil
		})
		if err != nil {
			return UserAllowlistRequestOpOutput{}, fmt.Errorf("failed to execute AllowlistRequest: %w", err)
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

**File:** core/capabilities/vault/authorizer_test.go (L111-128)
```go
func TestAuthorizer_RejectsAllowListBasedAuthReplay(t *testing.T) {
	allowListBasedAuth := vaultmocks.NewAuthorizer(t)
	// Use a method without secret identifiers so the owner-binding check is a no-op.
	req := jsonrpc.Request[json.RawMessage]{ID: "1", Method: vaulttypes.MethodPublicKeyGet}
	allowListBasedAuth.EXPECT().AuthorizeRequest(mock.Anything, req).Return(vault.NewAuthResult("", "0xabc", "digest-1", time.Now().Add(time.Minute).Unix()), nil).Twice()

	a := vault.NewAuthorizer(allowListBasedAuth, nil, logger.TestLogger(t))

	authResult, err := a.AuthorizeRequest(t.Context(), req)
	require.NoError(t, err)
	require.Empty(t, authResult.OrgID())
	require.Equal(t, "0xabc", authResult.WorkflowOwner())
	require.Equal(t, "0xabc", authResult.AuthorizedOwner())

	authResult, err = a.AuthorizeRequest(t.Context(), req)
	require.Nil(t, authResult)
	require.ErrorIs(t, err, vault.ErrRequestAlreadySeen)
}
```

**File:** system-tests/lib/cre/workflow/secrets.go (L199-211)
```go
	var reqDigestBytes [32]byte
	copy(reqDigestBytes[:], requestDigestBytes)

	wfReg, err := workflow_registry_v2_wrapper.NewWorkflowRegistry(workflowRegistryAddress, sethClient.Client)
	if err != nil {
		return errors.Wrap(err, "failed to instantiate workflow registry v2 wrapper")
	}

	expiry := uint32(time.Now().Add(time.Hour).Unix()) //nolint:gosec // G115: timestamp fits uint32 until year 2106
	_, decErr := sethClient.Decode(wfReg.AllowlistRequest(sethClient.NewTXOpts(), reqDigestBytes, expiry))
	if decErr != nil {
		return errors.Wrap(decErr, "failed to allowlist vault request in workflow registry")
	}
```
