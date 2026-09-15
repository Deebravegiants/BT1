The code confirms the claim exactly as described: `Authorize` reads `h.authorizedKeys[workflowID]` at line 92 without holding `h.mu`, while `syncMetadata` (lines 164-182) replaces `h.authorizedKeys` under `h.mu.Lock()`. All other accessors (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`) correctly use `h.mu.RLock()`, confirming `Authorize` is the outlier and this is not an intentional design choice.All facts in the claim are confirmed by the code. The exploit path is fully reachable: `HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize` reads `h.authorizedKeys` unguarded, while `syncMetadata` running on a background ticker writes to the same field under `h.mu.Lock()`. This is a genuine data race in Go, which the runtime can detect as a fatal, unrecoverable crash (`fatal error: concurrent map read and map write`), causing a denial of service reachable by any unprivileged client sending ordinary trigger requests.

Audit Report

## Title
Unsynchronized concurrent map access on `WorkflowMetadataHandler.authorizedKeys` causes race condition in JWT-based trigger authorization - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` reads `h.authorizedKeys[workflowID]` at line 92 without holding `h.mu`, while the periodic `syncMetadata` goroutine (invoked from a background ticker started in `Start()`) replaces the entire `h.authorizedKeys` map under `h.mu.Lock()` at line 178. This is an unprotected concurrent map read/write, directly reachable from any unprivileged client sending an HTTP trigger request to the gateway.

## Finding Description
Every other accessor of the handler's shared state (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`) correctly acquires `h.mu.RLock()`/`RUnlock()`, but `Authorize` does not, despite reading the same map that `syncMetadata` mutates under `h.mu.Lock()`. [1](#0-0) [2](#0-1)  The unguarded read is at [3](#0-2) , while the guarded write that reassigns the map header (a full replacement, not an in-place mutation) is at [4](#0-3) . `syncMetadata` is scheduled unconditionally on a periodic ticker from `Start()`: [5](#0-4) . `Authorize` is called from `httpTriggerHandler.authorizeRequest`, which is itself invoked on every single external `HandleUserTriggerRequest` call handling an unprivileged client's JSON-RPC trigger request: [6](#0-5) [7](#0-6) . No existing lock, wrapper, or synchronization mechanism protects the read in `Authorize`, and this is clearly an oversight relative to the locking discipline applied elsewhere in the same struct.

## Impact Explanation
This is a genuine Go concurrent-map read/write race. Under the Go race detector this is flagged immediately; under normal (non-`-race`) production binaries, if the runtime detects concurrent map read and write (which it frequently does, especially during map growth/rehash triggered by `make(map[...])` + population in `syncMetadata`), the process terminates with an unrecoverable `fatal error: concurrent map read and map write`, crashing the entire gateway node — a denial of service. This maps to an in-scope availability/DoS impact against the gateway. A less certain secondary risk is a transiently inconsistent authorization read, though the deterministic, reproducible impact is the crash.

## Likelihood Explanation
High. No special access, timing, or privilege is required. `syncMetadata` runs continuously on a fixed interval (`MetadataAggregationIntervalMs`) as soon as the handler starts, which happens in normal gateway operation, and `Authorize` is on the direct, unauthenticated hot path of every external HTTP-trigger request via `HandleUserTriggerRequest`. Ordinary, expected production traffic reliably overlaps with the sync ticker.

## Recommendation
Acquire `h.mu.RLock()`/`h.mu.RUnlock()` around the `h.authorizedKeys` lookup in `Authorize`, consistent with the pattern used in `WorkflowShards`, `GetWorkflowID`, and `GetWorkflowReference`. Alternatively, switch to `atomic.Pointer[map[...]...]` for lock-free reads since `syncMetadata` already replaces the map wholesale rather than mutating it in place.

## Proof of Concept
1. Start `WorkflowMetadataHandler` via `Start(ctx)`, which schedules `syncMetadata` on a ticker (`MetadataAggregationIntervalMs`).
2. Register at least one workflow's metadata so `syncMetadata` has non-trivial map contents to swap in on each tick.
3. Concurrently, from a test or client, repeatedly call `httpTriggerHandler.HandleUserTriggerRequest` (or send external HTTP trigger JSON-RPC requests) in a tight loop, driving repeated calls into `WorkflowMetadataHandler.Authorize`.
4. Run the test/binary with `go test -race` (or `GORACE`/`-race` build flag in production-like load testing); the race detector will report a data race between the read at `workflow_metadata_handler.go:92` and the write at `workflow_metadata_handler.go:178`, confirming the unsynchronized access described above.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L92-92)
```go
	keys, exists := h.authorizedKeys[workflowID]
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L164-178)
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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L356-376)
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

func (h *WorkflowMetadataHandler) GetWorkflowReference(workflowID string) (workflowReference, bool) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	workflowRef, exists := h.workflowIDToRef[workflowID]
	return workflowRef, exists
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-109)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}
```
