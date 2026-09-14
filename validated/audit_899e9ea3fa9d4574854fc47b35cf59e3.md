This confirms the root cause: `HandleUserTriggerRequest` calls `h.authorizeRequest` → `h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)` [1](#0-0)  which is a fully unprivileged, internet-facing entry point (no lock spanning the whole request, concurrent goroutines can call `Authorize` for the same JWT simultaneously). Inside `Authorize`, the JWT-replay defense is a non-atomic check-then-record: `isReplay()` takes an `RLock`, returns, and only later — after further processing — `recordUsage()` takes a separate `Lock` [2](#0-1) , with the two independent locking helpers defined here: [3](#0-2) .

This is a genuine analog of the reported reentrancy bug class: the fix in the CEGA report was "record state before performing the effect"; here the code does the mirror-image mistake — it checks the "already used" state, performs work, and only marks state as used afterward, with no atomicity between check and record. A single JWT can therefore be replayed via two concurrent requests before either finishes, defeating the anti-replay control, exactly as the vault's `RequestReplayGuard.CheckAndRecord` correctly avoids by doing the check-and-insert under one lock [4](#0-3) .

### Title
JWT replay-guard check-then-record race lets a single HTTP-trigger JWT authorize two concurrent workflow executions - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The Gateway's HTTP Trigger `Authorize` path is reachable by any unauthenticated internet client hitting the HTTP trigger endpoint with a signed JWT. The one-time-use enforcement for that JWT (`jti`) is implemented as two separate, independently-locked operations — `isReplay()` and `recordUsage()` — instead of one atomic check-and-set, mirroring the "check happens before state is finalized" flaw described in the reported reentrancy bug.

### Finding Description
`httpTriggerHandler.HandleUserTriggerRequest` calls `authorizeRequest`, which calls `h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)` for every incoming request, without any external serialization/locking scoped to a given JWT `jti` [5](#0-4) .

Inside `Authorize`:
```go
if h.jwtCache.isReplay(claims.ID) {
    ... return error
}
... // signer/authorized-key checks
h.jwtCache.recordUsage(claims.ID)
```
`isReplay` acquires `cache.mu.RLock()` and releases it before returning; `recordUsage` acquires `cache.mu.Lock()` separately, later [3](#0-2) . There is no single critical section spanning "read `seen`" and "write `seen`" for the same `jti`, so two goroutines processing two HTTP requests carrying the identical JWT can both pass `isReplay` before either calls `recordUsage`.

This is the same class of bug as the reported reentrancy: a check against not-yet-updated state is performed, an externally-triggered side effect (dispatching the workflow trigger to the DON) proceeds, and only afterward is the state that should have prevented the duplicate finally recorded — exactly analogous to `settleVault` checking `SettlementStatus` before, rather than atomically with, performing the payout.

By contrast, the Vault capability's own replay protection performs the check and insert atomically under one lock in `RequestReplayGuard.CheckAndRecord` [4](#0-3) , confirming that the HTTP-trigger cache's split-lock pattern is the outlier/regression.

### Impact Explanation
An unprivileged external caller who captures or is issued a single-use JWT for an HTTP trigger can fire two (or more) concurrent requests with that same token, causing the target workflow to be executed multiple times from what should be a single authorized invocation. Depending on the workflow's actions (on-chain writes, fund transfers, external API side effects), this can result in duplicate job/workflow runs and duplicated downstream effects triggered by a single authorization — a concrete unauthorized-run/duplicate-execution bypass of the anti-replay control.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to send near-simultaneous requests with the same JWT before the first `recordUsage` call completes — a narrow race window, but trivially triggerable by an external client since it only requires firing two HTTP requests in parallel (no privileged access, no on-chain state needed, unlike the original report which required specific asset/decimal/price conditions).

### Recommendation
Make the check-and-record atomic: hold a single lock (or use a `sync.Map`-based `LoadOrStore`, or the same pattern as `RequestReplayGuard.CheckAndRecord`) that performs "is this `jti` already present? if not, insert it" as one critical section, and reject the request if the insert reveals the entry already existed. Consider adopting `RequestReplayGuard` for this cache in `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go` instead of the separate `isReplay`/`recordUsage` methods.

### Proof of Concept
1. Obtain (or be issued) a single valid JWT for the HTTP trigger of workflow `W` with a given `jti`.
2. Fire two concurrent HTTP requests to the gateway's HTTP trigger endpoint carrying the identical JWT/`req` (same `jti`), timed so both reach `workflowMetadataHandler.Authorize` before either has called `recordUsage`.
3. Both calls to `h.jwtCache.isReplay(claims.ID)` return `false` because neither goroutine has yet recorded usage.
4. Both requests pass authorization and are separately dispatched via `sendWithRetries` to the workflow DON, causing workflow `W` to execute twice from a single-use token.

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
