### Title
JWT single-use replay protection has a check-then-act race allowing token reuse - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The `Authorize` method on `WorkflowMetadataHandler` implements single-use JWT (`jti`) protection for HTTP-trigger workflow-execution requests using a check-then-act pattern that is not atomic: `isReplay()` is called under one lock acquisition and `recordUsage()` is called under a separate, later lock acquisition, with unauthorized-key/business logic executed in between. This mirrors the reported `EscrowManager._findCheckpoint` bug class, where non-atomic, order-dependent state updates that assume sequential, single-shot execution break down under concurrent/simultaneous execution, corrupting the intended bookkeeping (there: checkpoints/voting weight; here: JWT replay cache).

### Finding Description
`jwtReplayCache.isReplay` and `jwtReplayCache.recordUsage` each acquire and release their own lock independently: [1](#0-0) 

`Authorize` calls them non-atomically, with a "check" at the top and a "record" only at the very end, after JWT signature verification and workflow/signer authorization checks: [2](#0-1) 

Because there is no lock held across the whole `Authorize` call, two goroutines processing the same JWT concurrently (e.g., two nearly-simultaneous HTTP trigger requests carrying an identical signed JWT/`jti`) can both pass `isReplay(claims.ID)` (both observe `false`) before either calls `recordUsage(claims.ID)`. Both requests then proceed to be authorized and dispatched to the workflow DON as legitimate, distinct trigger executions, exactly as the existing regression test intends to prevent for sequential calls: [3](#0-2) [4](#0-3) 

This is directly analogous to the `EscrowManager` bug: the contract's checkpoint bookkeeping assumed checkpoints could not be created "at the same time" and thus its increment/lookup logic broke under concurrent operations at the same timestamp, silently corrupting state (votes reset to zero). Here, the JWT anti-replay bookkeeping assumes `isReplay`+`recordUsage` execute atomically per JWT, and breaks under concurrent invocation with the same `jti`, silently allowing replay.

### Impact Explanation
An unprivileged caller who can submit an HTTP trigger request (the JWT is attached and verified per-request, not tied to a privileged principal) can race two copies of the same signed JWT to the gateway. If both requests are processed by racing goroutines before either records usage, the single-use guarantee is bypassed and the same JWT authorizes two (or more) separate `WorkflowExecute` dispatches to the DON. This is a concrete authentication/replay-protection bypass in the internet-facing HTTP trigger gateway path, potentially causing duplicate/unintended workflow executions from a single signed request — undermining the anti-replay guarantee the code explicitly documents and tests for.

### Likelihood Explanation
Likelihood is realistic but not guaranteed: it requires winning a narrow race window (the interval between the `isReplay` check and the corresponding `recordUsage` call, encompassing JWT signature verification and authorized-key lookups) by sending duplicate requests concurrently, which an external caller fully controls (can fire many parallel copies to increase odds). Unlike the Solidity report's deterministic same-`block.timestamp` trigger, this is a network-timing race, so it is probabilistic rather than deterministic, but it is trivially triggerable by any caller capable of sending two HTTP requests at once. Note that `RequestReplayGuard` (used elsewhere in `core/capabilities/vault`) correctly performs check+record under a single mutex acquisition and does not have this flaw; only the `jwtReplayCache` used by `WorkflowMetadataHandler.Authorize` is affected.

### Recommendation
Make the check-and-record operation atomic: hold a single lock (or use a `sync.Map`/`LoadOrStore`-style primitive) across the entire "is `jti` already used → record `jti`" sequence, similar to how `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go` performs both operations under one `mu.Lock()`. Concretely, replace `isReplay`/`recordUsage` in `jwtReplayCache` with a single `CheckAndRecord(jti string) bool` method that checks-and-inserts atomically, and call it once in `Authorize` immediately after JWT verification, before the (possibly slower) authorized-key checks — or at minimum, ensure no other goroutine can observe an unrecorded `jti` between the check and the record for the same token.

### Proof of Concept
Not directly executable from this analysis (would require constructing two goroutines invoking `WorkflowMetadataHandler.Authorize` concurrently with the same JWT/`jti` and asserting both succeed under a slow/instrumented `authorizedKeys` lookup to widen the race window — analogous to the existing sequential test at `workflow_metadata_handler_test.go:1193-1217`, but issuing the two `Authorize` calls in parallel goroutines instead of sequentially). I was unable to execute code to confirm the race is winnable in practice; this assessment is based on static analysis of the non-atomic lock usage shown above.

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
