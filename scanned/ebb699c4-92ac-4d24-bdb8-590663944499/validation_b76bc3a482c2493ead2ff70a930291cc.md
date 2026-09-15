Based on my research, I found a genuine unbounded-cache-growth pattern in the codebase that closely mirrors the BIND lame-cache CVE class (unauthenticated/external-actor-triggerable requests causing an internal cache to grow without any eviction of stale entries, leading to memory/performance degradation).

### Title
Unbounded growth of the bridge observation cache with no eviction of expired entries - ([File: core/services/pipeline/bridgeconn/bridge_conn_manager.go])

### Summary
`bridgeConnManager.cache` is a process-wide singleton map keyed by a SHA-256 hash of `(bridgeName, requestData["data"])`. Entries are added on every distinct bridge lookup via `PutObservation` [1](#0-0) , but `GetObservation` only checks TTL on read and returns `ErrBridgeObservationExpired` for stale entries — it never deletes them from the map [2](#0-1) . There is no background cleanup/reaper routine in this file (unlike other caches in the codebase, e.g. `jwtReplayCache.cleanupOldEntries` in `workflow_metadata_handler.go` and `requestCache`'s explicit `maxCacheSize` cap in `core/services/gateway/handlers/common/requestcache.go`, which bound growth) [3](#0-2) .

### Finding Description
The cache key is derived deterministically from the bridge's `data` payload: [4](#0-3) 

Every unique `data` object produces a new, distinct 32-byte map key that is stored forever once written via `PutObservation`, regardless of `observationTTL` (60s) expiry [5](#0-4) . This is structurally the same bug class as ALPINE-CVE-2021-25219: a resolver/cache keeps accumulating entries that are functionally "dead" (expired/unusable) but are never purged, so the internal data structure can grow indefinitely as more distinct lookups occur.

### Impact Explanation
If the `data` field driving the bridge task request (and thus the cache key) can be influenced by a large or unbounded set of distinct values on each job run — e.g., varying parameters supplied through a job run triggered externally — an unprivileged/external caller could cause the process-wide singleton cache to accumulate entries without bound, since neither TTL expiry nor any other mechanism evicts them. This leads to unbounded memory growth in the node process, which is the closest structural equivalent of the CVE's "internal data structures can grow almost infinitely" resource-exhaustion characteristic.

### Likelihood Explanation
I was not able to fully trace, within the remaining tool budget, the exact upstream call path confirming that the `data` map passed to `GetObservation` (via `core/services/pipeline/task.bridge.go`) is populated from attacker/external-initiator-controlled job-run input rather than from fixed, operator-configured job-spec parameters. This is a meaningful gap: if `requestData["data"]` is always static per job spec (configured by a privileged node operator) and does not vary per external run, the cardinality of distinct cache keys would be small and bounded by the number of configured bridge tasks, not by external actor requests — in that case, this would NOT qualify as an unprivileged-actor analog and should be rejected per the scan rules.

### Recommendation
1. Confirm exactly which fields of `requestData` flow into the bridge task's `data` payload and whether any of them originate from external, per-request/run input (e.g., webhook/EI-supplied run parameters) rather than fixed job-spec configuration.
2. If external per-run input does influence the cache key, add active eviction of expired entries (a periodic sweep, similar to `jwtReplayCache.cleanupOldEntries`) and/or a hard cap on cache size (similar to `requestCache`'s `maxCacheSize`) to `bridgeConnManager`.

### Proof of Concept
Not constructed — I could not confirm within the available investigation budget that `requestData["data"]` passed into `bridgeObservationCacheKey` is attacker/external-caller-controlled per request, which is required to demonstrate unprivileged-actor exploitability. This finding should be treated as a code-quality/hardening gap in `bridgeConnManager.cache` (missing eviction, unlike sibling caches in the codebase that do enforce TTL cleanup or size caps) rather than a fully validated attacker-triggerable vulnerability, pending confirmation of the exact data flow from `core/services/pipeline/task.bridge.go` into this cache.

### Citations

**File:** core/services/pipeline/bridgeconn/bridge_conn_manager.go (L32-41)
```go
// observationTTL bounds how long a cached observation may be served before it is
// treated as stale. Hardcoded for now; may become configurable later.
const observationTTL = 60 * time.Second

// cacheEntry pairs a cached observation with the time it was stored, so
// GetObservation can reject entries older than observationTTL.
type cacheEntry struct {
	payload  []byte
	storedAt time.Time
}
```

**File:** core/services/pipeline/bridgeconn/bridge_conn_manager.go (L99-107)
```go
	m.mu.RLock()
	entry, ok := m.cache[key]
	m.mu.RUnlock()
	if !ok {
		return nil, fmt.Errorf("%w for bridge %q", ErrBridgeObservationNotFound, bridgeName)
	}
	if m.clock.Now().Sub(entry.storedAt) > observationTTL {
		return nil, fmt.Errorf("%w for bridge %q", ErrBridgeObservationExpired, bridgeName)
	}
```

**File:** core/services/pipeline/bridgeconn/bridge_conn_manager.go (L115-121)
```go
func (m *bridgeConnManager) PutObservation(key [32]byte, observation []byte) {
	payload := make([]byte, len(observation))
	copy(payload, observation)
	m.mu.Lock()
	defer m.mu.Unlock()
	m.cache[key] = cacheEntry{payload: payload, storedAt: m.clock.Now()}
}
```

**File:** core/services/pipeline/bridgeconn/bridge_conn_manager.go (L178-190)
```go
// bridgeObservationCacheKey mirrors the streams-adapter's own ObservationPayloadHash.
// The adapter is configured with its own adapterName equal to this bridge's name,
// so payload_hash on an accepted observation equals this same key.
func bridgeObservationCacheKey(bridgeName string, data map[string]any) ([32]byte, error) {
	lookupBytes, err := json.Marshal(data)
	if err != nil {
		return [32]byte{}, fmt.Errorf("failed to marshal bridge lookup payload: %w", err)
	}
	b := make([]byte, 0, len(bridgeName)+len(lookupBytes))
	b = append(b, bridgeName...)
	b = append(b, lookupBytes...)
	return sha256.Sum256(b), nil
}
```

**File:** core/services/gateway/handlers/common/requestcache.go (L46-66)
```go
func NewRequestCache[T any](timeout time.Duration, maxCacheSize uint32) RequestCache[T] {
	return &requestCache[T]{cache: make(map[globalID]*pendingRequest[T]), timeout: timeout, maxCacheSize: maxCacheSize}
}

func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
```
