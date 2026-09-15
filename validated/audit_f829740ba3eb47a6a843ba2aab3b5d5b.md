Audit Report

## Title
Race condition in Gateway JWT replay-guard allows a single-use HTTP trigger token to authorize multiple workflow runs (TOCTOU) - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize()` checks JWT single-use via `jwtCache.isReplay()` and only marks the JWT as used via `jwtCache.recordUsage()` at the very end of the function, after workflow lookup and signer authorization checks succeed. Because `isReplay()` and `recordUsage()` are two independent, separately-locked operations rather than one atomic check-and-set, two concurrent `Authorize()` calls carrying the same JWT (`jti`) can both pass the replay check before either records usage, allowing a single-use JWT to authorize two workflow executions.

## Finding Description
`isReplay()` takes an `RLock`, checks map membership, and releases the lock immediately; `recordUsage()` acquires a separate `Lock` only after workflow-existence and signer-authorization checks complete: [1](#0-0) [2](#0-1) 

Crucially, the calling path `HandleUserTriggerRequest` invokes `authorizeRequest` (which calls `Authorize`) at line 106, well before the per-`requestID` in-flight dedup check performed in `setupCallback` at line 141/423-426: [3](#0-2) [4](#0-3) 

This confirms the existing in-flight request-ID dedup guard in `setupCallback` does **not** protect against this race, because it runs strictly after `Authorize()` has already been called and the JWT replay window has already passed. Two goroutines can both execute `isReplay(claims.ID)` and observe `false` before either calls `recordUsage(claims.ID)`, since these are non-atomic, independently-locked map operations. The existing tests only exercise sequential reuse (`duplicate request ID` and `duplicate JWT token and request ID` in `http_trigger_handler_test.go`), not concurrent reuse, so this gap is untested.

## Impact Explanation
A single signed JWT that is supposed to authorize exactly one HTTP-triggered workflow execution can, under concurrent submission, authorize two (or more) executions. Since `Authorize()` succeeding leads directly to `sendWithRetries` dispatching the trigger to the workflow DON, this is a concrete "unauthorized job run" — the gateway's single-use JWT invariant is broken by an unprivileged holder of a valid JWT, not by any operator/admin/host-level actor.

## Likelihood Explanation
Exploitation only requires an attacker to hold one valid signed JWT (as any legitimate unprivileged caller would) and to submit it via two near-simultaneous HTTP requests to the gateway — no cryptographic break, no special privilege, and no reliance on a malicious node/peer/operator. The race window exists across every `Authorize()` call, making it reliably reproducible under concurrency (e.g., detectable under `go test -race` with two goroutines).

## Recommendation
Combine the replay check and the usage recording into a single atomic "check-and-set" operation performed under one lock acquisition in `jwtReplayCache` (e.g., a `CheckAndRecord(jti)` method), analogous to `RequestReplayGuard.CheckAndRecord` used elsewhere in the codebase, so no two goroutines can observe "not yet used" for the same `jti` at once. Additionally, review the unguarded read of `h.authorizedKeys[workflowID]` in `Authorize()`, which is accessed without holding `h.mu`.

## Proof of Concept
1. Register a workflow and authorized signer key, as done in `createTestTriggerHandler`/`registerWorkflow` in `http_trigger_handler_test.go`.
2. Create one signed JWT via `createTestJWTToken(t, req, privateKey)`.
3. Spawn two goroutines that each call `handler.workflowMetadataHandler.Authorize(workflowID, token, req)` concurrently with the identical token/request, synchronized (e.g., via a barrier or short injected delay between `isReplay` and `recordUsage`) so both execute `isReplay()` before either executes `recordUsage()`.
4. Observe both calls return `(key, nil)` instead of the second one returning "JWT token has already been used," confirming double authorization from a single-use JWT. This can also be demonstrated by adapting the existing "duplicate JWT token and request ID" test in `http_trigger_handler_test.go` to fire both `HandleUserTriggerRequest` calls concurrently instead of sequentially, using distinct request IDs to bypass the unrelated in-flight-request-ID dedup and isolate the JWT race.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L87-105)
```go
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L399-412)
```go
func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}

func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-146)
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

	strippedWorkflowID := strings.TrimPrefix(workflowID, "0x")
	legacyExecutionID, err := workflows.EncodeExecutionID(strippedWorkflowID, req.ID) //nolint:staticcheck // legacy ID kept for observability comparison
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID: " + err.Error())
	}
	// Workflows shouldn't use more than one HTTP trigger. If we ever need to support multiple triggers, we'd need to pass
	// trigger index to the Gateway handler and somehow allow senders to pick. For now, we use trigger index 0.
	// Execution IDs here are used only for logging.
	executionIDWithTriggerIndex, err := workflows.GenerateExecutionIDWithTriggerIndex(strippedWorkflowID, req.ID, 0)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID with trigger index: " + err.Error())
	}
	h.lggr.Debugw("processing request",
		"legacyExecutionID", legacyExecutionID,
		"executionIDWithTriggerIndex", executionIDWithTriggerIndex,
		"requestID", req.ID,
		"workflowID", workflowID)

	reqWithKey, err := reqWithAuthorizedKey(triggerReq, *key)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error marshaling trigger request: " + err.Error())
	}

	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
	}

	return h.sendWithRetries(ctx, legacyExecutionID, executionIDWithTriggerIndex, reqWithKey, workflowID, doneCh)
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-426)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
```
