Audit Report

## Title
Unsynchronized concurrent map access on `authorizedKeys` in `WorkflowMetadataHandler.Authorize` causes data race / crash reachable from unprivileged gateway requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` reads `h.authorizedKeys[workflowID]` without acquiring `h.mu`, while the background `syncMetadata` goroutine periodically replaces the entire `h.authorizedKeys` map under `h.mu.Lock()`. This is an unsynchronized concurrent map read/write, which in Go can trigger `fatal error: concurrent map read and map write`, crashing the gateway process.

## Finding Description
`Authorize` is called on every inbound JSON-RPC HTTP-trigger request for this handler, and its unguarded read at [1](#0-0)  accesses `h.authorizedKeys` with no `h.mu.RLock()`, unlike the other read accessors on the same struct which correctly lock: [2](#0-1) [3](#0-2) [4](#0-3) . Meanwhile, `Start` schedules `syncMetadata` on a fixed ticker for the process lifetime [5](#0-4) , and `syncMetadata` replaces `h.authorizedKeys` (and other fields) under `h.mu.Lock()` [6](#0-5) . I verified the full file and confirmed this is the only accessor of `h.authorizedKeys` missing the lock, while every sibling accessor (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`) locks correctly. This constitutes a genuine unsynchronized concurrent map access bug — Go's race detector will flag it, and in production this class of bug (map write racing with map read) reliably produces a fatal, unrecoverable runtime error, not merely a benign data race.

## Impact Explanation
This is a real code defect independent of network conditions or attacker sophistication — a crash from a single lucky timing collision between a normal request and the internal periodic sync, not a volumetric flood. That distinguishes it from "DoS via traffic volume," which SECURITY.md explicitly excludes ("Impacts that only require DDoS," "Any denial-of-service attacks that are executed against project assets" as a prohibited *testing* activity, not necessarily an exclusion of the underlying bug class). A crash of the gateway process from ordinary request timing is a legitimate availability bug reachable by any client capable of sending HTTP-trigger requests to the gateway (no special privilege required), and gateway availability is a security-relevant, internet-facing component in this codebase.

## Likelihood Explanation
`syncMetadata` runs continuously on a fixed timer for the lifetime of the process, and `Authorize` executes on essentially every incoming request to this handler before full authorization succeeds. A moderate rate of ordinary requests is sufficient to eventually collide with a `syncMetadata` write window, and this recurs indefinitely (not a one-time race), making it practically reproducible under sustained normal load — no crafted payloads, admin access, or privileged setup are required.

## Recommendation
Add `h.mu.RLock()` / `defer h.mu.RUnlock()` around the read of `h.authorizedKeys` in `Authorize`, mirroring the pattern in `WorkflowShards`, `GetWorkflowID`, and `GetWorkflowReference`; take a local reference to the inner `map[gateway.AuthorizedKey]struct{}` while holding the lock, then release it before performing the `keys[key]` lookup (which does not itself need the lock since `keys` is a locally captured map value that is never mutated in place after being copied into `authorizedKeys` in `syncMetadata`).

## Proof of Concept
1. Instantiate a `WorkflowMetadataHandler` with a short `MetadataAggregationIntervalMs` and a shard whose aggregator periodically produces metadata so `syncMetadata` regularly reassigns `h.authorizedKeys`.
2. Call `h.Start(ctx)` to begin the `syncMetadata` ticker goroutine.
3. From a separate goroutine, repeatedly call `h.Authorize(workflowID, token, req)` in a tight loop with any workflow ID/JWT.
4. Run under `go test -race`: the race detector reports a data race between the unguarded read at line 92 (`Authorize`) and the guarded write at line 178 (`syncMetadata`). Under sustained load without `-race`, this can surface as `fatal error: concurrent map read and map write`, crashing the process.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L296-296)
```go
		h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L356-369)
```go
func (h *WorkflowMetadataHandler) GetWorkflowID(workflowOwner, workflowName, workflowTag string) (string, bool) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	workflowRef := workflowReference{
		workflowOwner: workflowOwner,
		workflowName:  workflowName,
		workflowTag:   workflowTag,
	}
	workflowID, exists := h.workflowRefToID[workflowRef]
	if !exists {
		return "", false
	}
	return workflowID, true
}
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
