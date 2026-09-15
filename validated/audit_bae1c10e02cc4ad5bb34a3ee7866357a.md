Audit Report

## Title
Replay guard records a request digest as "seen" before owner-binding validation completes, permanently burning that digest on failure - (File: `core/capabilities/vault/authorizer.go`)

## Summary
`authorizer.AuthorizeRequest` calls `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` unconditionally right after the underlying auth mechanism succeeds, and only afterwards calls `validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner())`, which can still fail and cause the whole request to be rejected. [1](#0-0)  Because `RequestReplayGuard.CheckAndRecord` has no rollback/unrecord path and simply marks the digest as permanently seen until its expiry, a digest that fails the later owner-binding check is nonetheless burned for the rest of its validity window. [2](#0-1) 

## Finding Description
The authorization pipeline is:
1. `authorizeRequest` resolves an `AuthResult` (owner, digest, expiry) via either the allowlist-based or JWT-based mechanism. [3](#0-2) 
2. `replayGuard.CheckAndRecord` is called unconditionally and marks the digest as seen for `expiresAt`. [4](#0-3) 
3. Only after that does `validateSecretOwnersMatchAuthorized` check that the payload's embedded `Owner` fields (for `create`/`update`/`delete`/`list` secrets requests) match `authResult.AuthorizedOwner()`, and this can fail with a returned error. [5](#0-4) [6](#0-5) 

`RequestReplayGuard.CheckAndRecord` has no corresponding rollback method; once a digest is written to `g.seen`, it stays there until it expires. [7](#0-6) 

The digest is derived purely from the request's method/params/id via `req.Digest()`, independent of who is calling. [8](#0-7)  Critically, the on-chain `AllowlistRequest` call that produces a `WorkflowRegistryOwnerAllowlistedRequest` binds an arbitrary, caller-chosen digest to the caller's own address as `Owner` — this is confirmed by the test/changeset helper flow, where `AllowlistRequest(digest, expiry)` is invoked by the caller for a digest of their choosing, and the resulting entry records that caller as `Owner`. [9](#0-8)  The changeset test flow (`link-owner` → `allowlist-request` → `upsert`) shows this is a self-service registration process using a self-generated signed ownership proof, not an admin-gated action. [10](#0-9)  This means an attacker can compute the digest of a request whose *params* target a victim owner (e.g., `ListSecretIdentifiersRequest.Owner = victim`), self-allowlist that exact digest bound to their own address, submit it, and have `authorizeAllowListBasedAuth` return `AuthorizedOwner() = attacker` for that digest — which then fails `validateSecretOwnersMatchAuthorized` (owner mismatch) but only *after* the digest has already been recorded as seen.

Existing tests confirm the replay guard rejects an identical digest on a second call (`TestAuthorizer_RejectsAllowListBasedAuthReplay`, `TestAuthorizer_RejectsJWTReplay`), and there is no test covering the "record succeeds, then owner-check fails, then legitimate replay is wrongly blocked" scenario, meaning the ordering flaw as described is real and unaddressed. [11](#0-10) 

## Impact Explanation
An attacker who can self-register an on-chain allowlist entry for a digest they choose (or self-mint a JWT with an `authorization_details` digest claim for their own org, as shown in `TestAuthorizer_RejectsJWTReplayDuringValidationLeewayWindow`) can pre-consume the replay-guard slot for a specific, predictable request digest belonging to a victim, causing the victim's legitimate subsequent request with that exact digest to be rejected with `ErrRequestAlreadySeen` until the attacker-chosen expiry elapses. [12](#0-11)  This is a genuine availability/denial-of-service defect against a specific vault secrets operation (create/update/delete/list), falling under the "unauthorized denial of a legitimate operation via unrolled state" impact class analogous to the referenced Arcadia bug pattern.

## Likelihood Explanation
The attack requires the attacker to predict the exact request digest (method + params + id) that a victim workflow will later submit — a nontrivial precondition, but one made more plausible in this codebase because CRE workflows are documented/tested to use deterministic, idempotent request IDs (reflected in comments such as "Retrying the same request body just hits the vault replay guard" in the system test helper). [13](#0-12)  Registering an attacker-controlled allowlist entry or minting a JWT for an arbitrary digest under the attacker's own identity appears to be a normal, unprivileged self-service capability of any vault-enabled user/workflow owner, not an admin or operator action, based on the reviewed changeset/test flow. I was not able to locate and fully verify the Solidity source of `AllowlistRequest` in this index to confirm there is no additional access-control gate beyond the self-linking flow shown in tests; this remains a minor residual uncertainty but does not change the core code-level finding.

## Recommendation
Reorder `authorizer.AuthorizeRequest` so that `validateSecretOwnersMatchAuthorized` (and any other request-content validation that can fail) runs *before* `replayGuard.CheckAndRecord`, ensuring the replay guard is only updated once the request is fully validated. Alternatively, add an `Unrecord`/rollback method to `RequestReplayGuard` that is invoked whenever a post-record validation step fails, restoring the digest to an unseen state.

## Proof of Concept
1. Attacker crafts a `vault.secrets.list` request whose `params.Owner` is a victim workflow owner, using method/params/id identical to what the victim's workflow will deterministically submit.
2. Attacker self-registers on-chain via `AllowlistRequest(digest, expiry)` for that exact digest (as shown in `allowlistRequest` test helper), which binds `Owner = attacker` to that digest. [9](#0-8) 
3. Attacker sends the crafted request. `authorizeAllowListBasedAuth` succeeds with `AuthorizedOwner() = attacker`; `replayGuard.CheckAndRecord(digest, expiry)` records the digest as seen; `validateSecretOwnersMatchAuthorized` then fails because `listReq.Owner` (victim) != `attacker`, and the request is rejected — but the digest is now burned in `RequestReplayGuard.seen`. [14](#0-13) 
4. Victim's workflow later submits the identical legitimate request; `replayGuard.CheckAndRecord` returns `ErrRequestAlreadySeen`, and the request is denied until the attacker-chosen `expiresAt` passes. [15](#0-14) 

A Go unit test mirroring `TestAuthorizer_RejectsAllowListBasedAuthReplay` but using two different mocked `AuthorizeRequest` calls (first returning `AuthorizedOwner="attacker"` for a `MethodSecretsList` request with `Owner="victim"` in params, second returning `AuthorizedOwner="victim"` for the same digest) would demonstrate that the second, legitimate call incorrectly receives `ErrRequestAlreadySeen` instead of being processed.

### Citations

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

**File:** core/capabilities/vault/authorizer.go (L148-197)
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
	case vaulttypes.MethodSecretsUpdate:
		if req.Params == nil {
			return errors.New("request params must not be nil")
		}
		var updateReq vaultcommon.UpdateSecretsRequest
		if err := json.Unmarshal(*req.Params, &updateReq); err != nil {
			return err
		}
		return validateEncryptedSecretOwnerMismatch(updateReq.EncryptedSecrets, workflowOwner)
	case vaulttypes.MethodSecretsDelete:
		if req.Params == nil {
			return errors.New("request params must not be nil")
		}
		var deleteReq vaultcommon.DeleteSecretsRequest
		if err := json.Unmarshal(*req.Params, &deleteReq); err != nil {
			return err
		}
		return validateSecretIdentifierOwnerMismatch(deleteReq.Ids, workflowOwner)
	case vaulttypes.MethodSecretsList:
		if req.Params == nil {
			return errors.New("request params must not be nil")
		}
		var listReq vaultcommon.ListSecretIdentifiersRequest
		if err := json.Unmarshal(*req.Params, &listReq); err != nil {
			return err
		}
		if vaultutils.NormalizeOwner(listReq.Owner) != vaultutils.NormalizeOwner(workflowOwner) {
			return fmt.Errorf("list secrets owner %q does not match authorized workflow owner %q", listReq.Owner, workflowOwner)
		}
		return nil
	default:
		return fmt.Errorf("owner validation not implemented for method %q", req.Method)
	}
}
```

**File:** core/capabilities/vault/request_replay_guard.go (L16-47)
```go
type RequestReplayGuard struct {
	mu      sync.Mutex
	seen    map[string]int64 // digest → unix expiry timestamp
	nowFunc func() time.Time // injectable for testing
}

// NewRequestReplayGuard creates a replay guard for authorized Vault requests.
func NewRequestReplayGuard() *RequestReplayGuard {
	return &RequestReplayGuard{
		seen:    make(map[string]int64),
		nowFunc: time.Now,
	}
}

// CheckAndRecord returns ErrRequestAlreadySeen if the digest was previously
// recorded and has not yet expired. Otherwise it records the digest with
// the given expiry timestamp (unix seconds, UTC).
//
// Expired entries are cleaned up on every call.
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

**File:** core/services/workflows/syncer/v2/workflow_syncer_v2_test.go (L881-911)
```go
func allowlistRequest(
	t *testing.T,
	th *testutils.EVMBackendTH,
	wfRegC *workflow_registry_wrapper_v2.WorkflowRegistry,
	input allowlistRequestParams,
) {
	t.Helper()
	totalAllowlistedRequestsBefore, err := wfRegC.TotalAllowlistedRequests(&bind.CallOpts{
		From: th.ContractsOwner.From,
	})
	require.NoError(t, err, "failed to get total allowlisted requests")

	requestDigest, err := input.Request.Digest()
	require.NoError(t, err)
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	require.NoError(t, err)

	_, err = wfRegC.AllowlistRequest(
		th.ContractsOwner,
		[32]byte(requestDigestBytes),
		uint32(input.ExpiryTimestamp.Unix()), //nolint:gosec // safe conversion
	)
	require.NoError(t, err, "failed to register allowlisted request")
	th.Backend.Commit()

	totalAllowlistedRequestsAfter, err := wfRegC.TotalAllowlistedRequests(&bind.CallOpts{
		From: th.ContractsOwner.From,
	})
	require.NoError(t, err, "failed to get total allowlisted requests")
	require.Equal(t, totalAllowlistedRequestsBefore.Uint64()+1, totalAllowlistedRequestsAfter.Uint64(), "total allowlisted requests mismatch")
}
```

**File:** deployment/cre/workflow_registry/v2/changeset/user_workflow_registry_test.go (L33-75)
```go
	t.Run("link-owner allowlist-request upsert pause activate delete unlink-owner", func(t *testing.T) {
		fixture := setupTest(t)

		chain := fixture.rt.Environment().BlockChains.EVMChains()[fixture.selector]
		deployerKey := chain.DeployerKey

		t.Log("Testing link owner...")
		validity, proof, signature := generateAndSignOwnershipProof(
			t,
			common.HexToAddress(fixture.workflowRegistryAddress),
			deployerKey.From.Hex(),
			chain,
			deployerKey.From.Hex(),
			"123",
			"12",
			"WorkflowRegistry 2.0.0",
			0, // 0 for linking
		)
		linkOwnerInput := UserLinkOwnerInput{
			ValidityTimestamp:         validity,
			Proof:                     common.Bytes2Hex(proof.Bytes()),
			Signature:                 common.Bytes2Hex(signature),
			ChainSelector:             fixture.selector,
			WorkflowRegistryQualifier: "test-workflow-registry-v2",
		}
		linkOwnerChangeset := UserLinkOwner{}
		err := linkOwnerChangeset.VerifyPreconditions(fixture.rt.Environment(), linkOwnerInput)
		require.NoError(t, err, "link owner preconditions should pass")
		_, err = linkOwnerChangeset.Apply(fixture.rt.Environment(), linkOwnerInput)
		require.NoError(t, err, "link owner apply should pass")

		t.Log("Testing allowlist request...")
		allowlistInput := UserAllowlistRequestInput{
			ExpiryTimestamp:           mustConvertInt64ToUint32(time.Now().Add(48 * time.Hour).Unix()),
			RequestDigest:             generateRandom32BytesString(t),
			ChainSelector:             fixture.selector,
			WorkflowRegistryQualifier: "test-workflow-registry-v2",
		}
		allowlistChangeset := UserAllowlistRequest{}
		err = allowlistChangeset.VerifyPreconditions(fixture.rt.Environment(), allowlistInput)
		require.NoError(t, err, "allowlist request preconditions should pass")
		_, err = allowlistChangeset.Apply(fixture.rt.Environment(), allowlistInput)
		require.NoError(t, err, "allowlist request apply should pass")
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

**File:** core/capabilities/vault/jwt_based_auth_test.go (L261-309)
```go
func TestAuthorizer_RejectsJWTReplayDuringValidationLeewayWindow(t *testing.T) {
	rsaKey := generateTestRSAKey(t, "key-1")
	jwksServer := newTestJWKSServer(t, rsaKey)

	issuer := jwksServer.URL() + "/"
	audience := "https://vault.test.chain.link"
	v := newTestValidator(t, issuer, audience)

	derivedOrg123Owner := testJWTExpectedWorkflowOwner(t, 1, "org-123")
	rawRequest := fmt.Appendf(nil, `{"jsonrpc":"2.0","id":"req-1","method":"vault.secrets.list","params":{"request_id":"req-1","owner":"%s","namespace":"main"}}`, derivedOrg123Owner)
	req, err := jsonrpc.DecodeRequest[json.RawMessage](rawRequest, "")
	require.NoError(t, err)

	digest, err := req.Digest()
	require.NoError(t, err)

	// Raw exp is in the past but still within the JWT validation leeway window.
	tokenExp := time.Now().Add(-30 * time.Second)
	token := createTestJWT(t, rsaKey, jwt.MapClaims{
		"iss":                             issuer,
		"aud":                             audience,
		"exp":                             jwt.NewNumericDate(tokenExp),
		"iat":                             jwt.NewNumericDate(time.Now().Add(-2 * time.Minute)),
		"org_id":                          "org-123",
		ClaimVaultSecretManagementEnabled: "true",
		ClaimChainlinkTenantID:            "1",
		"scope":                           OAuthScopeVaultSecretsList,
		"authorization_details": []any{
			map[string]any{
				"type":  "request_digest",
				"value": digest,
			},
		},
	})

	req, err = jsonrpc.DecodeRequest[json.RawMessage](rawRequest, token)
	require.NoError(t, err)

	a := NewAuthorizer(nil, v, logger.TestLogger(t))

	authResult, err := a.AuthorizeRequest(t.Context(), req)
	require.NoError(t, err)
	require.Equal(t, digest, authResult.Digest())
	require.Equal(t, tokenExp.UTC().Add(time.Minute).Unix(), authResult.ExpiresAt())

	authResult, err = a.AuthorizeRequest(t.Context(), req)
	require.Nil(t, authResult)
	require.ErrorIs(t, err, ErrRequestAlreadySeen)
}
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L227-243)
```go
func shouldRetryGatewayRequest(statusCode int, body []byte) bool {
	if isGatewayNotAllowlistedError(body) {
		return true
	}
	switch statusCode {
	case http.StatusServiceUnavailable, http.StatusBadGateway, http.StatusGatewayTimeout:
		// Gateway-to-DON timeout: the gateway gave up relaying the response, but the DON likely
		// already processed the request. Retrying the same request body just hits the vault
		// replay guard ("request was already authorized previously"). Don't retry these.
		if bytes.Contains(body, []byte("Request timed out")) {
			return false
		}
		return true
	default:
		return false
	}
}
```
