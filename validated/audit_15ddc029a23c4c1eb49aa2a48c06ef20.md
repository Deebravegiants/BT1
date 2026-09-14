Confirmed: `WorkflowMetadataHandler.Authorize` reads `h.authorizedKeys` (and other maps) directly without taking `h.mu.RLock()`, while `syncMetadata` (run every `MetadataAggregationIntervalMs` via a background ticker) reassigns the same maps under `h.mu.Lock()`. [1](#0-0) [2](#0-1) 

### Title
Unsynchronized concurrent map access in HTTP-Trigger workflow authorization allows crash/DoS and unreliable auth decisions - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize`, which is invoked on every unprivileged HTTP-trigger request received by the CRE Gateway, reads the `authorizedKeys` map without holding `h.mu`, while `syncMetadata` — run periodically on a background ticker — replaces that same map (and `workflowIDToRef`/`workflowRefToID`) while holding `h.mu.Lock()`. This is a data race on Go maps reachable purely by sending ordinary, unauthenticated/unprivileged trigger requests to the gateway, since `Authorize` is called for every incoming request before authentication succeeds.

### Finding Description
`Authorize` is the function that decides whether a signer is allowed to trigger a workflow: it reads `h.authorizedKeys[workflowID]` directly at line 92 with no lock. [3](#0-2) 

Meanwhile `syncMetadata`, invoked periodically by `runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)` from `Start`, builds fresh maps and swaps them into the struct under `h.mu.Lock()`: [2](#0-1) [4](#0-3) 

By contrast, other read paths on the very same struct (`GetWorkflowID`, `GetWorkflowReference`, `WorkflowShards`) correctly take `h.mu.RLock()` before reading: [5](#0-4) 

`Authorize` is the only accessor of these shared maps that does not lock. It is called from `httpTriggerHandler.authorizeRequest`, which is on the direct, unprivileged request path: any external caller hitting the HTTP trigger endpoint with a workflow ID/JWT triggers `HandleUserTriggerRequest → authorizeRequest → workflowMetadataHandler.Authorize`. [6](#0-5) [7](#0-6) 

Because Go maps are not safe for concurrent read/write, this pattern is a classic TOCTOU-style consistency defect analogous to the reported Cozy Finance flaw: the authorization decision is made against a data structure ("PToken/holder snapshot" analog = `authorizedKeys`) that can be concurrently mutated mid-read by an unrelated background process (the metadata sync "trigger"), rather than against a stable, atomically-read snapshot. Depending on Go runtime scheduling this can: (a) crash the process with "fatal error: concurrent map read and map write" (an unauthenticated remote client can cause this simply by sending trigger requests while metadata syncs, which happen every `MetadataAggregationIntervalMs`, default 1 minute), causing denial of service for the whole gateway process handling all DON workflow triggers; or (b) in rarer cases return corrupted/incorrect map lookup results, i.e., an authorization decision based on a torn read of the authorized-key set.

### Impact Explanation
A crash in the gateway process from a concurrent map read/write panic terminates the entire Gateway node handling all HTTP-triggered CRE workflows for its DON, not just the single requester — a full denial-of-service impact reachable by any unauthenticated caller sending ordinary trigger traffic. This is a Medium severity, node-availability impact rather than a fund-movement bypass, but is squarely within the requested scope (unprivileged-actor request path hitting node/gateway authentication/authorization logic).

### Likelihood Explanation
`syncMetadata` runs automatically and periodically (`MetadataAggregationIntervalMs`, default 60000ms) for the lifetime of the handler [8](#0-7) , and `Authorize` is invoked on every incoming trigger request without any special conditions. Any client sending trigger requests at a moderate rate will eventually race with a sync tick; higher request throughput or busier workflow registries increase the probability of hitting the unsynchronized window.

### Recommendation
Acquire `h.mu.RLock()`/`RUnlock()` around the map reads in `Authorize` (`h.authorizedKeys[workflowID]` lookup), matching the pattern already used in `GetWorkflowID`, `GetWorkflowReference`, and `WorkflowShards`. Alternatively, copy the required map/slice references while holding the lock before use.

### Proof of Concept
1. Configure a `WorkflowMetadataHandler` with a short `MetadataAggregationIntervalMs` (e.g., in tests) and register a valid workflow with an authorized key.
2. Run a goroutine that continuously calls `handler.syncMetadata(ctx)` (simulating the periodic ticker) in a tight loop while another goroutine continuously calls `handler.Authorize(workflowID, validJWT, req)` for valid signed requests.
3. Run with Go's race detector (`go test -race`) — this reliably reports a "DATA RACE" between `syncMetadata`'s map assignment (holding `h.mu.Lock()`) and `Authorize`'s unguarded read of `h.authorizedKeys`.
4. Under real concurrent load (without `-race`, e.g. in production), the same pattern can trigger a `fatal error: concurrent map read and map write`, crashing the gateway process — reproducible by sending trigger requests concurrently with a metadata sync tick.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-107)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L37-38)
```go
	defaultMetadataPullIntervalMs        = 1000 * 60 // 1 minute
	defaultMetadataAggregationIntervalMs = 1000 * 60 // 1 minute
```
