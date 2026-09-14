### Title
Unsynchronized concurrent map access on `WorkflowMetadataHandler.authorizedKeys` causes race condition in JWT-based trigger authorization - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` reads the shared `h.authorizedKeys` map without acquiring `h.mu`, while the periodic `syncMetadata` goroutine writes to the very same field under `h.mu.Lock()`. This is a genuine, unprotected concurrent-map-read/write race, directly reachable from unprivileged client requests entering the gateway's HTTP trigger path.

### Finding Description
`WorkflowMetadataHandler` guards its metadata maps (`workflowShards`, `workflowRefToID`, `workflowIDToRef`) with `h.mu` in every accessor except `Authorize`: [1](#0-0) 

`Authorize` reads `h.authorizedKeys[workflowID]` at line 92 with **no lock held**.

Meanwhile, `syncMetadata` — run on a periodic ticker started in `Start()` — rebuilds the entire map set and replaces `h.authorizedKeys` under `h.mu.Lock()`: [2](#0-1) [3](#0-2) 

This is the classic Go concurrent-map race: one goroutine mutates `h.authorizedKeys = authorizedKeys` (a map-header write, which under the hood in `syncMetadata` also involves populating the new map before the swap) while another goroutine, driven by an inbound unprivileged JSON-RPC trigger request, reads the map via `Authorize`. `Authorize` is invoked directly from the client-facing trigger-authorization path: [4](#0-3) 

Every `HandleUserTriggerRequest` call — triggered by any external user sending an HTTP trigger JSON-RPC request to the gateway — calls `h.authorizeRequest`, which internally invokes `workflowMetadataHandler.Authorize(workflowID, token, req)`. Since `syncMetadata` runs on a background ticker (`MetadataAggregationIntervalMs`) concurrently with any number of inbound requests, this read/write race is reliably triggerable by simply sending trigger requests while metadata syncing is active — which happens continuously in production.

### Impact Explanation
Go's built-in `map` type is not safe for concurrent read/write; the runtime detects this and calls `fatal error: concurrent map read and map write`, crashing the entire gateway process (not a recoverable panic — Go intentionally makes this an unrecoverable fatal error). Because `Authorize` is on the hot path of every external HTTP-trigger request, an unprivileged client can deterministically induce this race merely by sending trigger requests at a rate that overlaps with the metadata-sync ticker, causing a denial of service against the gateway node. In principle a race that doesn't hit the runtime's crash detector could also yield a transiently inconsistent view of `authorizedKeys` (e.g., an in-progress map growth/rehash observed mid-mutation), risking an incorrect authorization decision, though the primary practically demonstrable impact is the fatal crash/DoS.

### Likelihood Explanation
High. `syncMetadata` runs unconditionally on a ticker as soon as the handler starts, and `Authorize` is called on every single external trigger request with no synchronization gap — no special timing, privilege, or malicious peer is required, only ordinary unprivileged use of the public HTTP-trigger endpoint concurrently with the routine background sync.

### Recommendation
Acquire `h.mu.RLock()`/`h.mu.RUnlock()` around the `h.authorizedKeys` read in `Authorize`, consistent with the locking pattern already used in `WorkflowShards`, `GetWorkflowID`, and `GetWorkflowReference`. Alternatively, since `authorizedKeys` is replaced wholesale in `syncMetadata`, consider using `atomic.Pointer[map[...]...]` for lock-free reads, or ensure the entire `authorizedKeys` map access happens under `h.mu` for both readers and writers.

### Proof of Concept
1. Start the `WorkflowMetadataHandler` (`Start()`), which schedules `syncMetadata` on a ticker via `runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)` [5](#0-4) .
2. Concurrently, from an unprivileged client, continuously send JSON-RPC HTTP trigger requests to the gateway so that `HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize` is invoked in a tight loop.
3. Run the binary with the Go race detector (`-race`) or under sustained load; the concurrent unguarded read at `authorizedKeys := ... h.authorizedKeys[workflowID]` (line 92) racing against the guarded write `h.authorizedKeys = authorizedKeys` in `syncMetadata` (line 178) will be flagged/triggered, and under production conditions (no `-race`) can surface as `fatal error: concurrent map read and map write`, crashing the gateway process.

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
