This confirms the claim exactly matches the current code. `Authorize` reads `h.authorizedKeys[workflowID]` at line 92 with no lock acquisition, while `syncMetadata` replaces the entire map under `h.mu.Lock()` at lines 164-178. All other accessor methods (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`) correctly acquire `h.mu.RLock()` before reading shared state, confirming the omission in `Authorize` is inconsistent with the codebase's established locking convention. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

`syncMetadata` runs continuously via `h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)` inside `Start`, so the race window recurs on every aggregation interval for the lifetime of the process. [5](#0-4) 

Go maps are documented as not safe for concurrent use — one writer and any readers must be synchronized (typically via `sync.Mutex`/`sync.RWMutex`); an unsynchronized read concurrent with a write is undefined behavior and can trigger the runtime's `fatal error: concurrent map read and map write`, which is unrecoverable and crashes the process (not just the goroutine), while `Authorize` sits directly on the gateway's per-request authorization path for HTTP-triggered workflow invocations reachable by any external, unprivileged caller.

Now let me verify how `Authorize` is invoked to confirm reachability from unprivileged/external callers.Confirmed. `authorizeRequest` in `http_trigger_handler.go` directly invokes `h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)` from `HandleUserTriggerRequest`, which is the entry point for processing every incoming HTTP-trigger workflow execution request — reachable by any external, unprivileged caller of the gateway. [6](#0-5) [7](#0-6) 

Audit Report

## Title
Unsynchronized concurrent map access in workflow JWT authorization (data race enabling authorization inconsistency/crash) - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` reads `h.authorizedKeys[workflowID]` without acquiring `h.mu.RLock()`, while the periodically-running `syncMetadata` goroutine replaces the entire `authorizedKeys` map (along with `workflowRefToID`, `workflowIDToRef`, `workflowShards`) under `h.mu.Lock()`. This is a genuine unsynchronized concurrent map access: Go maps are not safe for concurrent read/write, so a reader without a lock racing a writer holding a lock is still a data race, which can cause a runtime `fatal error: concurrent map read and map write` crash or inconsistent authorization results.

## Finding Description
`Authorize` is called on every incoming trigger request via `httpTriggerHandler.authorizeRequest` → `h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)`, itself invoked from `HandleUserTriggerRequest`, the top-level entry point for processing HTTP-triggered workflow execution requests from external clients. Inside `Authorize`, the line `keys, exists := h.authorizedKeys[workflowID]` reads the map with no lock held.

Concurrently, `syncMetadata` is scheduled to run forever via `h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)` inside `Start`. It builds new maps and then does `h.mu.Lock(); ...; h.authorizedKeys = authorizedKeys; ...; h.mu.Unlock()`, fully replacing the map reference.

Every other reader of shared handler state — `WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference` — correctly wraps its map access in `h.mu.RLock()/RUnlock()`, confirming this is an inconsistency/oversight specific to `Authorize` rather than an intentional lock-free design. The locking convention used elsewhere in the same struct demonstrates the intended (and violated) invariant: all reads and writes of `authorizedKeys`, `workflowRefToID`, `workflowIDToRef`, and `workflowShards` must go through `h.mu`.

## Impact Explanation
- Availability: because Go's map implementation panics with an unrecoverable `fatal error: concurrent map read and map write` when a read races a write, an unprivileged remote client sending trigger requests while `syncMetadata` fires (which happens on every `MetadataAggregationIntervalMs` tick, indefinitely, as normal background behavior) can crash the gateway node process. This is a real DoS vector requiring no privileged access — any client able to reach the gateway's HTTP trigger endpoint qualifies.
- Correctness: in the best case (no crash), the race is still technically undefined per the Go memory model, though because `h.authorizedKeys[workflowID]` is a single read of a map header plus lookup, functional behavior deviation beyond a crash is unlikely in practice, but is not guaranteed by the language spec.

This maps most directly to a node/gateway availability (DoS) impact.

## Likelihood Explanation
`syncMetadata` runs continuously and unconditionally after `Start()` is called, and `Authorize` is on the hot path for every user-submitted trigger request — no special privilege, credential, or role is needed beyond being able to send a workflow-execute request to the gateway (with a validly-formed JWT for the target workflow, since `VerifyRequestJWT` is checked first, but that check occurs before the racy map read and doesn't require special server-side privilege to trigger the race — an attacker only needs a well-formed request hitting a workflow ID that exists at some point during the aggregation cycle). The race window recurs every aggregation interval, making it straightforward to reproduce with `go test -race` or under sustained load timed against the sync interval.

## Recommendation
Acquire `h.mu.RLock()`/`defer h.mu.RUnlock()` at the start of `Authorize` before reading `h.authorizedKeys`, consistent with `WorkflowShards`, `GetWorkflowID`, and `GetWorkflowReference`. Validate with `go test -race`, including a concurrency test exercising `Authorize` and `syncMetadata` in parallel goroutines.

## Proof of Concept
1. Construct a `WorkflowMetadataHandler` with a short `MetadataAggregationIntervalMs` and at least one workflow entry populated in `authorizedKeys`.
2. Launch one goroutine that repeatedly calls `syncMetadata(ctx)` directly (simulating the ticker) to continually replace `h.authorizedKeys`.
3. Launch multiple goroutines that repeatedly call `h.Authorize(workflowID, token, req)` for a valid signer/workflow pair.
4. Run under `go test -race`; the race detector reports a data race between the unsynchronized read at `workflow_metadata_handler.go:92` and the locked write at `workflow_metadata_handler.go:178`. Under sustained concurrent load without `-race`, this can surface as `fatal error: concurrent map read and map write`, crashing the process.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-96)
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
