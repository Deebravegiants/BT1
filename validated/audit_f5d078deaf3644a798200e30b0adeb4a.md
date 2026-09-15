The code confirms the claim exactly as described: `isReplay` and `recordUsage` are separate lock acquisitions with no atomicity across the check-then-act sequence, and `recordUsage` is deferred until after signer/authorized-key validation completes.Audit Report

## Title
JWT Replay-Protection Check-Then-Act Race Allows Concurrent Reuse of the Same JWT for Repeated Unauthorized Trigger Requests - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` calls `h.jwtCache.isReplay(claims.ID)` to check for reuse and only calls `h.jwtCache.recordUsage(claims.ID)` after signer/authorized-key checks succeed, with `isReplay` and `recordUsage` acquiring separate, independent locks (`RLock`/`Lock`) rather than performing an atomic check-and-set. This is a genuine TOCTOU race: two concurrent requests carrying the same signed JWT can both pass `isReplay` before either calls `recordUsage`, allowing the same `jti` to be authorized twice.

## Finding Description
`Authorize` verifies the JWT, checks `h.jwtCache.isReplay(claims.ID)` [1](#0-0) , then performs authorized-key lookups, and only calls `h.jwtCache.recordUsage(claims.ID)` at the very end of the function [2](#0-1) . The `jwtReplayCache` implements `isReplay` with an `RLock`/`RUnlock` pair and `recordUsage` with a separate `Lock`/`Unlock` pair on the same `map[string]time.Time`, with no lock held across the whole check-then-act sequence [3](#0-2) . Two goroutines processing the identical JWT concurrently can both observe "not present" in `isReplay` before either writes via `recordUsage`, so both proceed through signer/authorized-key checks and are treated as authorized.

This flows from `httpTriggerHandler.authorizeRequest`, which calls `h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)` directly from the externally-reachable `HandleUserTriggerRequest` path [4](#0-3) . Note, however, that `HandleUserTriggerRequest` also calls `h.resolveWorkflowID` before `authorizeRequest`, and afterward calls `h.setupCallback`, which independently rejects a request whose `requestID` (i.e., `req.ID`) is already in-flight [5](#0-4) . Since the JWT's signed digest is computed over the request (`VerifyRequestJWT(token, *req)`), and the request includes `req.ID`, an attacker replaying the exact same signed request (identical `req.ID`) would still be blocked from actually causing a second execution by the `setupCallback` requestID uniqueness check, even though the JWT `jti` gets "double-authorized" in the race window. The report's PoC does not address or rule out this downstream check, so the claim that this race leads to "repeated unauthorized trigger requests" (i.e., duplicate dispatched executions) is not fully substantiated — the `Authorize`-level race is real, but its end-to-end impact depends on whether an attacker can produce two distinct requests (different `req.ID`) that still validate against the *same* JWT, which was not demonstrated. I was unable to fully verify the exact contents/format signed by `VerifyRequestJWT`/the digest binding to `req.ID` within the available tool budget, so this downstream mitigation's completeness against the claimed impact remains partially unconfirmed.

## Impact Explanation
The `Authorize` function's check-then-act race on `jwtCache` is a real, concrete concurrency defect: `isReplay` and `recordUsage` are non-atomic, so a JWT can pass the replay check twice under concurrent load [3](#0-2) . However, the actual downstream consequence (duplicate workflow execution) is guarded by a separate, independent, atomic `requestID`-uniqueness check under a mutex in `setupCallback` [5](#0-4) , which would reject the second identical request before it results in a duplicate dispatch to nodes — provided the JWT is bound to a specific `req.ID`/digest as the report itself states. This means the exploitable end state described in the report (an unprivileged caller causing "repeated unauthorized trigger requests" / duplicate workflow triggering) is not clearly achievable purely via this race, since the primary anti-duplication mechanism the report is targeting is not the sole line of defense against duplicate execution.

## Likelihood Explanation
Winning the race window itself (concurrently querying `isReplay` before either side calls `recordUsage`) is plausible for a determined attacker firing parallel copies of a signed request. But because the request digest that the JWT signs includes `req.ID`, and a duplicate `req.ID` is independently rejected by `setupCallback`'s atomic map check, the practical exploitability of turning this into unauthorized/duplicate trigger execution is significantly reduced, contrary to the report's characterization.

## Recommendation
Regardless of the downstream mitigation, `isReplay`/`recordUsage` should still be made atomic (e.g., a single locked "check-and-insert" operation) as good practice to avoid relying on `setupCallback`'s incidental protection and to keep the JWT replay cache correct as an independent security control, since other call paths or future refactors could rely on `jwtCache` alone.

## Proof of Concept
Not independently reproducible as a full unauthorized-duplicate-trigger exploit with the evidence gathered: a race-condition unit test on `jwtReplayCache.isReplay`/`recordUsage` directly (two goroutines calling `isReplay` concurrently before either calls `recordUsage`) would confirm the low-level race, but end-to-end proof that this results in duplicate workflow execution requires demonstrating that two *different* `req.ID`s can carry a JWT whose digest binds only to workflow-level fields (not `req.ID`), which was not confirmed within the available investigation. Given this gap and the presence of the `setupCallback` requestID-uniqueness safeguard as an independent, atomic control on the same request path, this report's severity claim is not adequately substantiated as a full authorization-bypass/duplicate-trigger vulnerability.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-90)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L92-107)
```go
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
