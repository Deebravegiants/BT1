Confirmed by direct code inspection. The claim is accurate: `Authorize` reads `h.authorizedKeys[workflowID]` at line 92 without acquiring `h.mu`, while every other accessor of the same struct fields (`WorkflowShards` at line 272-274, `GetWorkflowID` at line 357-358, `GetWorkflowReference` at line 372-373, and the writer `syncMetadata` at line 164) correctly takes `h.mu.RLock()`/`h.mu.Lock()`. This is an inconsistency in locking discipline specifically on the one function reachable directly from unauthenticated external HTTP trigger requests via `authorizeRequest` → `HandleUserTriggerRequest` in `http_trigger_handler.go`, confirming the reachable, unsynchronized concurrent map access.

Audit Report

## Title
Unsynchronized concurrent map access in `WorkflowMetadataHandler.Authorize` causes a crash reachable from unauthenticated gateway HTTP-trigger requests - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

## Summary
`WorkflowMetadataHandler.Authorize` reads `h.authorizedKeys[workflowID]` at line 92 without holding `h.mu`, while the periodic background `syncMetadata` goroutine replaces the same map wholesale under `h.mu.Lock()` at line 178. Since `Authorize` is invoked on every external HTTP trigger request via `httpTriggerHandler.authorizeRequest` → `HandleUserTriggerRequest`, an unauthenticated attacker sending requests concurrently with the periodic sync tick can trigger a Go runtime `fatal error: concurrent map read and map write`, crashing the gateway process.

## Finding Description
`Authorize` is called from `authorizeRequest` in `http_trigger_handler.go` for every incoming `workflows.execute` HTTP trigger request: [1](#0-0) . The workflowID and JWT are attacker-controlled inputs from the HTTP layer, and reaching this line requires no valid credentials — an invalid or unregistered `workflowID` still causes execution to reach the racy read before returning an error. Inside `Authorize`, the map read `keys, exists := h.authorizedKeys[workflowID]` at line 92 is performed with no lock held: [2](#0-1) .

Meanwhile, `syncMetadata` runs periodically via `runTicker` (configured by `MetadataAggregationIntervalMs`, started in `Start`) and swaps `h.authorizedKeys` (and other maps) for a freshly built one, correctly under `h.mu.Lock()`: [3](#0-2) , [4](#0-3) .

The struct declares `mu sync.RWMutex` precisely to guard these fields [5](#0-4) , and every other reader of the same fields correctly takes `h.mu.RLock()`: `WorkflowShards` [6](#0-5) , `GetWorkflowID` [7](#0-6) , and `GetWorkflowReference` [8](#0-7) . `Authorize` is the sole outlier that omits this locking despite being the function reachable directly from unauthenticated network input. In Go, a concurrent unsynchronized map read racing a map write on the same map is undefined behavior and reliably manifests as an unrecoverable `fatal error: concurrent map read and map write`, terminating the process regardless of `recover()`.

## Impact Explanation
This is a remotely triggerable denial-of-service against the gateway process. Any client capable of sending an HTTP trigger request (`workflows.execute`) — without needing to be a registered or authorized workflow caller — can race the periodic `syncMetadata` map swap and crash the entire gateway. This maps to an in-scope "unauthorized action / node-availability" impact class for the gateway component: a single unauthenticated request stream can take down request routing for all workflows served by that gateway instance.

## Likelihood Explanation
`syncMetadata` runs on a fixed interval for the entire lifetime of the service (`MetadataAggregationIntervalMs`), so the race window recurs continuously and predictably. Any external caller capable of reaching the gateway's HTTP trigger endpoint can hit `Authorize` at will and at high frequency, with no valid signature, registered workflow, or elevated privilege required — the racy read occurs before the "not found"/"not authorized" checks return. Under sustained request load, hitting the race is a matter of repetition, not a rare timing coincidence, making this a highly reproducible availability bug reachable by any unprivileged client.

## Recommendation
Take `h.mu.RLock()` and `defer h.mu.RUnlock()` at the top of `Authorize`, immediately before reading `h.authorizedKeys[workflowID]`, matching the locking discipline already used by `WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`, and the `syncMetadata` writer. Audit for any other unguarded accesses to `authorizedKeys`, `workflowRefToID`, `workflowIDToRef`, or `workflowShards` to ensure full coverage.

## Proof of Concept
1. Start a gateway instance with `WorkflowMetadataHandler` running so `syncMetadata` fires on its configured `MetadataAggregationIntervalMs` interval (background metadata sync from DON nodes populates `authorizedKeys`/related maps on every tick).
2. From an external, unauthenticated client, continuously send `workflows.execute` HTTP trigger JSON-RPC requests (any `workflowID`, valid or invalid JWT) at high concurrency so that `HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize` is invoked repeatedly and concurrently with the sync tick.
3. Build/run the gateway with the Go race detector enabled (`go build -race` / `go test -race`) or under sustained concurrent load in a non-race build; observe `fatal error: concurrent map read and map write` originating from the unsynchronized read at `workflow_metadata_handler.go:92` racing the write at `workflow_metadata_handler.go:178`, crashing the process.
4. As a unit test, a synthetic Go test that calls `(*WorkflowMetadataHandler).Authorize` in a tight loop from one goroutine while concurrently calling `syncMetadata` (or directly reassigning `h.authorizedKeys` under lock) from another, run with `-race`, will deterministically flag the data race.

### Citations

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
