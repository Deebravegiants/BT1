Audit Report

## Title
Non-atomic check-then-act in JWT replay cache allows replay of the same authorization token - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` checks JWT replay status via `jwtCache.isReplay` and only records usage via `jwtCache.recordUsage` after the authorized-key lookup completes. The read and write to the replay-tracking map are performed in separate, non-atomic critical sections (`RLock` for `isReplay`, a distinct `Lock` for `recordUsage`), so two concurrent requests carrying the identical JWT can both pass the replay check before either records usage. [1](#0-0) [2](#0-1) 

## Finding Description
`Authorize` verifies the JWT signature, then calls `h.jwtCache.isReplay(claims.ID)` which acquires `RLock`, checks map membership, and releases the lock. Only after the authorized-key lookup succeeds does the function call `h.jwtCache.recordUsage(claims.ID)`, which acquires a separate `Lock`. [3](#0-2)  There is no lock spanning both operations, so the "has this jti been used" check and "mark this jti as used" mutation are not atomic. Two goroutines processing requests with the same `jti` concurrently can both observe `isReplay == false`, both pass the authorized-key check, and both call `recordUsage`. [2](#0-1) 

I traced the call path: `httpTriggerHandler.HandleUserTriggerRequest` calls `authorizeRequest`, which calls `workflowMetadataHandler.Authorize` directly, with no additional deduplication on the JWT `jti` anywhere else in the pipeline. [4](#0-3)  Note that `setupCallback` does enforce uniqueness, but only on the user-supplied JSON-RPC `req.ID`, not on the JWT's `jti` claim — these are independent fields, so an attacker can send two requests with distinct `req.ID` values but the identical JWT/`jti`, defeating that unrelated guard and still hitting the race window in `Authorize`. [5](#0-4) 

## Impact Explanation
The cache's stated purpose is one-time-use JWT enforcement ("JWT token has already been used..."). [6](#0-5)  If a valid signed JWT is submitted twice at nearly the same instant, both requests can be authorized and dispatched to the DON as duplicate `workflows.execute` calls, sending the request to all shard nodes twice. [7](#0-6)  This is a genuine violation of the intended one-time-use invariant and maps to a gateway request impersonation/replay bypass. However, the exploit does not bypass JWT signature verification or authorized-key checks; it only defeats the supplementary anti-replay layer, and each duplicate request must still be independently rate-limited and aggregated by the DON (2f+1 identical-response requirement), which somewhat limits standalone severity.

## Likelihood Explanation
Likelihood is limited: it requires possession of an already-valid, correctly signed JWT with a not-yet-recorded `jti`, and the ability to submit two copies of that exact same token concurrently within a microsecond-scale race window between the `RLock` release in `isReplay` and the `Lock` acquisition in `recordUsage`. Since a legitimate token holder controls their own JWT anyway (and could simply issue two separate JWTs to trigger the workflow twice with only slightly more effort), the marginal value of this race is chiefly in scenarios where token possession, not workflow-execution privilege, is meant to be the single-use resource (e.g., a token intended to be forwarded once, or a token exposed to a third party who is meant to be limited to one use). This is a real, provable code inconsistency, but exploitation requires precise timing and doesn't escalate privileges beyond what the token's legitimate signer already possesses.

## Recommendation
Combine the check and the mutation into a single atomic operation, e.g., a `checkAndRecordJWTUsed(jti string) bool` method that acquires one write lock, checks map membership, inserts the entry, and returns whether the token was already present — removing the separate `isReplay`/`recordUsage` calls from `Authorize`. Also note `jwtReplayCache` is in-memory and per-instance; if multiple gateway replicas exist, this replay protection is not shared across instances, which is a separate deployment-scope concern beyond the atomicity fix.

## Proof of Concept
1. Obtain a validly signed JWT for a registered workflow with `jti = "X"`.
2. Fire two HTTP trigger requests using distinct `req.ID` values (to bypass the unrelated `setupCallback` requestID-dedup) but carrying the identical JWT (`jti = "X"`) to the gateway concurrently.
3. Both goroutines execute `Authorize`: both call `h.jwtCache.isReplay("X")` before either calls `h.jwtCache.recordUsage("X")`; race timing allows both to observe `false`.
4. Both requests pass the authorized-key check and are separately dispatched via `sendWithRetries` to the workflow DON — the token authorizes two independent executions despite the intended one-time-use enforcement. [1](#0-0) [7](#0-6) 

This can be confirmed deterministically with a Go unit test that spawns two goroutines calling `Authorize` with the same `jti` after artificially delaying between the `isReplay` and `recordUsage` calls (e.g., via a test hook or `-race`-detectable interleaving), asserting both return success.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-147)
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
