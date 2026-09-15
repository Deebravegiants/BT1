## Analysis

The externally-reported bug uses zero as a "flag" sentinel value that, when it coincides with a legitimately-occurring real value, silently disables a protection mechanism. The closest reachable analog in this codebase is in the Vault gateway's replay-protection mechanism, `RequestReplayGuard`, which uses an expiry timestamp both as "the value at which this record should be purged" and implicitly relies on that value never legitimately being `<= now()`.

`RequestReplayGuard.CheckAndRecord` unconditionally calls `clearExpiredLocked()` *before* checking whether a digest was already seen: [1](#0-0) 

`clearExpiredLocked` purges any digest whose stored expiry is `<= now`: [2](#0-1) 

The stored expiry comes directly from `AuthResult.expiresAt`, which is a private `int64` field with the Go zero value `0`, and `AuthResult.ExpiresAt()` explicitly returns `0` for a `nil` receiver: [3](#0-2) [4](#0-3) 

`authorizer.AuthorizeRequest` feeds `authResult.ExpiresAt()` straight into the replay guard: [5](#0-4) 

Both authorization backends compute `expiresAt` from external, request-controllable data: the allowlist backend takes it directly from the on-chain `ExpiryTimestamp` field of the allowlisted request, and the JWT backend takes it from the token's `exp` claim (plus a fixed leeway): [6](#0-5) [7](#0-6) 

If `expiresAt` ends up `0` (or any timestamp `<= now`, e.g. an already-past on-chain `ExpiryTimestamp`, which is only prevented by a separate off-chain changeset precondition rather than by the guard itself) for an otherwise-valid, currently-accepted authorization, the very next call to `CheckAndRecord` purges that digest entry as "expired" before checking for a duplicate — silently disabling replay protection for that specific request. This mirrors the LSP bug class: a timestamp value that is supposed to signal "not yet meaningfully set / already gone" instead coincides with a real, currently-valid authorization, defeating the protection that depends on the sentinel being distinguishable from a legitimate value.

I could not fully verify from static analysis alone whether the on-chain `ExpiryTimestamp` can practically be `0` or already-past at the moment `AuthorizeRequest` runs in production (the off-chain changeset `UserAllowlistRequest.VerifyPreconditions` rejects `ExpiryTimestamp == 0`, but that check is not enforced by the contract or by `allowListBasedAuth` itself, and a request could be authorized just as its expiry passes). This gap in confirmation should be validated with a live/replayed test against the deployed `WorkflowRegistry` contract and gateway before treating this as fully confirmed.

### Title
Replay guard treats already-expired/zero-expiry authorizations as immediately purgeable, defeating Vault request replay protection - (File: core/capabilities/vault/request_replay_guard.go)

### Summary
`RequestReplayGuard.CheckAndRecord` purges a digest's replay-protection entry whenever its recorded expiry is `<= now`, including a zero/default expiry. Since `AuthResult.expiresAt` is attacker-influenced (via on-chain allowlist expiry or JWT `exp` claim) and can legitimately be `0` or already in the past at authorization time, an authorized-but-near/at-expiry request's replay-guard entry is purged on the *very next* `CheckAndRecord` call, allowing the same request to be replayed and reauthorized instead of being blocked as a duplicate.

### Finding Description
`CheckAndRecord` always calls `clearExpiredLocked()` first, which deletes any digest whose recorded expiry timestamp is not in the future: [8](#0-7) 
Only after this purge does it check `g.seen[digest]` for a duplicate and then re-insert. The expiry value stored is `authResult.ExpiresAt()`, sourced from either the on-chain allowlist's `ExpiryTimestamp` field or the JWT's `exp` claim: [5](#0-4) [6](#0-5) 
Because `AuthResult.expiresAt` is a plain `int64` with Go's zero-value default, and `ExpiresAt()` returns `0` for a nil result, any code path that produces (or a caller that legitimately authorizes) an `AuthResult` with `expiresAt <= now()` causes the just-recorded replay entry to be treated as already expired and removed on the next guard check — re-enabling reuse of that authorized request digest.

### Impact Explanation
If exploited, this allows an unprivileged client to resend an already-authorized Vault request (`secrets/create`, `secrets/list`, `secrets/delete`, etc.) and have it reauthorized as if it were new, defeating the replay-protection guarantee the `RequestReplayGuard` is specifically designed to provide. Depending on the method, this could allow repeated execution of secret-management operations using a stale, near-expiry authorization.

### Likelihood Explanation
Likelihood depends on how frequently an authorization's `expiresAt` is `0` or already in the past at the moment of authorization — e.g., an on-chain allowlist entry whose `ExpiryTimestamp` has just elapsed by the time the gateway processes the request, or a request processed right at the JWT boundary. The off-chain changeset used to create allowlist entries rejects `ExpiryTimestamp == 0`, but this is not enforced at the contract or authorization layer itself, so the guarantee is incomplete.

### Recommendation
Reject or clamp non-future expiry values before recording them in `RequestReplayGuard` (i.e., treat `expiresAt <= now()` as an authorization failure rather than silently allowing insertion-then-immediate-purge), and enforce a minimum "expiresAt in the future" invariant at the point `AuthResult` is constructed in both `allow_list_based_auth.go` and `jwt_based_auth.go`.

### Proof of Concept
Not independently reproduced end-to-end; reasoning is based on static code review of `request_replay_guard.go` and `authorizer.go`, cross-referenced with `allow_list_based_auth.go` and `jwt_based_auth.go`. A concrete PoC would require constructing an on-chain allowlist entry whose `ExpiryTimestamp` is at or before the current time when the gateway authorizes it, then issuing the same request twice to observe the second one bypass `ErrRequestAlreadySeen`.

### Citations

**File:** core/capabilities/vault/request_replay_guard.go (L35-64)
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

// ClearExpired removes all entries whose expiry timestamp is in the past.
// Call this to eagerly reclaim memory even when CheckAndRecord is not invoked.
func (g *RequestReplayGuard) ClearExpired() {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.clearExpiredLocked()
}

func (g *RequestReplayGuard) clearExpiredLocked() {
	now := g.nowFunc().UTC().Unix()
	for digest, expiry := range g.seen {
		if now > expiry {
			delete(g.seen, digest)
		}
	}
}
```

**File:** core/capabilities/vault/authorizer.go (L18-34)
```go
type AuthResult struct {
	orgID         string
	workflowOwner string
	digest        string
	expiresAt     int64
}

// NewAuthResult remains exported for cross-package tests that cannot construct
// AuthResult directly because its fields are intentionally private.
func NewAuthResult(orgID, workflowOwner, digest string, expiresAt int64) *AuthResult {
	return &AuthResult{
		orgID:         orgID,
		workflowOwner: workflowOwner,
		digest:        digest,
		expiresAt:     expiresAt,
	}
}
```

**File:** core/capabilities/vault/authorizer.go (L69-76)
```go
// ExpiresAt returns the unix timestamp (UTC) after which this
// authorization is no longer valid.
func (a *AuthResult) ExpiresAt() int64 {
	if a == nil {
		return 0
	}
	return a.expiresAt
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

**File:** core/capabilities/vault/jwt_based_auth.go (L225-233)
```go
	authExpiresAt := claims.ExpiresAt.UTC().Add(jwtValidationLeeway).Unix()
	v.lggr.Debugw("JWTBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", derivedWorkflowOwner, "digest", requestDigest, "expiresAt", authExpiresAt)
	return &AuthResult{
		orgID:         claims.OrgID,
		workflowOwner: derivedWorkflowOwner,
		digest:        requestDigest,
		expiresAt:     authExpiresAt,
	}, nil
}
```
