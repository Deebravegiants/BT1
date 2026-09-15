### Title
Unbounded, cross-tenant growth of the gateway JWT-replay cache before rate limiting enables memory-exhaustion DoS - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The `WorkflowMetadataHandler` maintains a single, gateway-wide `jwtReplayCache` (`cache map[string]time.Time`, keyed by JWT `jti`) that is written to on every successful HTTP-trigger authorization, and is only pruned by a periodic time-based sweep (`cleanupOldEntries`, driven by `JWTReplayPeriodMs`, default 24h) rather than by any size bound. Crucially, in `httpTriggerHandler.HandleUserTriggerRequest`, the call to `authorizeRequest` (which records the `jti` via `h.workflowMetadataHandler.Authorize` → `jwtCache.recordUsage`) happens **before** `checkRateLimit`. This mirrors the `Cooler.sol` `Request[]` bug class: a data structure that grows on every valid/authenticated request and is never bounded except by wall-clock time, allowing an authenticated-but-unprivileged caller to force unbounded memory growth shared across all tenants on the gateway node.

### Finding Description
In `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`, `HandleUserTriggerRequest` executes:
1. `h.authorizeRequest(ctx, workflowID, req, callback)` — line 106
2. `h.checkRateLimit(ctx, workflowID, req.ID, callback)` — line 111

`authorizeRequest` calls `h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)`, which in `workflow_metadata_handler.go`:
```go
if h.jwtCache.isReplay(claims.ID) { ... }
...
h.jwtCache.recordUsage(claims.ID)
```
`recordUsage` unconditionally inserts the JWT's `jti` into `jwtReplayCache.cache` [1](#0-0) . This insertion happens **before** the per-workflow-owner rate limiter (`h.userRateLimiter.AllowErr(ctx)`) is even checked [2](#0-1) , so the rate limiter cannot bound how fast the cache grows — it only bounds how many requests are subsequently allowed to proceed to actual workflow execution.

The cache itself has no maximum-size eviction; it is only cleaned by `cleanupOldEntries`, which deletes entries whose insertion time is older than `JWTReplayPeriodMs` (default 24 hours) [3](#0-2) . Any caller holding a single valid authorized ECDSA key for any one registered workflow (the minimum bar to pass `Authorize`) can mint an unlimited number of uniquely-`jti`'d, validly-signed JWTs and fire them at the gateway's HTTP-trigger endpoint at line-rate. Each request:
- Passes signature/digest verification in `VerifyRequestJWT` [4](#0-3) 
- Passes the replay check (each `jti` is unique, so never previously seen)
- Gets recorded into the shared `jwtCache` map
- Only then is it throttled by the per-workflow rate limiter, which the attacker doesn't care about — the goal is only to grow the map

Since `jwtCache` is a single instance shared by the entire `WorkflowMetadataHandler` (not partitioned per-workflow or per-owner), this growth affects the memory footprint for every workflow's trigger authorization served by that gateway process, not just the attacker's own workflow.

### Impact Explanation
An authenticated holder of any single workflow's authorized signing key can grow an unbounded, gateway-wide in-memory map (keyed by attacker-chosen strings) at essentially network line-rate, independent of the intended per-workflow-owner rate limit, for up to the full `JWTReplayPeriodMs` window (default 24 hours) before any entries are reclaimed. Sustained abuse can exhaust gateway process memory, causing the `HTTPCapabilityHandler`/`WorkflowMetadataHandler` (and potentially the whole gateway process, since Go's GC and OOM behavior affects the entire process) to degrade or crash — a denial of service impacting all workflows served by that gateway shard, not just the attacker's own. This matches the Medium-severity impact described in the reference report: an authenticated but low-cost/low-privilege action leads to unbounded growth of a core protocol data structure with no cap, eventually causing DoS for all users of that resource.

### Likelihood Explanation
Likelihood is limited by the precondition that the attacker must possess (or compromise) at least one valid, currently-authorized signing key for some registered workflow on the target gateway/DON shard — this is not a fully anonymous/unauthenticated attack. However, once that bar is met (which is the normal operational bar for any legitimate workflow consumer, analogous to depositing "1 wei" of collateral in the original report), the attack is trivial to execute: generate new JWTs with fresh `jti`s and fire requests as fast as the network allows, since the `Authorize` step happens before rate limiting and the cache has no cap besides a 24-hour timer.

### Recommendation
- Move `checkRateLimit` before `authorizeRequest` (or otherwise gate JWT verification/cache writes behind the rate limiter) so that per-owner/per-workflow limits actually bound the rate of `jwtCache` insertions.
- Add an explicit maximum size (and/or per-owner sub-limit) to `jwtReplayCache`, evicting oldest entries (or rejecting new insertions) once the cap is reached, instead of relying solely on time-based expiry via `cleanupOldEntries`.
- Consider partitioning the replay cache per workflow/owner so a single compromised or malicious key cannot inflate memory shared by unrelated workflows on the same gateway shard.
- Shorten `JWTReplayPeriodMs` or add more frequent/size-triggered cleanup passes if a global cap isn't feasible.

### Proof of Concept
1. Obtain a valid ECDSA signing key already registered as an authorized key for any workflow on the target gateway/DON (the normal precondition for triggering that workflow via HTTP).
2. In a loop, construct JSON-RPC `workflows.execute` requests to the HTTP-trigger endpoint (`gateway_common.MethodWorkflowExecute`), each with a unique request `id` and a freshly minted JWT (`utils.CreateRequestJWT`) carrying a unique `jti` and a digest matching the request, signed with the compromised/legit key.
3. Fire these requests as fast as possible via the gateway's public endpoint. Each one:
   - Passes `VerifyRequestJWT` and `isReplay` checks (new `jti` each time)
   - Triggers `jwtCache.recordUsage(claims.ID)` in `workflow_metadata_handler.go` line 105/411, growing the shared map
   - Is only *afterward* subject to `checkRateLimit`, so most requests can be rejected downstream by the rate limiter while still having already grown the cache.
4. Observe `WorkflowMetadataHandler.jwtCache.cache` grow unbounded (proportional to attacker's send rate × time) until the periodic `cleanupOldEntries` sweep runs (governed by `JWTReplayPeriodMs`, default 24h), during which gateway memory usage increases correspondingly.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L407-412)
```go
func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L414-426)
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
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```

**File:** core/utils/jwt.go (L228-304)
```go
// VerifyRequestJWT verifies a signed JWT for a JSON-RPC request
// It recovers and returns the public key used to sign the JWT, checks the issuer, validates the digest,
// and performs all validations done by jwt.ParseWithClaims() including expiration checks.
func VerifyRequestJWT[T any](tokenString string, req jsonrpc.Request[T], opts ...VerifyOption) (*JWTClaims, gethcommon.Address, error) {
	options := &verifyOptions{}
	for _, opt := range opts {
		opt(options)
	}

	maxExpiryDuration := maxJWTExpiryDuration
	if options.maxExpiryDuration != nil {
		maxExpiryDuration = *options.maxExpiryDuration
	}

	issuedAtTolerance := defaultIssuedAtTolerance
	if options.issuedAtTolerance != nil {
		issuedAtTolerance = *options.issuedAtTolerance
	}
	signedString, signature, err := splitToken(tokenString)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	decodedSignature, err := base64.RawURLEncoding.DecodeString(signature)
	if err != nil {
		return nil, gethcommon.Address{}, fmt.Errorf("signature segment is not valid base64url: %w", err)
	}
	pubKey, err := GetSignersEthAddress([]byte(signedString), decodedSignature)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	verifiedToken, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (any, error) {
		if token.Method.Alg() != EthereumSigningMethod.Alg() {
			return nil, fmt.Errorf("unsupported JWT 'alg': '%s'. Expected '%s'", token.Method.Alg(), EthereumSigningMethod.Alg())
		}
		if _, ok := token.Method.(*SigningMethodEth); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return pubKey, nil
	})
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	verifiedClaims, ok := verifiedToken.Claims.(*JWTClaims)
	if !ok {
		return nil, gethcommon.Address{}, errors.New("claims payload is not in the expected format")
	}
	if !verifiedToken.Valid {
		return nil, gethcommon.Address{}, errors.New("signature or claims validation failed")
	}
	reqDigest, err := req.Digest()
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	if verifiedClaims.ID == "" {
		return nil, gethcommon.Address{}, errors.New("JWT ID (jti) is required but missing")
	}
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
	if verifiedClaims.Digest != "0x"+reqDigest {
		return nil, gethcommon.Address{}, fmt.Errorf("claim digest '%s' does not match calculated request digest '0x%s'", verifiedClaims.Digest, reqDigest)
	}

	return verifiedClaims, pubKey, nil
}
```
