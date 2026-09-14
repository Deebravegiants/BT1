### Title
Replay guard records a request digest as "seen" before owner-binding validation, permanently blocking legitimate resubmission — analog of insert-before-validate ordering bug ([File: core/capabilities/vault/authorizer.go])

### Summary
`authorizer.AuthorizeRequest` writes a request's digest into the `RequestReplayGuard` cache via `CheckAndRecord` *before* it validates that the request's embedded secret-owner fields match the authorized owner. If the subsequent owner-match check fails, the function returns an error, but the digest has already been permanently inserted into the guard's `seen` map and is never rolled back — mirroring the reported bug class of inserting an entity into a table before it passes validation and failing to remove it on error.

### Finding Description
`authorizer.AuthorizeRequest` in `core/capabilities/vault/authorizer.go` performs the steps in this order: [1](#0-0) 

1. Delegate to allow-list-based or JWT-based auth to get an `AuthResult` (owner, digest, expiry).
2. Call `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` — this immediately **records** the digest as "seen" in the in-memory cache.
3. **Only afterward** call `validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner())`, which unmarshals the request params and compares embedded owner fields (`encrypted_secrets[].id.owner`, `ids[].owner`, or `owner`) against the authorized owner.

`RequestReplayGuard.CheckAndRecord` is a pure insert-then-check cache primitive with no rollback capability: [2](#0-1) 

If step 3 fails (owner mismatch), `AuthorizeRequest` returns the error at line 115, but the digest recorded in step 2 is never removed. Because `CheckAndRecord` treats any previously-seen digest as `ErrRequestAlreadySeen`: [3](#0-2) 

any later attempt to submit the *exact same request* (identical method, ID, and params — which is what the digest is computed over) is rejected immediately with "request was already authorized previously," even though it was never actually authorized. The digest is computed over the full request content, including the owner field being validated: [4](#0-3) 

This is functionally identical to the reported bug class: a candidate entity is written into a persistent/cached table (`valTable` / `seen` map) prior to completing validation (`Validate()` / `validateSecretOwnersMatchAuthorized`), and on validation failure the entity is left behind rather than being excluded or removed.

### Impact Explanation
The practical effect is a permanent (until expiry, e.g. up to the on-chain allowlist expiry window used in `ExecuteSecrets`, which can be an hour or more) denial-of-service against a specific legitimate request. Any request whose owner-binding check fails on the first attempt — whether due to a legitimate client-side bug, an owner-normalization mismatch (`vaultutils.NormalizeOwner`), or a benign retry after a transient failure — permanently "burns" that digest in the replay guard. The exact same request, even if it would otherwise be correctly authorized and owner-matched, can never succeed again for the lifetime of the cached expiry, since `CheckAndRecord` cannot distinguish a genuinely-replayed authorized request from a request whose earlier attempt failed authorization for an unrelated reason. This is a resource/availability-impacting logic flaw in the internet-facing vault gateway pipeline, not a data-integrity or fund-movement bypass — I was unable to construct a scenario where this ordering issue enables cross-user response confusion, secret disclosure, or authentication bypass, since the digest is a hash over the full attacker-controlled request content and does not collide with another user's distinct request.

### Likelihood Explanation
This can be triggered by any unprivileged client of the vault gateway (`core/capabilities/vault/gateway_vault_request_processor.go` → `authorizeAndStamp` → `Authorizer.AuthorizeRequest`) with zero special conditions beyond submitting a request whose params' `owner` field doesn't match the authorized owner on the first attempt (e.g., a case-sensitivity or address-format mismatch, or a client bug), then retrying with a corrected/identical payload. Given `NormalizeOwner` only handles lowercase/`0x` prefix normalization, other formatting differences (e.g., checksum vs. non-checksum mismatches elsewhere in the pipeline, or accidental duplicate submissions during retries/timeouts) are plausible in real client implementations.

### Recommendation
Reorder validation in `authorizer.AuthorizeRequest` so that `validateSecretOwnersMatchAuthorized` runs before `replayGuard.CheckAndRecord`, mirroring the fix pattern from the referenced report (perform all validation checks prior to any state-mutating insert). Alternatively, make `RequestReplayGuard` support a rollback/`Remove` operation and call it if any post-record validation step fails.

### Proof of Concept
1. Submit a `vault.secrets.create` request whose digest is allowlisted (or JWT-authorized) but whose `encrypted_secrets[0].id.owner` does not match the authorized owner (e.g., due to a client formatting bug producing `"0xAbC"` vs. the on-chain `"0xabc"` in a different representation, or simply a wrong owner field by mistake).
   - `AuthorizeRequest` calls `replayGuard.CheckAndRecord(digest, expiry)` → succeeds, digest recorded.
   - `validateSecretOwnersMatchAuthorized` → fails with "encrypted secret owner ... does not match authorized workflow owner ...".
   - Request is rejected, per `TestAuthorizer_AllowListPath_RejectsCreateOwnerMismatch`: [5](#0-4) 
2. Correct the client bug and resubmit the identical request (same method/ID/params, hence same digest) that would now pass owner validation.
   - `AuthorizeRequest` calls `replayGuard.CheckAndRecord(digest, expiry)` → digest already present in `seen` map from step 1 → returns `ErrRequestAlreadySeen`, confirmed by the existing replay test pattern: [6](#0-5) 
   - The legitimate request is now permanently rejected until the recorded expiry elapses, even though it was never truly authorized.

### Citations

**File:** core/capabilities/vault/authorizer.go (L99-118)
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

**File:** core/capabilities/vault/authorizer_test.go (L148-170)
```go
func TestAuthorizer_AllowListPath_RejectsCreateOwnerMismatch(t *testing.T) {
	params, err := json.Marshal(vaultcommon.CreateSecretsRequest{
		EncryptedSecrets: []*vaultcommon.EncryptedSecret{
			{Id: &vaultcommon.SecretIdentifier{Owner: "0xother", Namespace: "ns", Key: "k"}, EncryptedValue: "cipher"},
		},
	})
	require.NoError(t, err)

	req := jsonrpc.Request[json.RawMessage]{
		ID:     "1",
		Method: vaulttypes.MethodSecretsCreate,
		Params: (*json.RawMessage)(&params),
	}

	allowListBasedAuth := vaultmocks.NewAuthorizer(t)
	allowListBasedAuth.EXPECT().AuthorizeRequest(mock.Anything, req).Return(vault.NewAuthResult("", "0xauthorized", "digest-1", time.Now().Add(time.Minute).Unix()), nil).Once()

	a := vault.NewAuthorizer(allowListBasedAuth, nil, logger.TestLogger(t))

	authResult, err := a.AuthorizeRequest(t.Context(), req)
	require.Nil(t, authResult)
	require.ErrorContains(t, err, "encrypted secret owner at index 0 \"0xother\" does not match authorized workflow owner \"0xauthorized\"")
}
```
