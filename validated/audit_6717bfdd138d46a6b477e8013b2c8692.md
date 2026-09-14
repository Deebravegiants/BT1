Confirmed: `httpTriggerHandler.HandleUserTriggerRequest` is the direct handler for incoming unprivileged user HTTP-trigger requests, and it calls `authorizeRequest` → `WorkflowMetadataHandler.Authorize` [1](#0-0) , which reads `h.authorizedKeys[workflowID]` without taking `h.mu` [2](#0-1) , while the periodic `syncMetadata` goroutine mutates the very same map under `h.mu.Lock()` [3](#0-2) .

### Title
Unsynchronized concurrent map access in `WorkflowMetadataHandler.Authorize()` causes crash / auth-state race on concurrent user requests - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`Authorize()` is invoked directly on the hot path of every unprivileged HTTP-trigger request, but it reads `h.authorizedKeys` without holding `h.mu`, while a background ticker goroutine (`syncMetadata`) periodically replaces that same map while holding `h.mu.Lock()`. This is the same bug class as CVE-2023-32253 (deadlock/DoS triggerable by concurrent unprivileged requests against a shared, lock-protected cache), except here the concurrency defect is a data race rather than a deadlock — but it is reachable the same way: an unprivileged remote actor sending overlapping requests concurrently with the node's normal internal state-refresh cycle.

### Finding Description
- `WorkflowMetadataHandler.Authorize(workflowID, token, req)` is called from `httpTriggerHandler.authorizeRequest`, itself called from `HandleUserTriggerRequest`, which is the gateway's entry point for external/unprivileged HTTP trigger requests [4](#0-3) .
- Inside `Authorize`, the code does `keys, exists := h.authorizedKeys[workflowID]` and later indexes into `keys[key]` with **no lock held** [5](#0-4) .
- All other accessors of the same handler state (`GetWorkflowID`, `GetWorkflowReference`, `WorkflowShards`) correctly take `h.mu.RLock()`/`RUnlock()` before touching the maps [6](#0-5) [7](#0-6) .
- `syncMetadata`, run periodically via `runTicker` from `Start()` [8](#0-7) , builds an entirely new `authorizedKeys` map and swaps it into `h.authorizedKeys` under `h.mu.Lock()` [3](#0-2) .
- Because `Authorize()` reads `h.authorizedKeys` unguarded while `syncMetadata` concurrently writes the field (map reassignment) under the mutex, Go's race detector/runtime will flag this as a data race; in production this can trigger the Go runtime's `fatal error: concurrent map read and map write` panic, crashing the entire gateway process — a remotely triggerable denial of service. It can also, in more benign cases, yield an authorization check performed against a stale or half-updated key set (cross-user response confusion / bypass of intended re-authorization semantics), though the crash is the primary, easily provable impact.
- This is structurally analogous to the ksmbd bug class: a shared, mutex-protected resource is accessed unsafely on a request-processing path that fires per external caller, while a periodic maintenance path also touches that resource — sending overlapping unprivileged requests during a metadata sync window is sufficient to trigger the fault.

### Impact Explanation
An unprivileged remote client can send HTTP trigger requests continuously; combined with the node's own metadata sync ticker (which runs at `MetadataAggregationIntervalMs` and is unavoidable/always active), this creates a naturally recurring race window. If the race is hit, the entire gateway node process can crash (`fatal error: concurrent map read and map write` is unrecoverable by design — it bypasses `recover()`), taking down request handling for all workflows served by that gateway. This matches "Availability: High" impact under the referenced CVE (CVSS AV:N/AC:H/../A:H).

### Likelihood Explanation
Likelihood is analogous to the original CVE: it requires precise but achievable timing — an attacker only needs to keep sending trigger requests to increase the probability of overlapping with a metadata sync cycle. No special privileges are required; only knowledge of a valid `workflowID` (which is often the very information a legitimate but unprivileged client would have) is needed to reach `Authorize()`. The condition is a race, so it is probabilistic rather than deterministic, similar to the "AC:H" (high attack complexity) rating in the referenced CVE.

### Recommendation
Take `h.mu.RLock()`/`defer h.mu.RUnlock()` at the top of `Authorize()` before reading `h.authorizedKeys`, matching the pattern already used in `GetWorkflowID`, `GetWorkflowReference`, and `WorkflowShards`. Since `Authorize()` also calls `h.jwtCache.recordUsage` (already separately locked) and does logging, only the `h.authorizedKeys` lookup needs to be brought under `h.mu`.

### Proof of Concept
1. Start a `WorkflowMetadataHandler` with `Start()` running (so the `syncMetadata` ticker is active) and register at least one workflow with authorized keys.
2. In one goroutine, repeatedly call `handler.Authorize(workflowID, token, req)` (simulating concurrent unprivileged HTTP-trigger requests hitting `HandleUserTriggerRequest` → `authorizeRequest`).
3. In another goroutine (or via the real ticker), repeatedly call `handler.syncMetadata(ctx)` to simulate the periodic metadata refresh reassigning `h.authorizedKeys`.
4. Run with `go test -race`, or under sustained load in production; the concurrent unsynchronized map read in `Authorize` against the mutex-protected write in `syncMetadata` will be flagged by the race detector, and under real load can crash the process with `fatal error: concurrent map read and map write`.

### Citations

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
