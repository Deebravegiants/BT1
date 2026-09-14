### Title
Unsynchronized read of `WorkflowMetadataHandler.authorizedKeys`/`workflowIDToRef` races with concurrent `syncMetadata` writes - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The prysm fix addressed a race where a mutable "current host" field was read and written from different goroutines (fallback host switching) without atomic/synchronized access. The closest analogous pattern found in this codebase is `WorkflowMetadataHandler.Authorize`, which reads the `authorizedKeys` map (and, transitively, `workflowIDToRef`/`workflowShards` in call sites) directly without taking `h.mu`, while `syncMetadata` periodically re-assigns these same maps under `h.mu.Lock()`.

### Finding Description
`WorkflowMetadataHandler` guards its metadata maps with `mu sync.RWMutex`: [1](#0-0) 

`syncMetadata` reassigns `h.authorizedKeys`, `h.workflowRefToID`, `h.workflowIDToRef`, and `h.workflowShards` while correctly holding `h.mu.Lock()`: [2](#0-1) 

However, `Authorize` — which is invoked per incoming, unprivileged HTTP-trigger request to verify a workflow's signer against the authorized-key set — reads `h.authorizedKeys[workflowID]` with no lock at all: [3](#0-2) 

`syncMetadata` runs on a periodic timer/goroutine (metadata sync loop) independent of the goroutine(s) handling inbound trigger requests that call `Authorize`. Since Go maps are not safe for concurrent read/write, a request arriving while a sync cycle is rebuilding these maps can:
- crash the process with "fatal error: concurrent map read and map write" (the Go runtime's race detector/map implementation explicitly panics on this), or
- under `-race`, be flagged as a genuine data race, exactly the class of bug the cited prysm PR fixes (non-atomic RW of a field that gets swapped by a concurrent "switch" operation).

### Impact Explanation
This is a reachable, unprivileged-triggered condition: any external caller sending HTTP trigger requests to the gateway can race with the internal periodic metadata sync. In the best case this only crashes the gateway handler goroutine's request path (denial of service on the trigger-handling capability); in degenerate cases concurrent unsynchronized map access in Go can corrupt runtime map internals leading to a process-wide crash, i.e., availability impact on the internet-facing HTTP-trigger gateway path. It does not, on inspection, provide a way to bypass authorization (the map is read, not maliciously written by the attacker), so this should be scoped as a race/availability bug rather than an authentication bypass.

### Likelihood Explanation
Likelihood depends on sync frequency vs. request rate. Given the metadata pull/aggregation intervals used elsewhere in this same file (pull/aggregation on the order of tens of seconds/minutes) and per-request concurrent invocation of `Authorize` from the gateway's message-handling goroutines, the race window is narrow but not negligible under sustained request load, especially once many workflows are registered (larger map rebuild = longer write window). This is analogous to the prysm bug, which was also a narrow-but-real race exposed by `-race` testing under host-switch/fallback pressure.

### Recommendation
Take `h.mu.RLock()`/`RUnlock()` around the map reads in `Authorize` (and any other unguarded direct field accesses on `authorizedKeys`, `workflowIDToRef`, `workflowRefToID`, `workflowShards` outside of `syncMetadata`), mirroring the locking already used by `syncMetadata`. Add a `-race` regression test that exercises `Authorize` concurrently with `syncMetadata`, similar to the `TestHandler_ConcurrentHostSwitch` test referenced in the source report.

### Proof of Concept
1. Start `WorkflowMetadataHandler` and register a workflow via `syncMetadata` on a periodic goroutine (as done in production wiring).
2. Concurrently, from a second goroutine, repeatedly call `Authorize(workflowID, token, req)` for the same or different workflow IDs while the sync goroutine rewrites `h.authorizedKeys` under lock.
3. Run with `go test -race` — the unsynchronized read in `Authorize` against the concurrently-reassigned map triggers a detected data race (and, without `-race`, can trigger `fatal error: concurrent map read and map write` under sufficiently tight timing), demonstrating the same RW-race bug class fixed upstream in the cited prysm commit.

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
