## Title
Unbounded in-memory JWT replay cache in the HTTP Trigger gateway handler allows memory-exhaustion DoS - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The Gateway's HTTP Trigger handler protects against JWT replay by recording every successfully-authorized JWT's `jti` in an in-memory map, `jwtReplayCache.cache`. This map has no maximum size and is only pruned by a periodic cleanup ticker whose default period is **24 hours**. Because the write to this cache happens *before* the per-workflow-owner rate limiter is enforced, an external caller who legitimately controls one workflow trigger (a normal, unprivileged CRE end-user action, not an operator/node privilege) can generate an unbounded number of small, uniquely-`jti`'d signed requests and grow this map continuously in memory for up to 24 hours before any entries are evicted — mirroring the xgrammar unbounded-cache DoS pattern (many small unique requests → unbounded memory growth via a compile/verify cache with no size cap).

### Finding Description
`jwtReplayCache` is a plain map keyed by JWT ID with no capacity bound: [1](#0-0) 

Every time `Authorize` succeeds (valid signature, digest match, unused `jti`, and signer present in the workflow's `authorizedKeys`), it unconditionally records the `jti` into this map: [2](#0-1) 

The only reclamation mechanism is a ticker-driven `cleanupOldEntries` pass, scheduled at `h.jwtCache.cleanupPeriod`: [3](#0-2) 

That period is derived from `JWTReplayPeriodMs`, whose default is a full day: [4](#0-3) 

Critically, in `HandleUserTriggerRequest`, `authorizeRequest` (which triggers the cache write via `WorkflowMetadataHandler.Authorize`) runs **before** the per-workflow-owner rate limiter (`checkRateLimit`) is enforced: [5](#0-4) 

This means the cache-growth step is not gated by the rate limiter at all — an authorized caller (i.e., any workflow owner with a registered HTTP-trigger workflow, which is the normal, unprivileged way to use this feature) can sign an unbounded stream of requests, each with a fresh `jti`/request `id`/digest, and every one of them adds a permanent (until the next 24-hour sweep) entry to `h.jwtCache.cache`, regardless of whether the request is subsequently throttled by `checkRateLimit`.

### Impact Explanation
Each cache entry is small (a string key plus a `time.Time`), but sustained flooding for hours before the 24-hour cleanup window elapses can accumulate a very large number of entries, consuming gateway node memory and potentially triggering OOM conditions on the Gateway process, denying service to all workflows sharing that gateway instance — directly analogous to the xgrammar CVE's "many small requests with unique keys fill unbounded cache → memory DoS" pattern. This is reachable by any legitimate (non-operator, non-node) party who owns a registered workflow with an HTTP trigger, since JWT authorization (not node-level or operator-level access) is the only prerequisite.

### Likelihood Explanation
Likelihood is moderate-to-high for any party running a registered workflow: they hold the private key needed to sign valid JWTs for their own workflow, and generating unique `jti`/request IDs at high volume is trivial and costs the attacker very little (only their own workflow-owner rate limit throttles the resulting external calls to the DON — not the cache-write itself). The 24-hour default cleanup window gives a large amplification runway before any pruning occurs.

### Recommendation
- Enforce `checkRateLimit` (or an equivalent unauthenticated-write throttle) before `authorizeRequest` records new `jti` entries, so JWT-cache growth is capped by the same limiter that gates downstream DON traffic.
- Add an explicit maximum size / bounded LRU eviction to `jwtReplayCache` (similar to `requestCache`'s `maxCacheSize` bound in `core/services/gateway/handlers/common/requestcache.go`), independent of the time-based TTL sweep.
- Consider shortening the default `JWTReplayPeriodMs` cleanup interval or triggering eviction proactively once the map exceeds a configured entry-count threshold.

### Proof of Concept
1. Register a workflow with an HTTP trigger and obtain a valid ECDSA signing key registered as an `AuthorizedKey` for that workflow (normal onboarding flow).
2. For each of N requests, construct a `jsonrpc.Request` with a unique `id`, compute its digest, and sign a JWT with a fresh unique `jti` via `utils.CreateRequestJWT`/`SigningMethodEth` (as done in `createTestJWTToken` in the test suite, see `core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go`).
3. Submit all N requests to the Gateway's `workflows.execute` endpoint in rapid succession before the 24-hour cleanup ticker fires.
4. Each request that passes `Authorize` (signature + digest + authorized-signer checks) adds one entry to `WorkflowMetadataHandler.jwtCache.cache`, growing unbounded in memory regardless of whether `checkRateLimit` subsequently rejects the request from reaching the DON.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L29-34)
```go
// jwtReplayCache manages used JWT IDs to prevent replay attacks
type jwtReplayCache struct {
	mu            sync.RWMutex
	cleanupPeriod time.Duration
	cache         map[string]time.Time // jti -> timestamp
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L29-44)
```go
const (
	handlerName                          = "HTTPCapabilityHandler"
	defaultCleanUpPeriodMs               = 1000 * 60 * 10 // 10 minutes
	defaultMaxTriggerRequestDurationMs   = 1000 * 60      // 1 minute
	defaultNodeSendTimeoutMs             = 1000 * 10      // 10 seconds
	defaultInitialIntervalMs             = 100
	defaultMaxIntervalTimeMs             = 1000 * 30 // 30 seconds
	defaultMultiplier                    = 2.0
	defaultMetadataPullIntervalMs        = 1000 * 60 // 1 minute
	defaultMetadataAggregationIntervalMs = 1000 * 60 // 1 minute
	defaultMetadataPullRequestTimeoutMs  = 1000 * 30 // 30 seconds
	internalErrorMessage                 = "Internal server error occurred while processing the request"
	defaultOutboundRequestCacheTTLMs     = 1000 * 60 * 10      // 10 minutes
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
	defaultSendResponseTimeoutMs         = 1000 * 5            // 5 seconds
)
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
