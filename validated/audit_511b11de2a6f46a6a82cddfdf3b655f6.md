### Title
Data race on `authorizedKeys` map allows unsynchronized authorization check in `WorkflowMetadataHandler.Authorize` - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The AMO bug is a class of "inconsistent state check" — validating an operation against one source of truth (`stakedBalance()`) while the actual effectful operation consults a broader/different source (`stakedBalance()` + local contract balance), causing check and action to diverge. Searching the gateway/authorization code for an analogous check/act inconsistency, the closest reachable, unprivileged-client-triggerable analog is in `WorkflowMetadataHandler.Authorize`, which reads the `authorizedKeys` map without the same synchronization discipline used everywhere else that map is accessed.

### Finding Description
`WorkflowMetadataHandler` protects its authorization state (`authorizedKeys`, `workflowIDToRef`, `workflowRefToID`, `workflowShards`) with `h.mu`. Every other accessor takes the lock: `syncMetadata` takes `h.mu.Lock()` before replacing `h.authorizedKeys` [1](#0-0) , and `GetWorkflowID`/`GetWorkflowReference`/`WorkflowShards` all take `h.mu.RLock()` [2](#0-1) [3](#0-2) .

However, `Authorize`, which is the function that validates an unprivileged client's JWT-signed HTTP trigger request against the authorized signer set for a workflow, reads `h.authorizedKeys[workflowID]` directly with **no lock at all**: [4](#0-3) 

`syncMetadata` is invoked periodically on a background goroutine ticker (`h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)`), and it fully reassigns `h.authorizedKeys` under `h.mu.Lock()` [5](#0-4) . Meanwhile `Authorize` is invoked concurrently from `httpTriggerHandler.authorizeRequest` on every incoming, attacker-controlled HTTP trigger request [6](#0-5) .

This is exactly the "inconsistent check" bug class from the report: the check path (`Authorize`) reads a data structure that is concurrently mutated through a different, unsynchronized path (`syncMetadata`), so the value observed by the check can be a partially-updated/torn Go map read — undefined behavior in the Go memory model for concurrent map access without synchronization.

### Impact Explanation
Unsynchronized concurrent map access in Go is undefined behavior: a concurrent read during a map write can, at best, trigger a `fatal error: concurrent map read and map write` runtime panic (denial of service of the gateway component), and at worst return incorrect/inconsistent data (e.g. observing a half-written map yielding a false negative/positive on signer membership) since the Go runtime provides no atomicity guarantees for such races. Because `Authorize` gates whether an unauthenticated/unprivileged client's HTTP trigger request is accepted as coming from a signer registered for a given `workflowID`, an incorrect read of `keys` under race could affect authorization outcomes for that workflow, and a panic is trivially triggerable by an external client since `Authorize` runs directly in the request-handling path for every incoming HTTP trigger call.

### Likelihood Explanation
The race window is realistically exercised: `syncMetadata` runs on a fixed timer with sub-few-second/second-level periods (`MetadataAggregationIntervalMs`), and `Authorize` runs on the hot path of every incoming HTTP trigger request from any client that can reach the gateway's `MethodWorkflowExecute`/HTTP trigger endpoint [7](#0-6) . Any moderately active workflow will have overlapping reads/writes; an attacker only needs to send trigger requests, which is an unprivileged, internet-facing action.

### Recommendation
Take `h.mu.RLock()`/`h.mu.RUnlock()` around the `h.authorizedKeys[workflowID]` lookup in `Authorize`, consistent with `GetWorkflowID`, `GetWorkflowReference`, and `WorkflowShards`, so that the authorization check and the metadata-sync write path can never observe inconsistent/torn map state.

### Proof of Concept
Not independently reproducible from the index alone (requires running the Go race detector against `WorkflowMetadataHandler` under concurrent load): drive `syncMetadata()` via the periodic ticker (or call it directly in a test) on one goroutine while concurrently calling `Authorize(workflowID, token, req)` from many goroutines for the same `workflowID`; running with `go test -race` on `core/services/gateway/handlers/capabilities/v2` should flag the concurrent map read/write between `workflow_metadata_handler.go:92` (read, unlocked) and `workflow_metadata_handler.go:178` (write, locked). Due to indexing limits I could not confirm whether an existing `-race`-enabled test already exercises this exact concurrent path; a background Devin session with full repo/test access would be needed to run the race detector and confirm the panic/incorrect-read in practice.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L230-237)
```go
func (h *gatewayHandler) Methods() []string {
	return []string{
		gateway_common.MethodWorkflowExecute,
		gateway_common.MethodHTTPAction,
		gateway_common.MethodPushWorkflowMetadata,
		gateway_common.MethodPullWorkflowMetadata,
	}
}
```
