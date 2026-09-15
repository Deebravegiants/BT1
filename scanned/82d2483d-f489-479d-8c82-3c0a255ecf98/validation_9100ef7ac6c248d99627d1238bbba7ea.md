### Title
Unsynchronized concurrent map access in `WorkflowMetadataHandler.Authorize` causes a crash reachable from unauthenticated gateway HTTP-trigger requests - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
`WorkflowMetadataHandler.Authorize` reads the `h.authorizedKeys` map without holding `h.mu`, while the periodic background `syncMetadata` goroutine replaces the same map wholesale under `h.mu.Lock()`. This is the same bug class as ALPINE-CVE-2022-42334: installation/removal of a shared resource (there, pinned-cache regions; here, the authorized-key/workflow map) is not properly serialized against a lower-privileged reader, allowing a race that corrupts/crashes the process.

### Finding Description
`Authorize` is called on every incoming external HTTP trigger request (via `authorizeRequest` in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`) to validate the JWT signer against the workflow's authorized keys: [1](#0-0) 

This read (`h.authorizedKeys[workflowID]`) is performed with **no lock held**. Meanwhile, `syncMetadata`, which runs periodically in the background to refresh workflow metadata pulled/pushed from DON nodes, swaps out the entire `authorizedKeys` map (and related maps) under `h.mu.Lock()`: [2](#0-1) 

The struct declares `mu sync.RWMutex` specifically to guard these fields, and every other accessor (`syncMetadata`'s writer, and reads elsewhere in the file) is expected to take it, but `Authorize` — the one code path directly reachable by an external, unauthenticated HTTP caller — was not updated to take `h.mu.RLock()`. In Go, an unsynchronized concurrent map read racing a map write is undefined behavior and commonly manifests as a runtime `fatal error: concurrent map read and map write`, which is unrecoverable and terminates the process (not a normal panic that can be caught by `recover()`).

### Impact Explanation
Any external, unauthenticated caller sending HTTP trigger requests to the gateway can, given the periodic `syncMetadata` refresh cycle, race the map swap and force a Go runtime fatal error, crashing the gateway process. Because `HandleUserTriggerRequest` (and therefore `Authorize`) is on the network-facing request path with no privilege requirement, this is a remotely triggerable denial-of-service against the gateway component, achievable by any user submitting workflow-execute requests while metadata sync runs (which happens on a fixed interval for the lifetime of the service).

### Likelihood Explanation
`syncMetadata` runs periodically as long as the handler is started (driven by the aggregator/pull-request cycle), so the race window recurs continuously. Any client capable of sending an HTTP trigger request (does not need to be a registered/authorized workflow caller — the unauthorized case still dereferences the map before returning an error) can trigger `Authorize` concurrently with the internal sync tick. No special privilege, valid signature, or registered workflow is required to hit the racy read — an unauthenticated request for any (even non-existent) `workflowID` reaches the same unsynchronized read at line 92.

### Recommendation
Take `h.mu.RLock()`/`defer h.mu.RUnlock()` at the top of `Authorize` before reading `h.authorizedKeys`, matching the locking discipline already used by `syncMetadata`'s writer. Consider auditing other read paths in `WorkflowMetadataHandler` for the same pattern to ensure every access to `authorizedKeys`, `workflowRefToID`, `workflowIDToRef`, and `workflowShards` is consistently guarded by `h.mu`.

### Proof of Concept
1. Start a gateway with `WorkflowMetadataHandler` running (i.e., `syncMetadata` firing on its configured interval).
2. From an external, unprivileged client, continuously send `MethodWorkflowExecute` HTTP trigger requests (valid or invalid JWTs, any `workflowID`) so that `authorizeRequest` → `Authorize` is invoked at a high rate, concurrently with the metadata sync tick.
3. Run the gateway binary under `go test -race` or in production with `GORACE` detection enabled, or under sustained load, to observe `fatal error: concurrent map read and map write` originating from the unsynchronized read at `workflow_metadata_handler.go:92` racing the write at `workflow_metadata_handler.go:178`, crashing the process. [3](#0-2)

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
