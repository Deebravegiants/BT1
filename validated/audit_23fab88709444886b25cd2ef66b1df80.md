The claim confirms exactly what's in the code: `Authorize` at line 92 reads `h.authorizedKeys[workflowID]` without acquiring `h.mu.RLock()`, while `syncMetadata` replaces `h.authorizedKeys` under `h.mu.Lock()` at lines 164-178. All other accessors (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`) correctly use `h.mu.RLock()`. Let me confirm the call path from `http_trigger_handler.go`.I've confirmed the full exploit path and code. The claim is technically accurate on all points.

Confirmed facts:
- `Authorize` reads `h.authorizedKeys[workflowID]` at line 92 with no lock held. [1](#0-0) 
- `syncMetadata` replaces `h.authorizedKeys` (and other maps) under `h.mu.Lock()`. [2](#0-1) 
- `syncMetadata` is run on a periodic ticker in `Start`. [3](#0-2) 
- Other accessors (`WorkflowShards`, `GetWorkflowID`, `GetWorkflowReference`) correctly acquire `h.mu.RLock()`. [4](#0-3) [5](#0-4) 
- The call path is confirmed: `HandleUserTriggerRequest` → `authorizeRequest` → `h.workflowMetadataHandler.Authorize(...)`, reachable from any unprivileged JSON-RPC trigger request against the gateway. [6](#0-5) 

This is a genuine, unsynchronized concurrent-map-access bug: an attacker sending trigger requests concurrently with the periodic `syncMetadata` tick can race `Authorize`'s unguarded read against the mutex-protected write/replacement of `h.authorizedKeys`, which in Go's runtime is detectable by the race detector and, if actually raced hard enough by the runtime's internal map-access checks, can crash the process with `fatal error: concurrent map read and map write` — an unauthenticated remote DoS against the gateway node. No existing lock, wrapper, or defensive copy protects this specific read; it's a clear omission relative to the pattern used by every sibling accessor.

Audit Report

## Title
Unsynchronized concurrent read of `authorizedKeys` map in `WorkflowMetadataHandler.Authorize` races with periodic `syncMetadata` writes - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize`, which is invoked on every unprivileged HTTP-trigger request via `httpTriggerHandler.authorizeRequest`, reads `h.authorizedKeys[workflowID]` without acquiring `h.mu.RLock()`. Concurrently, the background `syncMetadata` goroutine, run on a fixed ticker interval, replaces `h.authorizedKeys` (and related maps) under `h.mu.Lock()`. This is a classic unsynchronized concurrent Go map read/write, which Go's runtime treats as undefined behavior and can crash the process (`fatal error: concurrent map read and map write`), or in weaker cases yield an inconsistent authorization decision.

## Finding Description
`Authorize` reads the shared map directly at line 92 without any lock: [7](#0-6) 

`syncMetadata` swaps in a brand-new map for `h.authorizedKeys` while holding `h.mu.Lock()`: [2](#0-1) 

The ticker driving `syncMetadata` is registered unconditionally in `Start`: [8](#0-7) 

By contrast, every other reader of the same handler state correctly takes `h.mu.RLock()`: [4](#0-3) [5](#0-4) 

The reachable call path from an unprivileged trigger request is: `httpTriggerHandler.HandleUserTriggerRequest` → `authorizeRequest` → `h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)`: [9](#0-8) [6](#0-5) 

No existing check mitigates this: JWT verification and replay protection inside `Authorize` operate independently of the map race and do not synchronize access to `h.authorizedKeys`.

## Impact Explanation
An unauthenticated remote attacker who can send HTTP trigger requests to a gateway node can, purely by request timing relative to the fixed `MetadataAggregationIntervalMs` ticker, race the unsynchronized read in `Authorize` against the locked write in `syncMetadata`. This is a data race on a Go map, which is undefined behavior; under Go's runtime map-access instrumentation this reliably surfaces as `fatal error: concurrent map read and map write`, crashing the gateway node process. This is a remote, unauthenticated denial-of-service against gateway availability.

## Likelihood Explanation
High. The attacker needs no credentials beyond the ability to send trigger requests (the documented unprivileged path). The racing writer (`syncMetadata`) executes on every gateway node automatically at a fixed period once `Start` is called, requiring no attacker action to trigger the write side. Sustained trigger traffic during any sync window will eventually collide with the map replacement.

## Recommendation
Acquire `h.mu.RLock()`/`RUnlock()` in `Authorize` around the read of `h.authorizedKeys[workflowID]` and the subsequent `keys[key]` lookup, matching the pattern already used in `WorkflowShards`, `GetWorkflowID`, and `GetWorkflowReference`. To minimize lock hold time, copy out just the per-workflow key set under the lock before performing signature/lookup logic outside it.

## Proof of Concept
1. Construct a `WorkflowMetadataHandler` and call `Start(ctx)` so the `syncMetadata` ticker begins running per `MetadataAggregationIntervalMs`.
2. Populate `h.authorizedKeys` for a workflow (as in `TestSyncMetadata`/`TestWorkflowMetadataHandler_Authorize`).
3. From one goroutine, tightly loop calling `handler.Authorize(workflowID, validJWT, req)`.
4. From another goroutine, tightly loop calling `handler.syncMetadata(ctx)` (or let the real ticker fire at a short interval for the test).
5. Run with `go test -race`: the race detector will flag the concurrent read at line 92 versus the locked write at lines 164-178; under load without `-race`, this can crash the process with `fatal error: concurrent map read and map write`.

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
