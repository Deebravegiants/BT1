### Title
HTTP Response Cache Key Omits WorkflowID, Causing Cross-Workflow Response Cache Poisoning/Confusion - (File: core/services/gateway/handlers/capabilities/v2/response_cache.go)

### Summary
The external report's bug class is: a hash/leaf used to authorize or key an action omits a discriminating identifier (`hookAddress`), so two logically distinct requests (different hooks, same encoded args) collapse to the same hash and get treated as interchangeable, enabling cross-context misuse. The chainlink analog is `OutboundHTTPRequest.Hash()` in the gateway's HTTP capability v2 response cache: the hash key omits `WorkflowID` while including `WorkflowOwner`, method, URL, headers and body — but the cache is documented as being isolated per-workflow.

### Finding Description
The gateway's HTTP trigger/action response cache stores cached HTTP responses keyed by `req.Hash()` [1](#0-0) . The README for this component explicitly states the isolation invariant that is supposed to hold: "Cache Key: Generated from workflow ID and request hash" and "Workflow Isolation: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage" [2](#0-1) .

However, the unit tests demonstrate the actual implementation contradicts that invariant: `req.Hash()` produces the **same** value for two requests that differ only in `WorkflowID`, while it does vary with `WorkflowOwner`: [3](#0-2) 
and [4](#0-3) 

This is structurally identical to the reported issue: a discriminating field that should make two logically distinct callers/contexts (here, `WorkflowID`; in the report, `hookAddress`) unaffiliated is dropped from the hash used for lookup/authorization, so requests from different workflows (belonging to the same owner) that happen to have identical method/URL/headers/body collide onto the same cache entry.

### Impact Explanation
Because the cache key does not include `WorkflowID`, if a workflow owner runs multiple distinct workflows (e.g., a shared/multi-tenant owner account, or CI/staging vs. production workflows under one owner) that issue the same outbound HTTP request shape, one workflow's cached response (including any secrets embedded in headers/body echoed back, or workflow-specific external state) can be served to a different workflow. This breaks the "Workflow Isolation" guarantee the component explicitly claims to provide, resulting in cross-workflow response confusion — an unprivileged workflow author can receive (or, if they control request shaping, poison) another one of their own workflows' cached results, or observe stale/cross-context data intended for a different execution context. This is analogous to the original bug where the missing discriminator allowed one context's authorized action to be replayed under a different, unintended context.

### Likelihood Explanation
This is reachable purely from unprivileged workflow-owner-controlled input: any workflow that uses the HTTP capability with `CacheSettings.Store = true` can trigger this path without needing any elevated privilege — the request shape (method, URL, headers, body) is fully controlled by the workflow definition. No node-operator or peer-level privilege is required; the collision is deterministic and reproducible given the confirmed test behavior, not merely theoretical.

### Recommendation
Include `WorkflowID` in `OutboundHTTPRequest.Hash()` (in addition to `WorkflowOwner`) so the cache key matches the documented isolation model, ensuring cache entries cannot be shared across distinct workflows regardless of common ownership. This mirrors the report's remedy of hashing `keccak256(abi.encode(hookAddress, hookArgs))` instead of just `hookArgs` — the fix here is to hash `(WorkflowID, WorkflowOwner, method, URL, headers, body)` instead of omitting `WorkflowID`.

### Proof of Concept
1. Two distinct workflows, `wf-A` and `wf-B`, are owned by the same `WorkflowOwner`.
2. Both issue an identical `OutboundHTTPRequest{Method, URL, MultiHeaders, Body}` (e.g., a shared external API call), with `CacheSettings.Store = true`.
3. Per the test `TestRequestHash` at [3](#0-2) , `req1.Hash() == req2.Hash()` even though `WorkflowID` differs.
4. When `wf-A`'s response is stored via `newResponseCache` under this hash [5](#0-4) , a subsequent request from `wf-B` with the identical request shape retrieves `wf-A`'s cached response instead of performing its own isolated request, violating the documented "Workflow Isolation" guarantee.

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

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L151-175)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L178-197)
```go
func TestIsExpiredOrNotCached(t *testing.T) {
	testMetrics := createCacheTestMetrics(t)
	cache := newResponseCache(logger.Test(t), 1000, testMetrics) // 1 second TTL

	req := createTestRequest("GET", "https://example.com")

	t.Run("returns true for non-existent entry", func(t *testing.T) {
		result := cache.isExpiredOrNotCached(req)
		require.True(t, result)
	})

	t.Run("returns false for non-expired entry", func(t *testing.T) {
		cache.cache[req.Hash()] = &cachedResponse{
			response: createTestResponse(200, "test"),
			storedAt: time.Now(),
		}

		result := cache.isExpiredOrNotCached(req)
		require.False(t, result)
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L65-72)
```markdown
### 3.2 Caching Behavior

- **Cacheable Responses**: 2xx (success) and 4xx (client error) status codes.
- **Cache TTL**: Configurable, default 10 minutes
- **Cache Key**: Generated from workflow ID and request hash
- **Cache Invalidation**: Time-based expiration with periodic cleanup
- **Cache Strategy**: All cacheable responses are cached; Non-zero `CacheSettings.MaxAgeMs` determines whether to return a cached value or make a fresh request
- **Workflow Isolation**: Cache entries are scoped by workflow ID to prevent cross-workflow data leakage
```
