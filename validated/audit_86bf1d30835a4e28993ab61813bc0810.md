This confirms the claim exactly as described. `Authorize` at line 92 reads `h.authorizedKeys[workflowID]` with no lock acquisition, while `WorkflowShards` (line 271-278) and `GetWorkflowReference` (line 371-376) both correctly use `h.mu.RLock()`/`RUnlock()` before reading the same struct's maps. `syncMetadata` reassigns these maps under `h.mu.Lock()` (line 164-182), running periodically via `runTicker` on a separate goroutine (line 296) independent from the goroutine(s) invoking `Authorize` per-request. This is a genuine, unsynchronized concurrent map read/write in Go, which is undefined behavior and can panic with `fatal error: concurrent map read and map write`.

Audit Report

## Title
Unsynchronized read of `authorizedKeys` map in `WorkflowMetadataHandler.Authorize` races with concurrent `syncMetadata` writes - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` reads `h.authorizedKeys[workflowID]` without acquiring `h.mu`, while `syncMetadata` — running on an independent periodic ticker goroutine — reassigns `h.authorizedKeys` (along with `workflowRefToID`, `workflowIDToRef`, `workflowShards`) under `h.mu.Lock()`. This is an unsynchronized concurrent map read/write, which is undefined behavior in Go and can crash the process with `fatal error: concurrent map read and map write`.

## Finding Description
The struct declares `mu sync.RWMutex` specifically to guard the metadata maps [1](#0-0) . Other accessor methods on the same struct, such as `WorkflowShards` and `GetWorkflowReference`, correctly take `h.mu.RLock()` before reading these maps [2](#0-1) [3](#0-2) . However, `Authorize` reads `h.authorizedKeys[workflowID]` directly with no lock [4](#0-3) , while `syncMetadata` reassigns the whole map (and related maps) under `h.mu.Lock()` [5](#0-4) . `syncMetadata` is scheduled on its own periodic goroutine via `runTicker` in `Start` [6](#0-5) , independent of the request-handling goroutine(s) that invoke `Authorize` per incoming HTTP-trigger request. Since Go maps are not safe for concurrent read/write, this violates the mutual-exclusion invariant the mutex is meant to enforce, and the inconsistency (some accessors lock, `Authorize` does not) confirms this is an oversight rather than an intentional lock-free design.

## Impact Explanation
This is a genuine data race reachable by any unprivileged client sending HTTP-trigger requests to the gateway, since `Authorize` is invoked per inbound request to validate the JWT signer against the workflow's authorized keys. The race does not enable an authorization bypass (the map is only read by the attacker path, and its raw contents aren't attacker-controlled), but concurrent unsynchronized Go map access is undefined behavior that can panic the process with `fatal error: concurrent map read and map write`, causing a denial-of-service on the gateway's HTTP-trigger capability path. This maps to an availability impact on an internet-facing component, which is a legitimate (if lower-severity) finding class.

## Likelihood Explanation
The race window opens on every `syncMetadata` tick (governed by `MetadataAggregationIntervalMs`), during which `h.mu.Lock()` briefly holds the mutex while swapping in new maps. Any concurrent unprivileged trigger request executing `Authorize` at that exact moment reads the map without the lock, so the race is real but narrow, occurring under sustained request throughput and requiring precise timing to actually crash the process (as opposed to merely being flagged by Go's race detector). This is a plausible, low-effort-to-trigger race, especially under load or with `-race` instrumentation, but requires no special privileges — only enough external request volume to overlap with a sync tick.

## Recommendation
Take `h.mu.RLock()` / `defer h.mu.RUnlock()` at the top of `Authorize` around the read of `h.authorizedKeys[workflowID]`, consistent with the locking pattern already used in `WorkflowShards` and `GetWorkflowReference`. Audit for any other direct field accesses on `authorizedKeys`, `workflowIDToRef`, `workflowRefToID`, or `workflowShards` outside of `syncMetadata` that bypass `h.mu`. Add a `go test -race` regression test that concurrently calls `Authorize` and `syncMetadata` to catch regressions.

## Proof of Concept
1. Construct a `WorkflowMetadataHandler` and populate `h.authorizedKeys` for a workflow ID via a call path equivalent to `syncMetadata`.
2. Launch one goroutine that repeatedly calls `syncMetadata(ctx)` in a tight loop (simulating the periodic ticker).
3. Launch a second goroutine that repeatedly calls `Authorize(workflowID, token, req)` for the same workflow ID with a validly-signed JWT.
4. Run under `go test -race`; the race detector will flag the concurrent read (line 92, unlocked) against the concurrent write (line 178, under `h.mu.Lock()`) as a data race. Under sufficient timing pressure without `-race`, this can manifest as `fatal error: concurrent map read and map write`.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L36-54)
```go
type WorkflowMetadataHandler struct {
	services.StateMachine
	lggr            logger.Logger
	mu              sync.RWMutex
	authorizedKeys  map[string]map[gateway.AuthorizedKey]struct{} // map of workflow ID to authorized keys
	workflowRefToID map[workflowReference]string                  // map of workflow reference to workflow ID
	workflowIDToRef map[string]workflowReference                  // map of workflow ID to workflow reference
	workflowShards  map[string][]*shardEndpoint                   // map of workflow ID to the shards it is assigned to (quorum reached)
	// aggs holds one WorkflowMetadataAggregator per shard, keyed by shard donID.
	aggs            map[string]*aggregation.WorkflowMetadataAggregator
	shards          []*shardEndpoint
	nodeAddrToShard map[string]*shardEndpoint
	config          ServiceConfig
	stopCh          services.StopChan
	metrics         *metrics.Metrics
	jwtCache        *jwtReplayCache // JWT replay protection cache
	wg              sync.WaitGroup
	startTime       time.Time // time when Start() was called
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L92-92)
```go
	keys, exists := h.authorizedKeys[workflowID]
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L164-182)
```go
	h.mu.Lock()
	defer h.mu.Unlock()

	if len(h.workflowIDToRef) == 0 && len(workflowIDToRef) > 0 {
		latencyMs := time.Since(h.startTime).Milliseconds()
		h.metrics.RecordMetadataSyncStartupLatency(ctx, latencyMs, h.lggr)
	}
	// Log all registered workflow IDs
	workflowIDs := make([]string, 0, len(workflowIDToRef))
	for workflowID := range workflowIDToRef {
		workflowIDs = append(workflowIDs, workflowID)
	}
	h.lggr.Debugw("Synced workflow metadata", "workflowIDs", workflowIDs, "count", len(workflowIDs))

	h.authorizedKeys = authorizedKeys
	h.workflowRefToID = workflowRefToID
	h.workflowIDToRef = workflowIDToRef
	h.workflowShards = workflowShards
	h.metrics.RecordLoadedMetadataSize(ctx, int64(len(h.workflowIDToRef)), h.lggr)
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L271-278)
```go
func (h *WorkflowMetadataHandler) WorkflowShards(workflowID string) []*shardEndpoint {
	h.mu.RLock()
	defer h.mu.RUnlock()
	shards := h.workflowShards[workflowID]
	out := make([]*shardEndpoint, len(shards))
	copy(out, shards)
	return out
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L290-296)
```go
		h.runTicker(time.Duration(h.config.MetadataPullIntervalMs)*time.Millisecond, func(ctx context.Context) {
			err2 := h.sendMetadataPullRequest()
			if err2 != nil {
				h.lggr.Errorw("Failed to send pull request", "error", err2)
			}
		})
		h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L371-376)
```go
func (h *WorkflowMetadataHandler) GetWorkflowReference(workflowID string) (workflowReference, bool) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	workflowRef, exists := h.workflowIDToRef[workflowID]
	return workflowRef, exists
}
```
