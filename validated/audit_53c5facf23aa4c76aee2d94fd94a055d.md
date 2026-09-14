### Title
Cache-key collision in gateway HTTP action response cache omits WorkflowID, enabling cross-workflow response confusion - ([File: core/services/gateway/handlers/capabilities/v2/response_cache.go])

### Summary
The Fertilizer report's bug class is: an entity ID/cache key is derived from a subset of fields that isn't guaranteed unique, so two logically distinct records collide on the same key and one silently overwrites/serves data for the other, corrupting the state a party is entitled to. The `responseCache` used by the gateway's HTTP-action handler exhibits the same class: its cache key is `OutboundHTTPRequest.Hash()`, and the test suite for it explicitly documents that this hash does **not** include `WorkflowID`, only `WorkflowOwner` (plus method/URL/headers/body). [1](#0-0) 

### Finding Description
The `responseCache` is a map keyed by `req.Hash()`, shared across all HTTP-action requests handled by the gateway, and the README for this component explicitly claims cache entries are "scoped by workflow ID to prevent cross-workflow data leakage." [2](#0-1) 

However, the actual `Hash()` implementation used as the cache key deliberately ignores `WorkflowID` while it does vary with `WorkflowOwner`, as proven by the test cases:
- "having different workflowID results in same Hash" asserts `hash1 == hash2` for two requests differing only in `WorkflowID`. [1](#0-0) 
- "having same workflowOwner results in the same Hash" and "having different workflowOwner results in different Hash" confirm `WorkflowOwner` (not `WorkflowID`) is the isolation dimension actually used. [3](#0-2) 

The cache get/set/fetch paths (`isExpiredOrNotCached`, `Fetch`, `Set`) all key exclusively off `req.Hash()`: [4](#0-3) 

Because two different workflows belonging to the *same workflow owner* (an unprivileged client identity in this multi-tenant DON/gateway system) produce identical hashes as long as method/URL/headers/body/cache-key-relevant fields match, one workflow's cached HTTP response can be served to a completely different workflow run under the same owner. This mirrors the Fertilizer bug precisely: the identifier (`bpf+humidity+1` there, `Hash()` here) is documented/intended to be a unique-enough discriminator, but a relevant dimension (season there, `WorkflowID` here) is silently excluded from the key, letting two distinct logical entries collide and letting the newer entry silently override/serve in place of the other — an accidental "overwrite" of cached state that belongs to a different, isolated workflow execution.

### Impact Explanation
This is a cross-user/cross-workflow response confusion bug: a workflow's cached HTTP response (potentially containing owner-specific but workflow-scoped payloads, e.g., from an OAuth callback, personalized API response, or workflow-specific data fetched via the same URL/method/headers) can leak into or be served for a sibling workflow under the same owner, violating the intended workflow-level isolation the code's own documentation promises. This can cause data returned to one workflow execution to actually be the (stale, or unrelated) result computed for a different workflow, which can silently corrupt business logic/decisions made downstream by that workflow (loss-of-integrity impact analogous to the "loss of funds due to wrong lastBpf" scenario, but manifesting as wrong/stale action results propagated into an unrelated workflow's execution).

### Likelihood Explanation
Likelihood requires: (1) one workflow owner running two or more distinct workflows that both issue an `OutboundHTTPRequest` with identical `Method`/`URL`/headers/body cache-relevant fields (a realistic scenario for shared integrations or copy-pasted workflow templates), and (2) `CacheSettings.Store`/`MaxAgeMs` set such that entries are cached and read within TTL. Since `CacheSettings` fields themselves don't affect the hash (also explicitly tested), any workflow triggering the same endpoint under the same owner is naturally exposed to this collision without any adversarial action — this is a reachable, unprivileged-triggered condition, not a contrived edge case.

### Recommendation
Include `WorkflowID` (and ideally `WorkflowOwner` remains, but with `WorkflowID` as the primary/mandatory scoping key) in the `Hash()` computation used for the cache key, matching the isolation guarantee documented in the component's own README. Add regression tests asserting that different `WorkflowID`s produce different hashes (currently the test suite asserts the opposite behavior as "expected"), and audit other cache-key/dedup-key derivations in the gateway/capabilities code for the same "documented isolation vs. actual key fields" mismatch.

### Proof of Concept
1. Workflow A and Workflow B are both registered under the same `WorkflowOwner` but have different `WorkflowID`s.
2. Both workflows issue an `OutboundHTTPRequest` to the gateway with identical `Method`, `URL`, headers, and body, each with `CacheSettings.Store = true`.
3. Workflow A's request executes first; its response is stored under `req.Hash()`. Per the test at [1](#0-0) , this hash is identical to the hash Workflow B's request would compute, because `WorkflowID` is excluded.
4. Workflow B's subsequent request within the cache TTL hits `rc.Fetch`/`isExpiredOrNotCached` ( [5](#0-4) ) and is served Workflow A's cached response instead of making its own request — demonstrating cross-workflow response confusion contrary to the documented "Workflow Isolation" guarantee.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L139-149)
```go
	t.Run("having different workflowID results in same Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.WorkflowID = "workflow-123"

		req2 := createTestRequest("GET", "https://example.com")
		req2.WorkflowID = "workflow-456"

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.Equal(t, hash1, hash2, "Hash should be the same regardless of WorkflowID")
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L151-176)
```go
	t.Run("having same workflowOwner results in the same Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.WorkflowOwner = "workflow-owner-123"

		req2 := createTestRequest("GET", "https://example.com")
		req2.WorkflowOwner = "workflow-owner-123"

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.Equal(t, hash1, hash2, "Hash should be the same for identical requests")
	})

	t.Run("having different workflowOwner results in different Hash", func(t *testing.T) {
		req1 := createTestRequest("GET", "https://example.com")
		req1.WorkflowOwner = "workflow-owner-123"

		req2 := createTestRequest("GET", "https://example.com")
		req2.WorkflowOwner = "workflow-owner-456"

		hash1 := req1.Hash()
		hash2 := req2.Hash()
		require.NotEqual(t, hash1, hash2, "Hash should be different for different workflow owner")
		require.NotEmpty(t, hash1, "Hash should not be empty")
		require.NotEmpty(t, hash2, "Hash should not be empty")
	})
}
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L65-73)
```markdown
### 3.2 Caching Behavior

- **Cacheable Responses**: 2xx (success) and 4xx (client error) status codes.
- **Cache TTL**: Configurable, default 10 minutes
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
---
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L46-120)
```go
// isExpiredOrNotCached returns true if the cached response is expired or not cached.
// IMPORTANT: this method does not lock the cache map. MUST be called with cacheMu write-locked.
func (rc *responseCache) isExpiredOrNotCached(req gateway.OutboundHTTPRequest) bool {
	cachedResp, exists := rc.cache[req.Hash()]
	if !exists || time.Now().After(cachedResp.storedAt.Add(rc.ttl)) {
		return true
	}
	return false
}

// Fetch fetches a response from the cache if it exists and
// the age of cached response is less than the max age of the request.
// If the cached response is expired or not cached, it fetches a new response from the fetchFn
// and caches the response if it is cacheable and storeOnFetch is true.
//
// The mutex is only held during cache map access (microseconds), not during fetchFn execution.
// Singleflight deduplicates concurrent requests to the same cache key so only one fetchFn
// runs per key, while requests to different keys execute in parallel.
// Cache read and write happen inside the singleflight callback to ensure the key remains
// in-flight until the result is stored, preventing duplicate fetches.
func (rc *responseCache) Fetch(ctx context.Context, req gateway.OutboundHTTPRequest, fetchFn func() gateway.OutboundHTTPResponse, storeOnFetch bool) gateway.OutboundHTTPResponse {
	cacheKey := req.Hash()
	cacheMaxAge := time.Duration(req.CacheSettings.MaxAgeMs) * time.Millisecond

	// Fast path: check cache without singleflight overhead.
	rc.cacheMu.RLock()
	cachedResp, exists := rc.cache[cacheKey]
	rc.cacheMu.RUnlock()
	if exists && cachedResp.storedAt.Add(cacheMaxAge).After(time.Now()) {
		rc.metrics.IncrementCacheHitCount(ctx, rc.lggr)
		return cachedResp.response
	}

	// Slow path: singleflight deduplicates concurrent fetches per key.
	// Cache check + store happen inside the flight so the key isn't released
	// until the result is cached, closing the race window between singleflight
	// completion and cache write.
	result, _, _ := rc.flight.Do(cacheKey, func() (any, error) {
		// Re-check cache: a previous flight may have just stored the result.
		rc.cacheMu.RLock()
		cachedResp, exists := rc.cache[cacheKey]
		rc.cacheMu.RUnlock()
		if exists && cachedResp.storedAt.Add(cacheMaxAge).After(time.Now()) {
			rc.metrics.IncrementCacheHitCount(ctx, rc.lggr)
			return cachedResp.response, nil
		}

		response := fetchFn()

		if storeOnFetch && isCacheableStatusCode(response.StatusCode) {
			rc.cacheMu.Lock()
			rc.cache[cacheKey] = &cachedResponse{
				response: response,
				storedAt: time.Now(),
			}
			rc.cacheMu.Unlock()
		}

		return response, nil
	})

	return result.(gateway.OutboundHTTPResponse)
}

// Set caches a response if it is cacheable (2xx or 4xx and cache is empty or expired for the given request)
func (rc *responseCache) Set(req gateway.OutboundHTTPRequest, response gateway.OutboundHTTPResponse) {
	rc.cacheMu.Lock()
	defer rc.cacheMu.Unlock()
	if isCacheableStatusCode(response.StatusCode) && rc.isExpiredOrNotCached(req) {
		rc.cache[req.Hash()] = &cachedResponse{
			response: response,
			storedAt: time.Now(),
		}
	}
}
```
