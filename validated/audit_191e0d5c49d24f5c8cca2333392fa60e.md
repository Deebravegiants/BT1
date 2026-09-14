### Title
JWT replay-protection check-then-act race allows a single trigger JWT to authorize multiple concurrent workflow executions - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The report describes a class of bug where a "have I already consumed this credit/reward" check and the corresponding "mark it as consumed" update are not applied atomically/consistently, letting an attacker pass the check multiple times for what should be a single-use credential. In `ExternalBribe`, this manifested as `prevRewards.timestamp` being advanced even when the reward wasn't actually credited, letting a user re-claim already-paid epochs. The closest reachable analog in this repo is the `jwtReplayCache` used to guard the internet-facing HTTP Trigger Gateway handler's one-time-use JWT (`jti`) check: the "is it replayed" check and "record it as used" write are two separate, independently-locked operations rather than one atomic check-and-set, creating a race window in which the same JWT can authorize more than one trigger execution.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the unprivileged-actor-facing entry point that validates a caller-supplied JWT for the `MethodWorkflowExecute` HTTP trigger flow: [1](#0-0) 

The replay-prevention primitive `jwtReplayCache` exposes two separate methods, each independently locked: [2](#0-1) 

`Authorize` calls `isReplay` (read lock) early, then does signature/authorized-key checks with no lock held, and only calls `recordUsage` (write lock) at the very end once fully authorized:
```go
if h.jwtCache.isReplay(claims.ID) { ... return error }
...
h.jwtCache.recordUsage(claims.ID)
return &key, nil
```
Because the "check" and the "record" are not performed under a single critical section (unlike the correctly-implemented `RequestReplayGuard.CheckAndRecord` in the Vault gateway handler, which combines check+record atomically under one mutex: [3](#0-2) ), two (or more) concurrent `Authorize` calls carrying the identical JWT/`jti` can both pass `isReplay` before either calls `recordUsage`. Both then proceed through `HandleUserTriggerRequest`, and the gateway will dispatch two DON-wide trigger broadcasts for the same nominally single-use JWT — analogous to the `prevRewards.timestamp` bug allowing a checkpoint's reward to be counted more than once because the guard state wasn't updated/consulted atomically with the eligibility check.

This mirrors the report's root cause pattern precisely: a stateful one-time-use gate (`prevRewards.timestamp` vs. `jwtCache`) whose update is not tightly coupled to the read that gates the privileged action, allowing the action to be repeated when it should be limited to once.

### Impact Explanation
A caller (any unprivileged client capable of obtaining/crafting a single valid workflow-trigger JWT, e.g. by replaying their own captured token concurrently) can cause the HTTP Trigger Gateway to authorize and dispatch the same trigger request to the DON multiple times instead of exactly once. This can cause duplicate workflow executions/duplicate on-chain or off-chain side effects billed or attributed to a single request, and undermines the explicit "duplicate JWT token and request ID" guarantee that the test suite asserts should fail on replay ( [4](#0-3) ). Impact is Medium: it does not directly leak secrets or bypass workflow-owner authorization, but it violates a security invariant (exactly-once trigger execution) that downstream systems may rely on for idempotency/billing/rate control.

### Likelihood Explanation
Likelihood is Medium: exploitation requires firing two requests carrying the same JWT close enough in time to land inside the narrow window between the `isReplay` read and the `recordUsage` write (which additionally spans the interior authorized-key/signature checks, widening the race window). This is a realistic race for a scripted attacker but not a trivial single-request exploit; it is a genuine concurrency bug rather than a purely theoretical one, since `HandleUserTriggerRequest`/`Authorize` is reachable directly from network input with no additional privilege.

### Recommendation
Make the replay-check-and-record atomic, following the same pattern already used correctly by `RequestReplayGuard.CheckAndRecord` in the Vault gateway handler: merge `isReplay` and `recordUsage` into a single method that holds one lock for the full duration of "check membership, and if absent, insert" (i.e., `if _, exists := cache.cache[jti]; exists { return ErrReplay }; cache.cache[jti] = time.Now(); return nil`), and have `Authorize` call this combined method exactly once, before any other authorization checks are performed, so a duplicate `jti` can never pass the gate twice regardless of concurrent callers.

### Proof of Concept
1. A caller obtains one valid signed JWT (`jti = X`) for a registered workflow, valid for `MethodWorkflowExecute`.
2. The caller fires two (or more) concurrent `HandleUserTriggerRequest` calls to the Gateway using the identical JWT.
3. Both goroutines execute `Authorize`: both call `h.jwtCache.isReplay(claims.ID)` before either has called `h.jwtCache.recordUsage(claims.ID)`, so both see `exists == false`.
4. Both goroutines pass the authorized-key checks (same key, same workflow) and both eventually call `recordUsage`, but by then both have already returned a valid `*gateway.AuthorizedKey` to their respective callers.
5. Both requests proceed through `HandleUserTriggerRequest` and get dispatched to DON nodes, resulting in two trigger executions credited to one JWT — violating the single-use invariant demonstrated by the existing replay test at [5](#0-4) , which only proves sequential (non-concurrent) replay is blocked.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L360-397)
```go
	t.Run("duplicate JWT token and request ID", func(t *testing.T) {
		handler, mockDon := createTestTriggerHandler(t)
		privateKey := createTestPrivateKey(t)
		registerWorkflow(t, handler, workflowID, privateKey)
		callback1 := hc.NewCallback()
		callback2 := hc.NewCallback()

		triggerReq := gateway_common.HTTPTriggerRequest{
			Workflow: gateway_common.WorkflowSelector{
				WorkflowID: workflowID,
			},
			Input: []byte(`{"key": "value"}`),
		}
		reqBytes, err := json.Marshal(triggerReq)
		require.NoError(t, err)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      requestID,
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}
		// First request should succeed
		req.Auth = createTestJWTToken(t, req, privateKey)
		mockDon.EXPECT().SendToNode(mock.Anything, mock.Anything, mock.Anything).Return(nil).Times(3)
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback1, time.Now())
		require.NoError(t, err)

		// Second request with same ID should fail
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback2, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "token has already been used")

		r, err := callback2.Wait(t.Context())
		require.NoError(t, err)
		requireUserErrorSent(t, r, jsonrpc.ErrInvalidRequest)
	})
```
