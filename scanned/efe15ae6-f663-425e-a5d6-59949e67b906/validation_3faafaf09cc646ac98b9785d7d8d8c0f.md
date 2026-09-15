### Title
Unsynchronized map access allows concurrent read/write on `WorkflowMetadataHandler.authorizedKeys`, causing a crash or authorization-map corruption on the HTTP-trigger gateway path - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize`, which is invoked on every incoming JSON-RPC HTTP trigger request from an unprivileged workflow/user client, reads `h.authorizedKeys[workflowID]` without holding `h.mu`, while the periodic `syncMetadata` goroutine replaces the entire `h.authorizedKeys` map under `h.mu.Lock()`. This is a data race on a Go map that is read/written concurrently by different goroutines without a shared lock, which is the closest analog in this codebase to the CVE's use-after-free class of bug: an unsynchronized access to a shared authorization/context structure that another path frees/replaces concurrently.

### Finding Description
`Authorize` is called from `HTTPCapabilityHandler`/`HTTPTriggerHandler` for every incoming JSON-RPC trigger request (`http_trigger_handler.go` calls `metadataHandler.Authorize`), which is directly reachable from an unauthenticated/unprivileged network client hitting the gateway's HTTP trigger capability. Inside `Authorize`: [1](#0-0) 

the code reads `h.authorizedKeys[workflowID]` at line 92 with no lock held at all (`h.mu` is never acquired in this function).

Meanwhile, `syncMetadata`, which runs periodically on a background ticker (`h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)` in `Start`), builds an entirely new `authorizedKeys` map and swaps it into `h.authorizedKeys` while holding `h.mu.Lock()`: [2](#0-1) 

Because `Authorize` never takes `h.mu.RLock()`, a client-triggered request that races with the periodic `syncMetadata` swap performs an unsynchronized concurrent read of a Go map while another goroutine writes to the field holding it. In Go, concurrent unsynchronized map access (even a "map variable reassignment" versus a raw read of the old/new map header) is undefined behavior that the runtime's race detector flags and that can manifest as `fatal error: concurrent map read and map write`, crashing the whole node process — a remote, unprivileged, client-triggerable denial of service. It also opens a window where a workflow-ID-to-authorized-key lookup can be evaluated against a map that is being torn down/rebuilt concurrently, risking incorrect authorization decisions if the runtime doesn't fatal immediately.

This mirrors the root cause pattern of CVE-2020-36385: a structure reachable via a shared registry/list (there: `ctx_list`; here: `h.authorizedKeys`) is accessed by one path without the synchronization that another path (context/entry teardown or, here, periodic metadata resync) requires, leading to unsafe concurrent access to a data structure that is being freed/replaced.

Other accessors in the same struct (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`) correctly take `h.mu.RLock()`; `Authorize` is the outlier that skips locking entirely.

### Impact Explanation
This is remotely triggerable by any unprivileged client sending JSON-RPC HTTP trigger requests to the gateway — no special privileges are required beyond making a normal-looking (even invalidly signed) trigger request, since `Authorize` is called before the request is otherwise validated. The most likely and severe outcome is a runtime `fatal error: concurrent map read and map write` panic that crashes the gateway process (availability impact, matching the CVSS `A:H` in the analog). A secondary, harder-to-prove risk is transient authorization inconsistency during the race window.

### Likelihood Explanation
`syncMetadata` runs on a periodic ticker configured via `MetadataAggregationIntervalMs` (default 1 minute), and `Authorize` is invoked on the hot path of every incoming trigger request, so the race window opens repeatedly and is easy to hit under any sustained request volume — no special timing manipulation is needed by the attacker beyond issuing requests continuously.

### Recommendation
Acquire `h.mu.RLock()`/`defer h.mu.RUnlock()` at the top of `Authorize` before reading `h.authorizedKeys`, consistent with the other read accessors (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`) in the same file.

### Proof of Concept
1. Start the gateway with a short `MetadataAggregationIntervalMs` and register at least one workflow so `authorizedKeys` is populated.
2. Continuously send valid-shaped JSON-RPC HTTP trigger requests (with any signed JWT, valid or not) to the gateway so `Authorize` is invoked in a tight loop from many goroutines.
3. Run the gateway binary/tests with `-race` (Go race detector) enabled while `syncMetadata`'s ticker fires concurrently with the incoming request goroutines.
4. Observe the race detector reporting a concurrent read/write on `h.authorizedKeys` between `Authorize` (workflow_metadata_handler.go:92) and `syncMetadata` (workflow_metadata_handler.go:178), or, without the race detector, observe an eventual `fatal error: concurrent map read and map write` crash under sustained load.

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
