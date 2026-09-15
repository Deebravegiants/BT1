### Title
Unsynchronized Map Access in `WorkflowMetadataHandler.Authorize` Causes Data Race with Concurrent Metadata Sync - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`WorkflowMetadataHandler.Authorize`, which validates the JWT signer against the currently-registered authorized keys for a workflow on every inbound HTTP trigger request, reads the shared `h.authorizedKeys` map without holding `h.mu`, while the periodically-running `syncMetadata` goroutine replaces that same map (and `workflowIDToRef`/`workflowShards`) under `h.mu.Lock()`. This is the direct analog of the Alchemy finding: a request-time validation routine assumes the "current state" it reads will not be mutated by another concurrently-running state-changing routine, but here that assumption is violated by design, on every single external request.

### Finding Description
`Authorize` is invoked from `httpTriggerHandler.authorizeRequest` for every unprivileged HTTP trigger request received by the gateway: [1](#0-0) 

It reads `h.authorizedKeys[workflowID]` directly, with no `h.mu.RLock()`: [2](#0-1) 

Meanwhile, `syncMetadata` runs on a periodic ticker (`MetadataAggregationIntervalMs`, default 1 minute) and fully replaces `h.authorizedKeys`, `h.workflowRefToID`, `h.workflowIDToRef`, and `h.workflowShards` while holding `h.mu.Lock()`: [3](#0-2) [4](#0-3) 

All other accessors of the same fields correctly take the lock (`GetWorkflowID`, `GetWorkflowReference`, `WorkflowShards`): [5](#0-4) 

Only `Authorize` — the function that performs the actual authentication decision (JWT signer vs. authorized key set) — omits synchronization. This mirrors the report's root cause: a validation routine that checks "current state" without accounting for the fact that another independently-triggered routine (there: another plugin's pre-hook; here: the periodic `syncMetadata` background goroutine) can concurrently mutate that exact state before/while the validation completes.

### Impact Explanation
Because `Authorize` reads a Go map (and the map header itself) concurrently with an unsynchronized write from `syncMetadata`, this is a data race on shared mutable state accessible via the internet-facing gateway's node API authentication path. In Go, concurrent unsynchronized map read/write is undefined behavior and commonly manifests at runtime as `fatal error: concurrent map read and write`, which crashes the entire gateway process — a hard, unrecoverable denial of service for the whole HTTP Trigger Handler capability, affecting all workflows and all tenants served by that gateway instance. Because the race is not merely benign staleness but literal concurrent access to a live Go map without a memory barrier, it can also produce corrupted/inconsistent authorization decisions in principle (reading a partially-updated map state), though the crash is the most reliably observable consequence.

### Likelihood Explanation
This race is trivially and continuously reachable: `syncMetadata` runs unconditionally on every gateway instance on a fixed timer once the handler is started, and `Authorize` runs on every single external HTTP trigger request (`HandleUserTriggerRequest` → `authorizeRequest` → `Authorize`). No malicious node, no privileged access, and no special timing manipulation are required — any legitimate external client issuing HTTP trigger requests at the moment `syncMetadata` fires will race with it. Given production traffic volume and the periodic nature of `syncMetadata`, this condition will be hit routinely rather than being a rare edge case.

### Recommendation
Take `h.mu.RLock()`/`RUnlock()` in `Authorize` around all reads of `h.authorizedKeys` (and any other shared handler state it touches), consistent with `GetWorkflowID`, `GetWorkflowReference`, and `WorkflowShards`. More broadly, audit `WorkflowMetadataHandler` for any other unsynchronized access to `authorizedKeys`, `workflowRefToID`, `workflowIDToRef`, or `workflowShards`, and document that these fields must never be read without holding `h.mu`, since they are the "in-flight state" replaced wholesale by the periodic `syncMetadata` goroutine.

### Proof of Concept
1. Start a gateway with `HTTPTriggerHandler`/`WorkflowMetadataHandler` running normally, with at least one workflow registered (so `authorizedKeys` is non-empty and `syncMetadata` will run and reassign the map every `MetadataAggregationIntervalMs`).
2. As an unprivileged external client, continuously send valid HTTP trigger requests (`HandleUserTriggerRequest`) with correctly signed JWTs for the registered workflow, at a rate high enough to overlap with the `syncMetadata` ticker tick (default every 1 minute) — e.g., fire requests in a tight loop for the duration of a test run.
3. Run the gateway process with Go's race detector enabled (`-race`) or under sustained load in a non-instrumented build; observe either a detected data race on `h.authorizedKeys` between `Authorize` (read) and `syncMetadata` (write), or, in production without the race detector, an eventual `fatal error: concurrent map read and write` crash of the gateway process, which is unrecoverable and terminates the service instance handling all workflow trigger traffic.

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L164-183)
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
