### Title
JWT replay-guard TOCTOU race in `WorkflowMetadataHandler.Authorize` allows duplicate workflow execution from a single signed HTTP trigger token - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
The Olympus report's root cause is a check-then-act pattern (`balanceBefore`/`balanceAfter`) that is not atomic with respect to an interleaved external call, letting an attacker consume the same value twice across two nominally-protected code paths. The same structural bug class exists in chainlink's gateway HTTP-trigger authentication path: the JWT single-use replay check (`isReplay`) and the corresponding "mark used" step (`recordUsage`) are two separate, independently-locked operations rather than one atomic check-and-set, so two concurrent requests carrying the identical signed JWT can both pass the replay check before either records usage.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the function that authenticates an unprivileged, internet-facing HTTP trigger request before it is dispatched to workflow nodes to start a workflow execution: [1](#0-0) 

The replay guard itself, `jwtReplayCache`, exposes two separate methods, `isReplay` (read lock) and `recordUsage` (write lock), that are invoked non-atomically by the caller: [2](#0-1) 

In `Authorize`, the sequence is: verify JWT signature → `isReplay(claims.ID)` check → look up authorized keys → `recordUsage(claims.ID)`. Between the `isReplay` check and the `recordUsage` call there is no mutex held across the whole sequence — each call only locks/unlocks the `jwtReplayCache.mu` for its own operation. If the gateway receives two concurrent HTTP trigger requests bearing the exact same valid, signed JWT (same `jti`), both goroutines can call `isReplay` and observe "not yet seen" before either calls `recordUsage`. Both then pass authorization and both proceed to `checkRateLimit` and workflow dispatch in `httpTriggerHandler.HandleUserTriggerRequest`.

This mirrors the Olympus bug class precisely: two logically-independent operations (`Operator::swap`'s reserve transfer vs. `OlympusTreasury::repayLoan`'s balance diff) that are each individually guarded (`nonReentrant` on each contract) but are not atomic with respect to each other, allowing state that should be single-use/consistent to be consumed twice.

### Impact Explanation
A single valid signed JWT (a workflow owner's authorization token for one HTTP trigger execution) can be replayed to trigger **two (or more) concurrent workflow executions** instead of the intended one, if the two requests race before the cache write commits. This defeats the explicit purpose of `jwtReplayCache` ("prevent replay attacks") and the associated per-workflow-owner rate limiting is only checked after authorization (`checkRateLimit` happens after `authorizeRequest` in `HandleUserTriggerRequest`), so a duplicated request could also cause duplicate billing/metering, duplicate side effects from the workflow (e.g., external actions performed twice), or resource strain on the DON. This is a request-impersonation/duplicate-authorization class issue directly reachable by an unprivileged internet-facing client (anyone in possession of one valid signed trigger request), which fits the "cross-user response confusion" / "unauthorized job run" acceptance criteria.

### Likelihood Explanation
Exploitation requires only sending the same HTTP request (with its JWT) twice in rapid succession/concurrently, e.g. via two parallel HTTP connections timed to land within the tiny window between the `isReplay` read and the `recordUsage` write. This window is a few microseconds to milliseconds, but is a genuine, network-reachable race that a client fully controls (client can retry/duplicate requests at will, e.g. through parallel sockets or infra-level connection retries), so it can be reliably triggered with a moderate amount of concurrent request flooding of the identical payload. No special privilege or secret beyond having one legitimate signed JWT (which the workflow owner is expected to have as it authorizes their own request) is required.

### Recommendation
Make the check-and-record step atomic: hold the `jwtReplayCache.mu` write lock for the entire "check `isReplay`, then `recordUsage`" sequence (or provide a single `CheckAndRecord`-style method, analogous to the one already correctly implemented in `core/capabilities/vault/request_replay_guard.go`), and call it as one atomic operation from `Authorize` rather than as two independently-locked steps. Additionally, consider moving the replay-check-and-record to occur immediately upon signature verification, before any other work, to shrink any remaining window.

### Proof of Concept
1. A workflow owner obtains a validly signed JWT trigger request for `MethodWorkflowExecute` with a given `jti`.
2. Attacker (or a buggy retrying client) sends the identical request+JWT twice concurrently to the gateway's HTTP trigger endpoint (two parallel connections).
3. Both goroutines execute `WorkflowMetadataHandler.Authorize`:
   - Goroutine A: `isReplay(jti)` → false (not yet recorded)
   - Goroutine B: `isReplay(jti)` → false (A hasn't called `recordUsage` yet)
   - Goroutine A: passes authorized-keys check, calls `recordUsage(jti)`
   - Goroutine B: passes authorized-keys check (same key lookup succeeds), calls `recordUsage(jti)` (now a no-op overwrite, but authorization was already granted)
4. Both requests proceed to `httpTriggerHandler.HandleUserTriggerRequest` → `checkRateLimit` → dispatch to DON nodes, producing two workflow executions from one signed authorization, confirmed by the existing test `TestWorkflowMetadataHandler_Authorize/"JWT replay protection"` which only demonstrates the sequential (non-concurrent) case succeeds in blocking replay — it does not cover the concurrent race window. [3](#0-2)

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
