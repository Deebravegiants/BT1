### Title
JWT Replay via TOCTOU Race in Gateway HTTP Trigger Authorization - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` is meant to enforce single-use JWT tokens for HTTP-triggered workflow execution requests coming from unprivileged clients through the internet-facing Gateway. The replay check (`isReplay`) and the replay recording (`recordUsage`) are two separate, non-atomic operations on the `jwtReplayCache`, creating a check-then-act race window that lets the same JWT be used to authorize more than one concurrent request, defeating the intended single-use/anti-replay guarantee.

### Finding Description
`Authorize` first verifies the JWT signature/digest, then checks for replay, then validates the signer against the workflow's authorized keys, and only *after* all of that succeeds does it record the token as used: [1](#0-0) 

The replay cache itself exposes `isReplay` (read lock) and `recordUsage` (write lock) as two independently-locked methods rather than a single atomic check-and-set: [2](#0-1) 

Because `isReplay` (line 87) and `recordUsage` (line 105) acquire and release the mutex independently, two goroutines calling `Authorize` concurrently with the *same* JWT (same `jti`) can both pass the `isReplay` check before either calls `recordUsage`. Both then proceed to pass signer validation and both get authorized, effectively processing the same signed request twice.

This directly parallels the underlying bug class in the external report: a token/credential meant to be single-use (there, a remote-cluster invite token; here, a single-use workflow-trigger JWT) is not atomically invalidated at the moment of use, allowing an attacker who captures/observes a valid token to replay it and be treated as though it were still valid.

The codebase already demonstrates the correct pattern elsewhere: `RequestReplayGuard.CheckAndRecord` in the Vault capability performs the check and the record under a single lock hold, atomically: [3](#0-2) 

`WorkflowMetadataHandler`'s `jwtReplayCache` does not follow this atomic pattern, making it the outlier and the vulnerable path.

`Authorize` is invoked from `httpTriggerHandler.authorizeRequest`, which is reached directly from unprivileged, internet-facing `HandleUserTriggerRequest` calls (JSON-RPC HTTP trigger requests to the Gateway): [4](#0-3) [5](#0-4) 

Note that `HandleUserTriggerRequest` does have a separate, atomic in-flight-request-ID guard (`setupCallback`/`callbacksMu`) that prevents duplicate processing keyed by JSON-RPC request ID, but this is a distinct mechanism from JWT replay protection, keyed by `req.ID` rather than `jti`, and does not close the race on the JWT cache itself — an attacker can send two concurrent requests with different top-level request IDs but the same underlying signed JWT/jti (e.g. resubmitting a captured token attached to a new outer request), bypassing the request-ID dedup entirely while still winning the JWT-cache race.

### Impact Explanation
Successful exploitation allows a single-use, short-lived workflow-execution JWT to authorize more than one workflow trigger execution. Since `Authorize`'s outcome directly gates whether the Gateway fans a trigger out to the DON (`sendWithRetries`) for actual workflow execution, this can result in duplicate/unauthorized job runs from a captured or replayed token — which could translate into duplicate on-chain actions or fund movement depending on what the triggered workflow does. This is an authentication/anti-replay bypass reachable from an unprivileged client, matching the "unauthorized job run" impact category.

### Likelihood Explanation
Exploitation requires only the ability to send two requests with the same valid signed JWT to the internet-facing Gateway "workflow execute" endpoint at roughly the same time (a trivial race to win over a network round trip), and does not require any special privilege beyond possessing (or having captured/observed) a legitimately issued token before it's consumed. No malicious node, peer, or operator access is required — it is purely a client-side race against the unprivileged HTTP-triggered execution path.

### Recommendation
Make the JWT replay check-and-record atomic, following the pattern already used by `RequestReplayGuard.CheckAndRecord`: combine `isReplay` and `recordUsage` into a single method that holds the write lock for both the existence check and the insertion, and call it once at the point authorization succeeds (or immediately after signature/digest verification, before other authorization checks), so no other goroutine can observe an unrecorded `jti` between the check and the record.

### Proof of Concept
1. Issue one workflow-trigger JWT (`jti = X`) signed by an authorized workflow key.
2. Fire two `HandleUserTriggerRequest` calls concurrently (different outer JSON-RPC request IDs to avoid the unrelated `callbacksMu`/`setupCallback` dedup) both carrying the same JWT with `jti = X`.
3. Both goroutines call `WorkflowMetadataHandler.Authorize`; both call `h.jwtCache.isReplay(claims.ID)` before either calls `h.jwtCache.recordUsage(claims.ID)`, so both see `exists == false` and both pass. Both are then dispatched to the DON, executing the workflow twice from a single-use token.

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

**File:** core/capabilities/vault/request_replay_guard.go (L35-47)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
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
