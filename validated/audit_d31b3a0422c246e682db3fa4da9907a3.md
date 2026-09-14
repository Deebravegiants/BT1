### Title
JWT single-use replay protection has a check-then-act race allowing token reuse in `WorkflowMetadataHandler.Authorize` - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` is meant to guarantee that a client-supplied JWT (identified by its `jti` claim) can authorize exactly one gateway-routed request. The "already used" check (`isReplay`) and the "mark as used" write (`recordUsage`) are two separate, independently-locked operations with unrelated work (key/signer validation) executed between them, instead of being one atomic check-and-set. This is the same class of bug as the RFP report: a piece of caller-controlled state (the recipient's `proposalBid` / here, the JWT's used status) is checked at one point and only committed later, and an attacker can exploit the gap between the check and the commit to get more than the single authorized use that the design intends.

### Finding Description
`Authorize` performs, in order:
1. `claims, signer, err := utils.VerifyRequestJWT(token, *req)` – verifies signature/claims.
2. `h.jwtCache.isReplay(claims.ID)` – read-only lookup under `cache.mu.RLock()`. [1](#0-0) 
3. Looks up `h.authorizedKeys[workflowID]` and validates the signer is an authorized key for the workflow. [2](#0-1) 
4. Only after all of that succeeds does it call `h.jwtCache.recordUsage(claims.ID)` to mark the `jti` as used. [3](#0-2) 

The cache itself exposes `isReplay` and `recordUsage` as two independently-locked methods rather than a single atomic "check-and-set" primitive: [4](#0-3) 

Because `isReplay` releases its lock immediately and `recordUsage` is only called at the very end of `Authorize` (after JWT signature verification and authorized-key map lookups), two (or more) requests carrying the exact same JWT that arrive concurrently can both pass the `isReplay` check before either one calls `recordUsage`. Both requests will then be treated as validly authorized, even though the JWT was designed to be single-use — the code path itself documents the single-use intent ("JWT token has already been used. Please generate a new one with new id (jti)").

This mirrors the root cause pattern in the RFP report: a state-changing decision (accept the recipient / authorize the request) is made based on a value that was checked earlier but is not atomically locked/consumed at check time, letting the caller "front-run" the gap to get an outcome (a second acceptance, a second privileged bid, a second authorized action) that the single-use/one-shot design was meant to prevent.

### Impact Explanation
Because `Authorize` gates access to gateway-routed, node-facing "web-api trigger" workflow-metadata requests (an unprivileged, internet-facing client submits a signed JWT to reach DON/gateway infrastructure), the missing atomicity allows request impersonation/duplication: a single client-issued, intended-single-use authorization token can be used to obtain two independently-authorized requests processed by the DON/gateway instead of one. Depending on what the metadata pull/execute operation gates (workflow triggering, metadata aggregation, quorum bookkeeping), this can let an attacker double-fire an operation that the single-use JWT design assumed would only be allowed once, undermining a security control intended to bound per-token request volume/idempotency — the same "one-shot state gets consumed twice due to a TOCTOU gap" impact class as the original finding (extra, unintended privileged action executed against caller-supplied stale/duplicate state).

### Likelihood Explanation
Exploitation requires only sending the same signed JWT concurrently (or in very close succession) to the gateway — no privileged access, no node compromise, and no network-layer trickery are needed; it is purely a client-triggerable race against the handler's own internal locking scheme. The window is small but real given `isReplay`/`recordUsage` are separate critical sections with JWT verification and map lookups executed in between, which is enough time for two goroutines/handlers processing concurrent gateway messages to both pass the check.

### Recommendation
Make the check-and-mark operation atomic: acquire the cache's write lock once, check `cache[jti]` for existence, and if absent set `cache[jti] = time.Now()` in the same critical section (i.e., replace `isReplay`+`recordUsage` with a single `checkAndRecord(jti) bool` method under one `mu.Lock()`), analogous to how `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go` already implements this pattern correctly for a very similar vault-JWT replay concern: [5](#0-4) 
Reuse or mirror that atomic pattern in `jwtReplayCache` so `Authorize` cannot be raced.

### Proof of Concept
Because the actual race requires precise concurrent execution timing that can't be reliably demonstrated without running goroutines against the live locking implementation, this is a structural/code-level proof rather than an executed exploit:

1. Two concurrent calls arrive: `Authorize(workflowID, tokenA, reqA)` and `Authorize(workflowID, tokenA, reqB)` — both carrying the identical JWT (`tokenA`, same `jti`).
2. Goroutine 1 calls `utils.VerifyRequestJWT` (succeeds), then `h.jwtCache.isReplay(claims.ID)` → `false` (cache empty), lock released. [6](#0-5) 
3. Before goroutine 1 reaches `recordUsage`, goroutine 2 also calls `isReplay(claims.ID)` → still `false` (goroutine 1 hasn't recorded yet).
4. Both goroutines pass the `authorizedKeys` signer check (same key, both authorized) and both call `recordUsage(claims.ID)`, both succeeding with `nil` error and a valid `*gateway.AuthorizedKey` returned.
5. Result: the single-use JWT `tokenA` authorized two separate requests, violating the intended one-time-use guarantee that the existing replay test (`TestWorkflowMetadataHandler_Authorize/"JWT replay protection"`) only verifies for the strictly sequential case: [7](#0-6) 
That test never exercises concurrent calls, so it does not catch this race.

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L92-104)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L105-108)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler_test.go (L1193-1217)
```go
	t.Run("JWT replay protection", func(t *testing.T) {
		params := json.RawMessage(`{"test": "data"}`)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id-replay",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &params,
		}

		token, err := utils.CreateRequestJWT(*req)
		require.NoError(t, err)

		tokenString, err := token.SignedString(privateKey)
		require.NoError(t, err)

		key, err := handler.Authorize(workflowID, tokenString, req)
		require.NoError(t, err)
		require.NotNil(t, key)

		// Second authorization with same JWT should fail (replay attack)
		key, err = handler.Authorize(workflowID, tokenString, req)
		require.Error(t, err)
		require.Contains(t, err.Error(), "JWT token has already been used. Please generate a new one with new id (jti)")
		require.Nil(t, key)
	})
```
