## Analog Vulnerability Found

### Title
Unsynchronized Map Access in `WorkflowMetadataHandler.Authorize` Causes Concurrent Read/Write Race With `syncMetadata` - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The reported bug class (`vestingRecipients` mutated without protecting invariants, allowing corrupted state to be read/relied upon later) has a structural analog in the gateway's `WorkflowMetadataHandler`: the `authorizedKeys` map (and related `workflowIDToRef`/`workflowShards` maps) is mutated by a background goroutine while being read from the unprivileged, internet-facing request path without proper synchronization.

### Finding Description
`WorkflowMetadataHandler.authorizedKeys` is a `map[string]map[gateway.AuthorizedKey]struct{}` protected by `h.mu sync.RWMutex` [1](#0-0) .

`syncMetadata`, run on a periodic ticker, rebuilds and swaps `h.authorizedKeys`, `h.workflowRefToID`, `h.workflowIDToRef`, and `h.workflowShards` while correctly holding `h.mu.Lock()`: [2](#0-1) 

However, `Authorize` — the function invoked on every incoming client (workflow trigger) request to authenticate/authorize the request's signer — reads `h.authorizedKeys[workflowID]` directly with **no lock held at all**: [3](#0-2) 

`Authorize` is called from the HTTP trigger handler on the unprivileged request path (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`), confirmed by the single reference to `.Authorize(` outside of tests. Since `syncMetadata` runs on its own ticker goroutine (`h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)`, [4](#0-3) ) and reassigns the entire map value under lock while `Authorize` reads it without any lock, this is a classic unsynchronized concurrent Go map access: one goroutine writing to a map (`h.authorizedKeys = authorizedKeys`) while another goroutine (triggered externally by any unprivileged client sending a workflow trigger request) reads from it concurrently.

### Impact Explanation
Concurrent unsynchronized map read/write in Go is undefined behavior and is actively detected by the Go runtime, resulting in a `fatal error: concurrent map read and map write` panic that crashes the entire gateway process — not just the goroutine. Because `Authorize` is reachable from any unprivileged client submitting a signed workflow-trigger request to the internet-facing gateway, and `syncMetadata` runs periodically and independently, this creates a remotely triggerable denial-of-service condition against the gateway: an attacker only needs to send trigger requests at a rate that increases the likelihood of racing with a `syncMetadata` cycle to reliably crash the process.

### Likelihood Explanation
The race window recurs on every `MetadataAggregationIntervalMs` tick, and `Authorize` is invoked on the hot path for every incoming client request. No special privileges, node compromise, or malicious peer behavior are required — a normal external client hitting the gateway with workflow trigger requests is sufficient to hit the race with reasonable frequency, especially under any request load.

### Recommendation
Acquire `h.mu.RLock()`/`RUnlock()` around all reads of `h.authorizedKeys` in `Authorize` (and any other unguarded reads of the shared maps), mirroring the synchronization already used in `WorkflowShards`, `GetWorkflowID`, and `GetWorkflowReference`. This should be done consistently for every field mutated in `syncMetadata`.

### Proof of Concept
1. Start a `WorkflowMetadataHandler` with a short `MetadataAggregationIntervalMs` and at least one shard.
2. In one goroutine, continuously drive `syncMetadata` (e.g., feed the aggregator observations to trigger frequent map reassignment).
3. In parallel, continuously invoke `Authorize(workflowID, token, req)` from many goroutines simulating concurrent unprivileged client requests.
4. Run with the Go race detector (`go test -race`) or under sufficient load — the process will report `fatal error: concurrent map read and map write` and crash, since `Authorize`'s `h.authorizedKeys[workflowID]` read at line 92 is not protected by `h.mu`, while `syncMetadata`'s `h.authorizedKeys = authorizedKeys` write at line 178 is protected by `h.mu.Lock()`.

*Note: I was unable to fully trace all downstream call sites of `Authorize` beyond `http_trigger_handler.go` due to index limitations; a Devin session with full repo access could confirm additional callers if any exist.*

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L38-51)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L296-296)
```go
		h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)
```
