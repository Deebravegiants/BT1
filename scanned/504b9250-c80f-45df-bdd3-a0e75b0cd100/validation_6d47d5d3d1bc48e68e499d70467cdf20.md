Confirmed: `authorizeRequest` (called on every unauthenticated user HTTP-trigger request) reaches `WorkflowMetadataHandler.Authorize`, which reads `h.authorizedKeys[workflowID]` without holding `h.mu`, while the periodic `syncMetadata` goroutine reassigns the whole map under `h.mu.Lock()`. This is the same bug class as the Mailpit advisory — an unsynchronized map read racing a synchronized map write, reachable from unprivileged/unauthenticated remote requests via the gateway. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Concurrent map read/write in `WorkflowMetadataHandler.Authorize` causes remote unauthenticated Gateway crash - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` reads the `authorizedKeys` map without holding `h.mu`, while the periodic `syncMetadata` background goroutine replaces that same map under `h.mu.Lock()`. A remote, unauthenticated user submitting HTTP trigger requests to the Gateway can race this unlocked read against the periodic metadata sync writer and trigger Go's `fatal error: concurrent map read and map write`, crashing the entire Gateway process — an unrecoverable panic that also brings down handling for all other DONs/workflows served by that Gateway instance.

### Finding Description
`WorkflowMetadataHandler` stores authorization state in `authorizedKeys map[string]map[gateway.AuthorizedKey]struct{}`, guarded (in principle) by `h.mu sync.RWMutex` [4](#0-3) .

The `Authorize` method, however, accesses `h.authorizedKeys[workflowID]` and iterates the inner map without acquiring `h.mu.RLock()`:
```go
keys, exists := h.authorizedKeys[workflowID]
...
if _, exists = keys[key]; !exists { ... }
``` [5](#0-4) 

Meanwhile, `syncMetadata` — invoked every `MetadataAggregationIntervalMs` (default 1 minute) via `h.runTicker(...)` started in `Start()` — builds a brand-new `authorizedKeys` map and swaps it in wholesale while holding `h.mu.Lock()`:
```go
h.mu.Lock()
defer h.mu.Unlock()
...
h.authorizedKeys = authorizedKeys
``` [2](#0-1) [6](#0-5) 

`Authorize` is called from `httpTriggerHandler.authorizeRequest`, which is reached from `HandleUserTriggerRequest` — the entry point for every incoming (unauthenticated at the transport layer; auth is exactly what's being computed) HTTP trigger request submitted by external clients to the Gateway:
```go
key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
``` [3](#0-2) [7](#0-6) 

This exactly mirrors the Mailpit root cause: an unlocked map read on the hot request path racing a lock-protected periodic writer/replacer. Because Go's map implementation sets an internal `hashWriting` flag during writes, a concurrent unlocked read hits `runtime.throw("concurrent map read and map write")`, which is not caught by any `defer/recover` (including whatever panic-recovery wraps the gateway's JSON-RPC/HTTP handler stack) — it terminates the process.

### Impact Explanation
A successful trigger crashes the entire Gateway process, taking down JSON-RPC handling for every DON/shard/workflow it serves — not just the targeted workflow. This is a full denial-of-service against the CRE Gateway's HTTP-trigger capability, reachable by any external caller who knows (or brute-forces) a valid `workflowID`/trigger endpoint, without needing valid JWT authorization (the crash occurs during the authorization lookup itself, before/independent of whether the JWT verifies).

### Likelihood Explanation
Likelihood is bounded by timing: the attacker needs their unlocked read in `Authorize` to overlap with the ~once-per-minute (`MetadataAggregationIntervalMs`, default 60000ms) `syncMetadata` write window. Since `syncMetadata` swaps the whole map (not just mutating entries) every cycle regardless of whether anything changed, an attacker can simply flood `HandleUserTriggerRequest` with concurrent requests continuously; eventually a read will land during the map-swap write, similar to the PoC pattern in the Mailpit advisory (hundreds of concurrent requests repeated over many rounds).

### Recommendation
Acquire `h.mu.RLock()`/`RUnlock()` around the `authorizedKeys` map read in `Authorize` (and any other unguarded reads of `authorizedKeys`, `workflowIDToRef`, `workflowRefToID`, `workflowShards` outside the methods that already lock, such as `aggForNode`'s access to `h.nodeAddrToShard` and `h.aggs`, which should also be audited for consistent locking). Ensure every access to these package-level shared maps — including from `syncMetadata`, `Authorize`, and any future exported accessors — goes through `h.mu`.

### Proof of Concept
1. Deploy a Gateway with an active DON registration such that `authorizedKeys` is periodically repopulated by `syncMetadata` (default every 60s).
2. From an external, unauthenticated client, continuously send `HandleUserTriggerRequest`-style JSON-RPC requests (`gateway_common.MethodWorkflowExecute`) referencing a valid `workflowID`, with high concurrency (hundreds of goroutines/connections), for several minutes so that many requests' `Authorize` calls fall exactly on `syncMetadata`'s lock-window boundary.
3. When an unlocked read in `Authorize` (`h.authorizedKeys[workflowID]`) coincides with `syncMetadata`'s `h.authorizedKeys = authorizedKeys` write, the Go runtime raises `fatal error: concurrent map read and map write`, crashing the Gateway process. Running with `-race` reproduces this deterministically as a `WARNING: DATA RACE` at `workflow_metadata_handler.go:92` vs `workflow_metadata_handler.go:178`.

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-104)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
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

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
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
