### Title
Hardcoded JWT tolerance/expiry combined with independently configurable replay-cache cleanup period enables JWT replay bypass in `WorkflowMetadataHandler.Authorize` - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
This is the same "hardcoded tolerance" bug class as the reported `_applySlippage` issue: a security-relevant tolerance value is hardcoded and not tied to related configurable parameters, which can be exploited or cause failures. In the gateway's HTTP-trigger workflow metadata handler, `Authorize()` verifies a caller-supplied JWT via `utils.VerifyRequestJWT` using hardcoded defaults (`defaultIssuedAtTolerance = 5*time.Minute`, `maxJWTExpiryDuration = 5*time.Minute`) rather than the configurable `WithIssuedAtTolerance`/`WithMaxExpiryDuration` options that exist in the same package [1](#0-0) . Meanwhile the JWT replay-protection cache's cleanup interval is independently configurable via `JWTReplayPeriodMs` [2](#0-1) . Because these two windows are not coupled, an operator (or default config) can set `JWTReplayPeriodMs` shorter than the token's maximum valid lifetime (tolerance + max expiry, up to ~10 minutes), allowing a previously-used, still within-tolerance JWT to be replayed successfully once its `jti` entry is purged from the replay cache.

### Finding Description
`Authorize` calls `utils.VerifyRequestJWT(token, *req)` with no verify options at all [3](#0-2) , so the hardcoded package-level defaults are always used: `issuedAtTolerance` of 5 minutes and `maxExpiryDuration` of 5 minutes [1](#0-0) [4](#0-3) . This means a JWT can legitimately have `iat` up to 5 minutes in the future and `exp` up to 5 minutes after `iat`, giving each token a maximum acceptance window of up to ~10 minutes from creation.

Replay protection is implemented separately via `jwtReplayCache`, whose entries are recorded on first use and purged by a background ticker running every `cleanupPeriod` (`h.config.JWTReplayPeriodMs`) [5](#0-4) . `cleanupOldEntries` deletes any cache entry recorded before `now - cleanupPeriod` [6](#0-5) .

If `JWTReplayPeriodMs` is configured (or defaults) to a value smaller than the hardcoded token validity window, a `jti` can be evicted from the replay cache while the token is still within its `exp`/`iat` tolerance and would still pass `VerifyRequestJWT`. Since `isReplay` only checks presence in this now-empty-of-that-entry cache [7](#0-6) , `Authorize` will accept the same JWT a second time, defeating the intended single-use guarantee and allowing request impersonation for that workflow/signer combination during the residual validity window.

The root cause mirrors the original report exactly: a hardcoded, non-configurable tolerance value (`defaultIssuedAtTolerance`/`maxJWTExpiryDuration`) is not aligned with an operationally-configurable, related parameter (`JWTReplayPeriodMs`), and there is no validation ensuring `cleanupPeriod >= issuedAtTolerance + maxExpiryDuration`.

### Impact Explanation
An attacker who observes or intercepts one valid signed JWT (e.g. via network exposure, logging, or a compromised intermediary) can replay it to call `Authorize` again after the replay-cache entry is purged, as long as the token has not yet expired per the hardcoded (but unconfigurable) tolerance window. This results in request impersonation / bypass of the intended single-use authorization control on an internet-facing gateway handler. Impact is Medium: it requires possession of a previously valid token and a misaligned/short cleanup interval, but when triggered it defeats the JWT replay-protection guarantee entirely.

### Likelihood Explanation
Likelihood is Medium: it depends on operator configuration of `JWTReplayPeriodMs` relative to the hardcoded 5-minute tolerance/expiry values, and there is no code-level guard preventing this misconfiguration. Because the hardcoded values are invisible to operators (not documented as needing to be reconciled with `JWTReplayPeriodMs`), a misconfiguration is plausible in production without any obvious warning.

### Recommendation
- Make the JWT `issuedAtTolerance` and `maxExpiryDuration` used in `Authorize` explicitly configurable (using the existing `WithIssuedAtTolerance`/`WithMaxExpiryDuration` options) rather than always falling back to hardcoded package constants.
- Add a startup/config validation that enforces `JWTReplayPeriodMs >= issuedAtTolerance + maxExpiryDuration`, so replay-cache entries cannot be purged before a token could naturally expire.
- Alternatively, key the cache eviction to the token's own `exp` claim rather than a fixed wall-clock cleanup period.

### Proof of Concept
1. Configure the gateway with `JWTReplayPeriodMs` set to a value smaller than 10 minutes (e.g. 1 minute) while the JWT verification path uses the hardcoded 5-minute `issuedAtTolerance` + 5-minute `maxExpiryDuration` defaults in `VerifyRequestJWT` [1](#0-0) .
2. A valid signer creates and sends a JWT-authenticated request to `WorkflowMetadataHandler.Authorize` with `iat = now`, `exp = now + 5m`. The request succeeds and `claims.ID` (`jti`) is recorded in `jwtCache` [8](#0-7) .
3. Wait slightly over 1 minute (the configured `cleanupPeriod`); the background ticker calls `cleanupOldEntries(now - cleanupPeriod)`, evicting the `jti` entry [5](#0-4) .
4. Replay the identical JWT (still within its 5-minute `exp`). `VerifyRequestJWT` accepts it again (still within tolerance/expiry), and `h.jwtCache.isReplay(claims.ID)` returns `false` since the entry was purged, so `Authorize` succeeds a second time — demonstrating the replay bypass.

### Citations

**File:** core/utils/jwt.go (L19-22)
```go
const (
	maxJWTExpiryDuration     = 5 * time.Minute // Maximum allowed expiry duration
	defaultIssuedAtTolerance = 5 * time.Minute // Default tolerance for issuedAt validation to handle clock drift
)
```

**File:** core/utils/jwt.go (L237-245)
```go
	maxExpiryDuration := maxJWTExpiryDuration
	if options.maxExpiryDuration != nil {
		maxExpiryDuration = *options.maxExpiryDuration
	}

	issuedAtTolerance := defaultIssuedAtTolerance
	if options.issuedAtTolerance != nil {
		issuedAtTolerance = *options.issuedAtTolerance
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L75-77)
```go
		metrics:         metrics,
		jwtCache:        newJWTReplayCache(time.Duration(cfg.JWTReplayPeriodMs) * time.Millisecond),
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-85)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L105-107)
```go
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-405)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L414-425)
```go
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
```
