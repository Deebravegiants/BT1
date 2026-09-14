### Title
JWT anti-replay cache eviction is decoupled from token expiry, allowing signed request replay in the HTTP Trigger gateway - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
The reported bug class is "lack of expiration/revocation control over a signed authorization artifact." The closest reachable analog in this codebase is the `WorkflowMetadataHandler.Authorize` flow on the internet-facing gateway, which authenticates unprivileged HTTP-trigger callers via a self-signed JWT (`utils.VerifyRequestJWT`) and relies on a separate, independently-configured in-memory cache (`jwtReplayCache`) to prevent replay of a given `jti`. The cache's eviction window is not tied to the token's own `exp`/`iat` lifetime, so a used token's single-use protection can lapse before the token itself has actually expired.

### Finding Description
`Authorize` verifies the JWT's signature, issuer, `exp`/`iat` bounds (via `utils.VerifyRequestJWT`, capped by `maxJWTExpiryDuration`) [1](#0-0) , then separately checks a local `jwtReplayCache` keyed by `claims.ID` (the `jti`) to reject reuse of the same token [2](#0-1) .

The replay cache, however, is pruned on its own independent timer using `JWTReplayPeriodMs`/`cleanupPeriod`, not the token's actual `exp`: [3](#0-2) [4](#0-3) 

`cleanupOldEntries` deletes any `jti` recorded more than `cleanupPeriod` ago — this is unrelated to the token's own signed `exp` claim, which can be set (within `maxJWTExpiryDuration`) to a longer window than `cleanupPeriod`. Once a `jti` is evicted from the cache, `isReplay` returns `false` again for it [5](#0-4) , so the exact same still-valid, signed JWT/request can be resubmitted and will pass authorization a second (or Nth) time before it naturally expires.

This mirrors the reported bug class: there is no mechanism binding the "revocation"/single-use window to the artifact's own stated expiration, so an attacker who has observed one signed request in transit (or a legitimate caller retrying) can replay it beyond the intended single-use semantics for as long as the token remains within its own `exp`.

### Impact Explanation
Because `Authorize` is the sole gate protecting `HandleUserTriggerRequest` on the gateway for unprivileged HTTP-trigger callers, a successful replay lets an attacker who intercepts (or otherwise obtains) a valid signed trigger request re-invoke the associated workflow trigger multiple times within the token's validity window, even though the design intent (`jti` + single-use cache) is exactly to prevent this. Depending on the workflow, repeated triggering can cause duplicate off-chain/on-chain side effects (e.g., duplicate job runs, duplicate fund-moving actions initiated by the workflow), which is a request-impersonation/replay class of impact.

### Likelihood Explanation
Likelihood depends entirely on operator configuration: it requires `JWTReplayPeriodMs` (the anti-replay cache retention) to be shorter than the actual `exp - iat` duration chosen by callers for their JWTs (itself bounded by `maxJWTExpiryDuration`). If these two independent knobs are not kept in sync — which the code does not enforce or validate anywhere — the replay window reopens automatically on every cleanup tick. I was not able to verify the concrete default values configured for `JWTReplayPeriodMs` vs. `maxJWTExpiryDuration` in this session (ran out of tool calls), so it is uncertain in the default deployment configuration whether the exploitable window is realistically small or large; this should be confirmed by inspecting `core/services/gateway/handlers/capabilities/v2/http_handler.go` defaults and `core/utils/jwt.go`'s `maxJWTExpiryDuration` constant.

### Recommendation
Tie the replay-cache retention to the actual claimed expiry of each token rather than a fixed global cleanup period: store `claims.ExpiresAt` alongside the `jti` when recording usage, and only evict an entry once `time.Now()` is past that specific `exp` (with a small grace buffer), instead of a blanket `cleanupPeriod` cutoff. Additionally, enforce at startup/config-validation time that `JWTReplayPeriodMs >= maxJWTExpiryDuration` (or eliminate the separate config entirely) so the anti-replay guarantee cannot silently be undermined by misconfiguration.

### Proof of Concept
1. Configure the gateway with `JWTReplayPeriodMs` smaller than the JWT lifetime a caller may legitimately choose (up to `maxJWTExpiryDuration`).
2. Client issues a signed JSON-RPC HTTP-trigger request with `iat=t0`, `exp=t0+maxJWTExpiryDuration`, and calls the gateway; `Authorize` succeeds and `recordUsage(jti)` stores it at `t0`.
3. Wait until `t0 + cleanupPeriod` elapses (still `< exp`); the periodic ticker in `Start()` calls `cleanupOldEntries` and evicts the `jti`.
4. Resubmit the identical previously-observed JWT/request. `VerifyRequestJWT` still succeeds (token not yet expired), and `isReplay(claims.ID)` now returns `false` since the entry was evicted, so `Authorize` accepts the replayed request a second time. [2](#0-1) [3](#0-2) [6](#0-5)

### Citations

**File:** core/utils/jwt.go (L284-298)
```go
	if verifiedClaims.ExpiresAt == nil {
		return nil, gethcommon.Address{}, errors.New("expiredAt (exp) is required but missing")
	}
	if verifiedClaims.IssuedAt == nil {
		return nil, gethcommon.Address{}, errors.New("issuedAt (iat) is required but missing")
	}
	now := time.Now()
	issuedAt := verifiedClaims.IssuedAt
	if issuedAt.After(now.Add(issuedAtTolerance)) {
		return nil, gethcommon.Address{}, fmt.Errorf("issuedAt (iat) is too far in the future (beyond tolerance of %.0f seconds)", issuedAtTolerance.Seconds())
	}
	duration := verifiedClaims.ExpiresAt.Sub(verifiedClaims.IssuedAt.Time)
	if duration > maxExpiryDuration {
		return nil, gethcommon.Address{}, fmt.Errorf("token lifetime %.0f sec exceeds the maximum allowed %.0f sec. Reduce the gap between 'iat' and 'exp'", duration.Seconds(), maxExpiryDuration.Seconds())
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-108)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
	if _, exists = keys[key]; !exists {
		h.lggr.Errorw("Signer not found in authorized keys", "signer", signer.Hex())
		return nil, fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)
	}
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L298-304)
```go
		h.runTicker(h.jwtCache.cleanupPeriod, func(ctx context.Context) {
			now := time.Now()
			expiredCount := h.jwtCache.cleanupOldEntries(now.Add(-h.jwtCache.cleanupPeriod))
			h.metrics.IncrementJwtCacheCleanUpCount(ctx, int64(expiredCount), h.lggr)
			h.metrics.RecordJwtCacheSize(ctx, int64(len(h.jwtCache.cache)), h.lggr)
			h.lggr.Debugw("Workflow execution cache cleanup completed", "expired_entries", expiredCount, "remaining_entries", len(h.jwtCache.cache))
		})
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-426)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}

func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}

// cleanupOldEntries removes expired entries from the cache
func (cache *jwtReplayCache) cleanupOldEntries(cutoff time.Time) int {
	cache.mu.Lock()
	defer cache.mu.Unlock()
	var expiredCount int
	for jti, createdAt := range cache.cache {
		if createdAt.Before(cutoff) {
			delete(cache.cache, jti)
			expiredCount++
		}
	}
	return expiredCount
}
```
