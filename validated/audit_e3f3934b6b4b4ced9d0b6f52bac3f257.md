### Title
Vault replay guard permanently consumes a request digest even when authorization succeeds but downstream owner-validation or processing fails, permanently blocking legitimate retries - ([File: core/capabilities/vault/authorizer.go])

### Summary
`authorizer.AuthorizeRequest` records a request's digest in the `RequestReplayGuard` as soon as the allowlist/JWT auth check and expiry check pass, *before* the subsequent owner-binding validation (and before the actual secret create/update/delete/list operation runs). If that later validation step fails — or any downstream processing after `authorizeAndStamp` returns fails — the digest has already been permanently marked "seen" and can never be reused until its on-chain allowlist expiry elapses, even though the user's actual request was never fulfilled. This mirrors the reported bug class: a state flag ("refunded"/"processed"/"seen") is set to true unconditionally after a partial step, permanently disallowing retries regardless of whether the underlying operation actually completed.

### Finding Description
`authorizer.AuthorizeRequest` in [1](#0-0)  performs, in order:
1. `authorizeRequest` (allowlist-based or JWT-based digest/owner check)
2. `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` — this call both checks *and unconditionally records* the digest as consumed
3. `validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner())` — only run *after* the digest has already been recorded

`RequestReplayGuard.CheckAndRecord` [2](#0-1)  stores the digest with its expiry immediately, and every subsequent call with the same digest returns `ErrRequestAlreadySeen` until that expiry timestamp is reached — regardless of whether the request actually succeeded in creating/updating/deleting a secret.

The digest is derived from the on-chain-allowlisted request content itself (via `req.Digest()`), and the allowlisted-request's `ExpiryTimestamp` is set on-chain by the workflow owner when they allowlist the request [3](#0-2) . So if:
- the owner-binding check (`validateSecretOwnersMatchAuthorized`) fails after the digest is already recorded, or
- any later step in `GatewayVaultRequestProcessor.ProcessRequest` (structure validation, ciphertext size validation, param stamping) fails [4](#0-3) , or
- the actual secrets-service call (create/update/delete) later fails for a transient reason,

the request never completes, yet the identical request can never be resubmitted for the remainder of the allowlist window — the caller is fully locked out of that specific allowlisted action with no ability to retry, exactly as in the reported OpenQ refund case where a partial/failed operation still consumes the one-shot flag.

### Impact Explanation
A legitimate vault client (workflow owner interacting through the gateway) who suffers any transient failure after passing initial auth checks (e.g., temporary owner-mismatch bug, malformed-but-fixable params causing `stamp` failure, or a downstream secrets-service error) permanently loses the ability to complete that specific allowlisted operation until the on-chain allowlist expiry passes — at which point they must obtain a brand-new on-chain allowlist entry (another transaction/gas cost) to retry. This is a self-inflicted denial-of-service on secret creation/update/deletion, unlike a simple retryable error, and matches the "one-shot flag consumed regardless of outcome" bug class from the report. Because Vault operations gate node secret storage used by workflows, being unable to create/rotate a secret for an extended window can materially impact workflow execution.

### Likelihood Explanation
This triggers on any legitimate request that passes allowlist/JWT authorization and expiry checks but fails a later, unrelated validation or processing step (owner-binding validation, structural validation, ciphertext-size validation, or the downstream secrets-service call). Such downstream failures are plausible during normal operation (e.g., a workflow-owner-address casing/normalization edge case, a malformed encrypted secret detected only in the ciphertext-size check, or a transient error while writing to the secrets store), so the likelihood of any operator/user encountering it is not negligible, though it requires a downstream failure to actually manifest.

### Recommendation
Only record the digest in `RequestReplayGuard` after the request has fully succeeded (i.e., after `validateSecretOwnersMatchAuthorized` passes and, ideally, after the underlying secrets operation completes), or provide a mechanism to release/un-record a digest when a downstream step fails before the operation is actually committed. At minimum, move `replayGuard.CheckAndRecord` to after `validateSecretOwnersMatchAuthorized` in `authorizer.AuthorizeRequest` [5](#0-4)  so that a request digest is only consumed once the request is fully authorized end-to-end, not merely allowlisted.

### Proof of Concept
1. A workflow owner allowlists a `SecretsCreate` (or update/delete) request digest on-chain with owner `0xAAA` and some expiry.
2. The client sends this request; `authorizeAllowListBasedAuth` succeeds (digest is allowlisted, not expired) and returns an `AuthResult` for owner `0xAAA`.
3. `a.replayGuard.CheckAndRecord(digest, expiresAt)` succeeds and permanently marks the digest as seen.
4. `validateSecretOwnersMatchAuthorized` then fails — e.g., because the `EncryptedSecrets[].Id.Owner` field in the request params does not exactly match the normalized authorized owner (a mismatch that can occur due to address-casing/format differences, unrelated to malice) — see `validateEncryptedSecretOwnerMismatch` [6](#0-5) .
5. The overall `AuthorizeRequest` call returns an error and the secret is never created.
6. The client fixes nothing (the digest is computed over the full unmodified request) and retries the identical request; `CheckAndRecord` now returns `ErrRequestAlreadySeen` [2](#0-1) , permanently blocking the request until the on-chain allowlist expiry elapses, even though zero secret operations were ever performed for this digest.

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

**File:** core/capabilities/vault/authorizer.go (L199-215)
```go
func validateEncryptedSecretOwnerMismatch(encryptedSecrets []*vaultcommon.EncryptedSecret, workflowOwner string) error {
	if len(encryptedSecrets) == 0 {
		return errors.New("request batch must contain at least 1 item")
	}
	for idx, encryptedSecret := range encryptedSecrets {
		if encryptedSecret == nil {
			return fmt.Errorf("encrypted secret must not be nil at index %d", idx)
		}
		if encryptedSecret.Id == nil {
			return fmt.Errorf("secret ID must not be nil at index %d", idx)
		}
		if vaultutils.NormalizeOwner(encryptedSecret.Id.Owner) != vaultutils.NormalizeOwner(workflowOwner) {
			return fmt.Errorf("encrypted secret owner at index %d %q does not match authorized workflow owner %q", idx, encryptedSecret.Id.Owner, workflowOwner)
		}
	}
	return nil
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

**File:** core/capabilities/vault/allow_list_based_auth.go (L64-76)
```go
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-293)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}

	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}

	p.lggr.Debugw("authorized gateway vault request", "method", req.Method, "requestID", req.ID, "owner", authorizedOwner, "orgID", authResult.OrgID(), "workflowOwner", authResult.WorkflowOwner())
	return &AuthorizedGatewayVaultRequest{
		Req:        *req,
		AuthResult: authResult,
	}, nil
}
```
