Audit Report

## Title
Vault replay guard permanently consumes a request digest even when authorization succeeds but downstream owner-validation or processing fails, permanently blocking legitimate retries - ([File: core/capabilities/vault/authorizer.go])

## Summary
`authorizer.AuthorizeRequest` calls `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` immediately after the allowlist/JWT check succeeds, and only afterward calls `validateSecretOwnersMatchAuthorized`. Because `CheckAndRecord` unconditionally marks the digest as permanently "seen" until its on-chain expiry, any request that passes initial auth but fails the subsequent owner-binding check (or any later processing step in `GatewayVaultRequestProcessor`) becomes permanently unresubmittable for the remainder of the allowlist window, even though no secret operation was ever completed.

## Finding Description
Verified against the code: `AuthorizeRequest` in `core/capabilities/vault/authorizer.go` performs `CheckAndRecord` at line 109 before `validateSecretOwnersMatchAuthorized` at line 113. `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go` (lines 35-47) stores the digest with its expiry unconditionally on first call and rejects all subsequent calls with the same digest via `ErrRequestAlreadySeen`, regardless of whether the request that recorded it ultimately succeeded. `validateSecretOwnersMatchAuthorized` (lines 151-197) and `validateEncryptedSecretOwnerMismatch` (lines 199-215) can fail for reasons unrelated to malice (e.g., normalization mismatch, malformed payload), and this failure occurs strictly after the digest has already been recorded. The ordering is confirmed exactly as claimed in the current codebase. [1](#0-0) [2](#0-1) 

## Impact Explanation
This is fundamentally a self-inflicted denial of service: the only party that can trigger this is the workflow owner acting on their own allowlisted request, and the only party impacted by the resulting lockout is that same owner. The digest is derived from the requester's own request content (`req.Digest()`), and the "attacker" precondition here is simply the legitimate owner submitting their own malformed/mismatched request. This does not constitute an authorization bypass, unauthorized state change, key/secret exfiltration, gateway impersonation, or cross-user impact — it does not affect any user other than the one whose own request failed. `SECURITY.md` and `RESEARCHER.md` both explicitly categorize "user self-harm" as excluded, and "Any denial-of-service" impacts are treated cautiously (prohibited to exploit against project assets, and DoS-only impacts are generally out of scope for websites/apps categories). While `RESEARCHER.md` does list "Permanent lock/freeze states created through reachable user actions" as a high-value scenario to test, the described scenario here is bounded strictly to the single requester's own future retries of their own specific allowlisted digest — it does not lock funds, other users' secrets, or node-wide functionality, and is recoverable by obtaining a new allowlist entry. [3](#0-2) 

## Likelihood Explanation
While the ordering bug is real and reproducible, exploiting it provides no attacker advantage over any other party — it only harms the actor who submits their own malformed request, which they control and can avoid by fixing the payload before submission. This does not map to any of the concrete in-scope impact categories (node API authentication/role bypass, key/secret exfiltration, unauthorized job run or fund movement, gateway request impersonation, allowlist/subscription bypass, cross-user response corruption) required by the validation rules.

## Recommendation
Move `replayGuard.CheckAndRecord` to occur only after `validateSecretOwnersMatchAuthorized` succeeds (and ideally after the downstream secrets operation completes) so a digest is only consumed once the request is fully validated end-to-end, improving UX/robustness even though it is not a security-critical fix under the applicable bounty scope.

## Proof of Concept
Not applicable as a security finding — the described PoC (owner allowlists a request, submits it, mismatch causes failure, retry blocked) only demonstrates the reporter locking out their own future retry of their own request, which does not satisfy the required "concrete in-scope impact" against another user, protected asset, or authorization boundary.

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
