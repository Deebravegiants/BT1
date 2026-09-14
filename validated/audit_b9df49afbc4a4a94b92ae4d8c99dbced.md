### Title
Unsynchronized map read in `WorkflowMetadataHandler.Authorize` races with locked map write in `syncMetadata`, crashing the Gateway process - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize()` reads the shared `h.authorizedKeys` map without holding `h.mu`, while the periodic `syncMetadata()` goroutine replaces the same map wholesale under `h.mu.Lock()`. Go's runtime detects this as a concurrent map read/write and aborts the process with an unrecoverable `fatal error: concurrent map read and map write`, exactly the same bug class as the free5GC BSF advisory (unsynchronized read vs. mutex-protected write on a shared map, reachable from unprivileged/authenticated client traffic).

### Finding Description
`Authorize` is called on every incoming user HTTP-trigger request to validate the request's JWT signer against the workflow's authorized keys: [1](#0-0) 

Note line 92: `keys, exists := h.authorizedKeys[workflowID]` — this map read happens with **no `h.mu.RLock()`** call anywhere in the function, unlike every other accessor in the same struct (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`), which all correctly take `h.mu.RLock()`: [2](#0-1) [3](#0-2) 

Meanwhile, `syncMetadata()` — run periodically on a ticker (`h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)`) — replaces `h.authorizedKeys` (and the other maps) wholesale under a proper `h.mu.Lock()`: [4](#0-3) [5](#0-4) 

Because `Authorize`'s read at line 92 is unlocked while `syncMetadata`'s reassignment at line 178 (`h.authorizedKeys = authorizedKeys`) is a full map-header write under lock, any user request processed concurrently with a `syncMetadata` tick can trip Go's built-in concurrent map access detector. This is structurally identical to the free5GC BSF advisory: a `RLock()`-protected getter exists elsewhere in the type, but one particular access path bypasses the lock and races against a locked writer, and Go's `fatal error: concurrent map read and map write` is not a recoverable panic — it terminates the process outright, bypassing any Gin/HTTP-level recovery middleware.

`Authorize` is invoked from the HTTP trigger request path in `http_trigger_handler.go` (confirmed by a direct call reference), which is driven by unprivileged/authenticated end users submitting workflow-execution requests through the Gateway's public JSON-RPC surface — i.e., this is reachable from ordinary client traffic, not an operator-only or node-to-node path.

### Impact Explanation
`syncMetadata` runs on a fixed interval (`MetadataAggregationIntervalMs`, default configuration in the low tens of seconds to a minute per `ServiceConfig`), and every incoming user-triggered request calls `Authorize`. Given nontrivial request volume, this creates a recurring, deterministic window where the unlocked read in `Authorize` and the locked write in `syncMetadata` overlap. Once triggered, this kills the entire Gateway process, taking down all Gateway-served capability traffic (HTTP triggers, vault, confidential relay, capabilities handlers) until restart — a full availability loss, matching the BSF advisory's Availability-only (CVSS `S:U/C:N/I:N/A:H`)-style impact.

### Likelihood Explanation
High under any sustained request load: `Authorize` runs on the hot path for every authenticated `HandleUserTriggerRequest` call, and `syncMetadata` fires unconditionally and periodically regardless of traffic. An attacker capable of sending even a moderate stream of valid (or invalid, since the exists-check happens either way) workflow trigger requests can reliably widen the race window and hit it, similar to how the BSF PoC used high-concurrency PUTs to trigger the race deterministically.

### Recommendation
Add `h.mu.RLock()` / `defer h.mu.RUnlock()` around the `h.authorizedKeys[workflowID]` lookup in `Authorize()`, consistent with the locking discipline already used by `WorkflowShards`, `GetWorkflowID`, and `GetWorkflowReference`. Also audit any other direct field accesses inside `WorkflowMetadataHandler` methods for the same unlocked-read pattern.

### Proof of Concept
Not independently executed (no runtime/terminal access in this analysis); root cause is derived from static code inspection: `Authorize()` (line 92) is the only accessor of `h.authorizedKeys`/`h.workflowIDToRef`/`h.workflowRefToID` that omits `h.mu` locking, while `syncMetadata()` (lines 164–182) performs a full unguarded-from-`Authorize`'s-perspective replacement of the same maps under `h.mu.Lock()`. A concrete PoC would require driving concurrent `HandleUserTriggerRequest` calls (each internally invoking `Authorize`) against a running Gateway while `syncMetadata`'s ticker fires, and observing `fatal error: concurrent map read and map write` in the Gateway process logs plus process exit — directly analogous to the BSF PoC's concurrent-PUT approach, substituting concurrent HTTP-trigger requests as the unprivileged trigger vector.

### Citations

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
