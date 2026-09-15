The claim is confirmed by direct code inspection: `Authorize()` at lines 92 and 101 reads `h.authorizedKeys` without acquiring `h.mu.RLock()`, while `syncMetadata()` reassigns `h.authorizedKeys` at line 178 under `h.mu.Lock()`. This is a genuine unsynchronized concurrent map access — `Authorize` is reachable from `HandleUserTriggerRequest`/`authorizeRequest` on every unprivileged HTTP-trigger request, and `syncMetadata` runs continuously via the ticker started in `Start()`. All sibling accessor methods (`GetWorkflowID`, `GetWorkflowReference`, `WorkflowShards`) correctly take `h.mu.RLock()`, confirming this is an inconsistency/oversight rather than intentional design.

Audit Report

## Title
Unsynchronized concurrent map access in `WorkflowMetadataHandler.Authorize()` causes crash / auth-state race on concurrent user requests - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize()` reads the `h.authorizedKeys` map without holding `h.mu`, while the periodic `syncMetadata` goroutine reassigns that same map field under `h.mu.Lock()`. Since `Authorize()` sits directly on the hot path of every unprivileged HTTP-trigger request (`HandleUserTriggerRequest` → `authorizeRequest` → `Authorize`), and `syncMetadata` runs continuously on a ticker started in `Start()`, an unprivileged remote client can trigger a data race that can crash the gateway process with `fatal error: concurrent map read and map write`.

## Finding Description
`Authorize` at [1](#0-0)  reads `h.authorizedKeys[workflowID]` (line 92) and indexes `keys[key]` (line 101) with no lock held. This method is invoked from `authorizeRequest`, which is called from `HandleUserTriggerRequest`, the gateway's entry point for unprivileged external HTTP trigger requests [2](#0-1) [3](#0-2) .

Meanwhile, `syncMetadata` builds a fresh `authorizedKeys` map and reassigns it to `h.authorizedKeys` under `h.mu.Lock()` [4](#0-3) , and this function is scheduled to run continuously via `h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)` inside `Start()` [5](#0-4) .

All other accessors of handler state correctly take the lock — `GetWorkflowID`, `GetWorkflowReference`, and `WorkflowShards` all wrap their map reads in `h.mu.RLock()`/`RUnlock()` [6](#0-5) [7](#0-6) , confirming `Authorize` is an outlier and the locking discipline was simply not applied there. There is no other synchronization mechanism (e.g., atomic pointer, sync.Map, copy-on-write with atomic swap) protecting `h.authorizedKeys`; it is a plain `map[string]map[gateway.AuthorizedKey]struct{}` field reassigned in place under a separate mutex that `Authorize` never acquires.

## Impact Explanation
Go's runtime detects concurrent unsynchronized map read/write and panics with `fatal error: concurrent map read and map write`, which is unrecoverable (bypasses `recover()`) and crashes the entire process. Since `MetadataAggregationIntervalMs` ticks are continuous and unavoidable in a running gateway, and `Authorize` is reachable by any unprivileged client that knows a valid `workflowID` (needed anyway to send a legitimate trigger request), this is a realistic, remotely triggerable denial-of-service against the gateway node, affecting all workflows it serves. This maps to an in-scope availability/DoS impact against the gateway's request-handling path.

## Likelihood Explanation
No special privileges are required beyond what any unprivileged HTTP-trigger caller already needs (a valid `workflowID` and a syntactically valid JWT-bearing request reaching `Authorize`). The race window recurs every metadata aggregation interval, so an attacker sending trigger requests at any sustained rate will periodically overlap with a `syncMetadata` cycle, making this probabilistically achievable and repeatable rather than a one-off occurrence, analogous to timing-dependent CVEs of this class.

## Recommendation
Acquire `h.mu.RLock()` / `defer h.mu.RUnlock()` at the top of `Authorize()` before reading `h.authorizedKeys`, mirroring the pattern already used in `GetWorkflowID`, `GetWorkflowReference`, and `WorkflowShards`. Only the `h.authorizedKeys` lookup needs to be brought under the lock; the JWT cache and logging calls are already independently synchronized.

## Proof of Concept
1. Construct a `WorkflowMetadataHandler` via `NewWorkflowMetadataHandler` and call `Start(ctx)` so the `syncMetadata` ticker is active; register at least one workflow with authorized keys via a simulated metadata push/aggregation cycle.
2. In one goroutine, repeatedly call `handler.Authorize(workflowID, token, req)` in a tight loop, simulating concurrent unprivileged HTTP-trigger requests.
3. In parallel, let the real ticker (or a directly invoked `handler.syncMetadata(ctx)` in a loop) repeatedly reassign `h.authorizedKeys`.
4. Run the test with `go test -race`; the race detector will report a data race between the unguarded read in `Authorize` (line 92/101) and the guarded write in `syncMetadata` (line 178). Under sustained concurrent load without the race detector, this can surface as a `fatal error: concurrent map read and map write` process crash.

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
