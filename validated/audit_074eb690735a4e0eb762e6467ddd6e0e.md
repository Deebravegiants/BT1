## Analysis: TOCTOU Race in Single-Use JWT Replay Protection Enables Authorization Bypass

The external report describes a "double-spend" caused by a custom forwarding mechanism failing to enforce single-use semantics on a voucher. The closest structural analog in this codebase is in the Gateway's HTTP-trigger authorization path, where a single-use signed JWT's replay check is not atomic with its "mark as used" step.

### Title
Non-atomic check-then-record JWT replay guard allows concurrent reuse of a single-use trigger authorization token - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
`WorkflowMetadataHandler.Authorize`, which authorizes every unprivileged client's `workflows.execute` HTTP-trigger request at the Gateway, checks whether a JWT's `jti` has already been used and only later records it as used, with no lock held across the whole operation. Two concurrent requests presenting the identical signed, single-use JWT can both pass the replay check before either records usage, defeating the single-use guarantee that is documented as "REQUIRED" for this token.

### Finding Description
`Authorize` performs the check and the record as two separate, independently-locked operations: [1](#0-0) 

`isReplay` takes an `RLock`, checks membership, and releases the lock; `recordUsage` is called afterwards under a completely separate `Lock`: [2](#0-1) 

Between the `isReplay` check returning `false` and `recordUsage` being invoked, an arbitrary number of concurrent goroutines calling `Authorize` with the same `jti` will all observe "not yet seen" and all proceed to be authorized, each returning a valid `*gateway.AuthorizedKey`. This is a classic check-then-act TOCTOU race on a security-critical single-use token, directly analogous to the Nomic bug class where a custom forwarding path failed to atomically consume a voucher before allowing it to be reused.

This is reachable directly from an unauthenticated network client: `HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize`: [3](#0-2) 

By contrast, the Vault capability in the same codebase implements the equivalent single-use guard correctly, atomically checking-and-recording under one lock: [4](#0-3) 

This confirms the intended design pattern for replay guards in this codebase is atomic check-and-record, and the Gateway's `jwtReplayCache` deviates from it.

### Impact Explanation
A signed, single-use JWT authorizing a workflow trigger is meant to be usable exactly once (the comment in `core/utils/jwt.go` explicitly marks `jti` as "REQUIRED" for replay protection). Due to the race, the same token can be accepted by `Authorize` more than once concurrently, each successful call producing a valid `AuthorizedKey` that is then used to build and dispatch a signed `workflows.execute` request to the workflow DON via `sendWithRetries`. Downstream, `setupCallback` deduplicates in-flight requests by the client-supplied JSON-RPC `id`, which mitigates same-ID replay, but does not restore the intended single-use guarantee of the JWT itself — the authorization bypass occurs before that dedup layer, and any code path or future caller (or client varying the request `id` while presenting the same authorization) that relies on `Authorize`'s single-use contract is not protected.

### Likelihood Explanation
The race window is real and requires no privileged access — only the ability to fire the same signed token in two concurrent Gateway requests, something trivially achievable by an unprivileged client. `jwtReplayCache` has no synchronization spanning the read-check to the write-record step, so this is a deterministic-under-race condition, not a theoretical one.

### Recommendation
Make the replay check-and-record atomic under a single critical section, mirroring `vault.RequestReplayGuard.CheckAndRecord`: combine `isReplay` and `recordUsage` into one method that takes the lock once, checks for existence, and inserts if absent, returning whether the token was already used.

### Proof of Concept
1. Client signs a single JSON-RPC `workflows.execute` request with a JWT containing `jti=X` bound to that request's digest.
2. Client fires two concurrent HTTP requests to the Gateway carrying the identical signed JWT (same `jti`), e.g. via two goroutines/`curl` processes hitting the trigger endpoint at the same instant.
3. Both requests reach `WorkflowMetadataHandler.Authorize` concurrently; both call `h.jwtCache.isReplay(claims.ID)` before either calls `h.jwtCache.recordUsage(claims.ID)`, so both observe `false` and both are authorized.
4. Both authorized calls proceed into `HandleUserTriggerRequest`'s downstream flow, demonstrating that the "used once" invariant documented for `jti` does not hold under concurrency. [1](#0-0)

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
