Audit Report

## Title
JWT Replay-Protection Check-Then-Act Race in `WorkflowMetadataHandler.Authorize` Allows Single-Use JWT Reuse - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

## Summary
`WorkflowMetadataHandler.Authorize` checks whether a JWT `jti` has already been used via `h.jwtCache.isReplay(claims.ID)` and only marks it used several lines later via `h.jwtCache.recordUsage(claims.ID)`, with unrelated map lookups (`h.authorizedKeys[workflowID]`, key membership check) executed in between under no lock on the JWT cache. Concurrent requests carrying the identical signed JWT can all observe `isReplay == false` before any of them calls `recordUsage`, defeating the single-use replay protection intended for the HTTP-trigger authentication path.

## Finding Description
`Authorize` is invoked from `httpTriggerHandler.authorizeRequest` [1](#0-0) , which is called from `HandleUserTriggerRequest`, the entry point that handles unprivileged, internet-facing HTTP-trigger requests [2](#0-1) .

Inside `Authorize`, the replay check and the usage recording are two separate, non-atomic operations, separated by additional unrelated logic: [3](#0-2) 

`isReplay` takes `cache.mu.RLock()` and releases it before returning; `recordUsage` separately takes `cache.mu.Lock()`: [4](#0-3) 

Because there is no single critical section spanning "check" and "mark used," two goroutines processing concurrent requests with the same JWT can both execute `isReplay` (returning `false` for both) before either executes `recordUsage`. The per-request `requestID` uniqueness check in `setupCallback` (`h.callbacks[requestID]`) does not prevent this, because `requestID` (`req.ID`, user-supplied and required to be unique) is a separate field from the JWT's `jti` claim used for replay protection — an attacker can send multiple requests with distinct `requestID`s but the identical JWT, bypassing the requestID dedup check entirely while still racing the JWT check-then-act window [5](#0-4) .

## Impact Explanation
Successful exploitation lets an unprivileged client bypass the single-use replay guard and get the gateway to accept and dispatch the same authorized JWT more than once concurrently, resulting in duplicate workflow-trigger executions being forwarded to the DON that should have been rejected as replays. This undermines the intended "unauthorized job run" guarantee of the JWT replay cache on the internet-facing HTTP trigger gateway path, matching the in-scope "unauthorized job run" impact category.

## Likelihood Explanation
Exploitation only requires the ability to send several concurrent HTTP requests to the gateway's HTTP trigger endpoint using the same previously-issued valid JWT with distinct `requestID`s — something any unprivileged client that already legitimately obtained one signed JWT can do without special access. The race window, while short, spans a JWT verification, two unlocked map lookups, and a lock acquisition, and is reliably triggerable with a burst of parallel requests carrying the same token.

## Recommendation
Make the "check-not-replayed" and "mark-as-used" operations atomic under a single lock in `jwtReplayCache`, e.g., add a `CheckAndRecord(jti string) bool` method that acquires `mu.Lock()` once, checks for existence, and inserts the entry in the same critical section, then update `Authorize` to call this atomic method instead of separately calling `isReplay` followed later by `recordUsage`.

## Proof of Concept
1. Obtain a legitimately signed JWT for a workflow-trigger request with `jti = X`.
2. Fire N concurrent HTTP requests to the gateway's HTTP trigger endpoint, each with a distinct `id`/`requestID` (to avoid the unrelated `setupCallback` dedup check) but all presenting the identical JWT (`jti = X`) in `req.Auth`.
3. Each goroutine handling a request calls `WorkflowMetadataHandler.Authorize`, which calls `h.jwtCache.isReplay(X)`; because `recordUsage(X)` has not completed for any of the concurrent calls yet, multiple goroutines observe `isReplay == false` and proceed, each accepting the same JWT and dispatching a duplicate workflow-trigger execution — verifiable via a Go unit test that spawns concurrent goroutines calling `Authorize` with the same token/claims and asserts more than one call succeeds.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
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
