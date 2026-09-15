The claim is confirmed by direct inspection of the source code. `Authorize` reads `h.authorizedKeys[workflowID]` at line 92 with no lock acquisition, while `syncMetadata` fully replaces `h.authorizedKeys`, `h.workflowRefToID`, `h.workflowIDToRef`, and `h.workflowShards` under `h.mu.Lock()` at lines 164-182, running on a periodic ticker started in `Start()` (line 296). All sibling accessors (`GetWorkflowID`, `GetWorkflowReference`, `WorkflowShards`) correctly take `h.mu.RLock()`, confirming `Authorize` is the outlier and the omission is not an intentional design choice.

Audit Report

## Title
Unsynchronized Map Access in `WorkflowMetadataHandler.Authorize` Causes Data Race with Concurrent Metadata Sync - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` reads `h.authorizedKeys[workflowID]` without holding `h.mu`, while the periodically-running `syncMetadata` goroutine wholesale-replaces `h.authorizedKeys` (and related maps) under `h.mu.Lock()`. This is an unsynchronized concurrent map read/write in Go, which is undefined behavior and can crash the gateway process with `fatal error: concurrent map read and write`.

## Finding Description
`Authorize` is called on every unprivileged HTTP trigger request via `httpTriggerHandler.authorizeRequest` [1](#0-0) . It reads `h.authorizedKeys[workflowID]` directly at line 92 with no `h.mu.RLock()`/`RUnlock()` anywhere in the function [2](#0-1) .

Meanwhile, `syncMetadata` runs on a periodic ticker (`MetadataAggregationIntervalMs`) started unconditionally in `Start()` [3](#0-2) , and replaces `h.authorizedKeys`, `h.workflowRefToID`, `h.workflowIDToRef`, and `h.workflowShards` while holding `h.mu.Lock()` [4](#0-3) .

Every other accessor of these same fields correctly takes `h.mu.RLock()`: `GetWorkflowID` and `GetWorkflowReference` [5](#0-4) , and `WorkflowShards` [6](#0-5) . `Authorize` is the sole exception, and there is no other guard (mutex, atomic, sync.Map, or copy-on-write pattern) protecting its map access — this is a genuine, unmitigated race.

## Impact Explanation
Concurrent unsynchronized map read (in `Authorize`) and write (in `syncMetadata`, which allocates and assigns a brand-new map value to `h.authorizedKeys`) is undefined behavior in Go. In practice this reliably manifests as `fatal error: concurrent map read and write`, an unrecoverable runtime panic that crashes the entire gateway process. Since the gateway is the internet-facing endpoint authenticating HTTP trigger requests for all workflows/tenants on that instance, this constitutes a hard, unauthenticated denial-of-service against the HTTP Trigger Handler capability — an in-scope availability/DoS impact reachable via the node API authentication path.

## Likelihood Explanation
No privileged access or special timing manipulation is required beyond ordinary usage: `syncMetadata` fires unconditionally on a fixed timer once the handler starts, and `Authorize` executes on every external HTTP trigger request. Under any nontrivial request volume, the window in which `syncMetadata` reassigns the map while `Authorize` is mid-lookup will eventually be hit, making this a realistic, repeatable production condition rather than a contrived edge case.

## Recommendation
Acquire `h.mu.RLock()`/`defer h.mu.RUnlock()` at the top of `Authorize` (or around the specific reads of `h.authorizedKeys`), matching the pattern used in `GetWorkflowID`, `GetWorkflowReference`, and `WorkflowShards`. Audit the rest of `WorkflowMetadataHandler` to ensure no other method reads `authorizedKeys`, `workflowRefToID`, `workflowIDToRef`, or `workflowShards` without holding `h.mu`, and document the invariant that these fields must only be accessed under the mutex.

## Proof of Concept
1. Start a `WorkflowMetadataHandler` with at least one registered workflow so `authorizedKeys` is non-empty, with `MetadataAggregationIntervalMs` set low (e.g., 10ms) to increase race frequency in a test.
2. In a Go test built with `-race`, spawn a goroutine that repeatedly calls `syncMetadata(ctx)` (or let the ticker in `Start()` drive it), and concurrently spawn goroutines that repeatedly call `Authorize(workflowID, validJWT, req)` with a validly signed JWT for the registered workflow.
3. Run `go test -race` — the race detector will report a data race between the map read at `workflow_metadata_handler.go:92` (`Authorize`) and the map write at `workflow_metadata_handler.go:178` (`syncMetadata`). Under sustained non-instrumented load this manifests as a `fatal error: concurrent map read and write` crash of the gateway process.

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
