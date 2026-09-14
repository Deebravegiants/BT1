I found a genuine TOCTOU race in the JWT single-use replay protection that maps to the "check-then-use-of-a-since-invalidated-token" temporal flaw pattern highlighted by CVE-2022-3640 (an operation validated a state that had already changed underneath it, "check → free → use"). Here the analogous flaw is "check → concurrent-use → record" instead of atomic check-and-set.

### Title
JWT single-use replay protection is bypassable via a check-then-act race, allowing duplicate authorized workflow-trigger execution - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`Authorize` checks `jwtCache.isReplay(claims.ID)` and only marks the JWT ID as used via `jwtCache.recordUsage(claims.ID)` after several more steps (workflow lookup, signer authorization), with **no lock held across the whole sequence**. Two concurrent requests carrying the same valid, signed JWT can both pass the `isReplay` check before either calls `recordUsage`, defeating the intended single-use guarantee.

### Finding Description
`jwtReplayCache` uses a `sync.RWMutex` but only protects each individual map access, not the read-check-then-write sequence: [1](#0-0) 

`Authorize` calls `isReplay` early, then performs workflow/authorized-key lookups, and only calls `recordUsage` at the very end: [2](#0-1) 

This is reachable by an unprivileged, externally-facing HTTP trigger request through `httpTriggerHandler.HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize`, part of the internet-facing gateway's HTTP trigger message path: [3](#0-2) 

The project's own tests confirm the *intended* behavior is single-use enforcement (sequential duplicate JWT is rejected): [4](#0-3) 

But that test only exercises the sequential case; nothing in the code enforces atomicity between the `isReplay` check and `recordUsage`, so two goroutines racing through `Authorize` concurrently (e.g., two copies of the request replayed at once by a network intermediary or a malicious client) can both observe `isReplay() == false` and both proceed to trigger the workflow with the same JWT before either one calls `recordUsage`.

### Impact Explanation
The JWT `jti` replay-cache is the sole mechanism preventing a captured/replayed signed trigger request from being executed more than once. Bypassing it allows an unprivileged external caller to trigger duplicate workflow executions from a single valid signed request (request impersonation/duplication of an already-authorized action), which can cause duplicate side effects (e.g., duplicate on-chain/off-chain workflow runs) depending on what the target workflow does. It does not grant unauthorized access to a workflow the attacker isn't already authorized to invoke, so the impact is bounded to duplicate-execution/anti-replay bypass rather than full authentication bypass.

### Likelihood Explanation
Requires two nearly-simultaneous requests with the identical valid JWT to hit `Authorize` concurrently — feasible for any client capable of sending two parallel HTTP requests with the same signed token (which the caller controls, since they hold the private key or captured the token), or via network-level duplication/replay of a single request. No special network position or node compromise is needed, satisfying "unprivileged actor" reachability.

### Recommendation
Make the "check-not-replayed" and "mark-as-used" operations atomic under a single lock held by `jwtReplayCache`, e.g., add a `CheckAndRecord(jti string) (alreadyUsed bool)` method that holds `mu.Lock()` for the entire check-and-set, and call it once from `Authorize` immediately after JWT verification (before any lookups), replacing the separate `isReplay`/`recordUsage` calls.

### Proof of Concept
1. Attacker crafts a single valid signed HTTP trigger request (`req.Auth = jwtToken`) for a workflow they are authorized to invoke.
2. Attacker fires the identical request (same body, same JWT, same `jti`) twice concurrently (e.g., via two parallel HTTP connections or a proxy replaying the request mid-flight).
3. Both goroutines invoke `WorkflowMetadataHandler.Authorize` concurrently; both call `h.jwtCache.isReplay(claims.ID)` before either has called `recordUsage`, so both see `exists == false`.
4. Both requests pass authorization and are forwarded to `sendWithRetries`, resulting in two accepted/triggered workflow executions from what should be a single-use token — violating the anti-replay guarantee demonstrated as enforced (for the sequential case) in `TestHttpTriggerHandler_HandleUserTriggerRequest_JWTAuthorization`'s duplicate-JWT test.

**Caveat / uncertainty:** I could not find evidence of additional synchronization (e.g., an outer lock in `authorizeRequest` or `HandleUserTriggerRequest`) that might serialize concurrent calls to `Authorize` for the same request; based on the code reviewed, no such serialization exists, but a full concurrency audit of `httpTriggerHandler.authorizeRequest` (not fully retrieved) would be needed to rule out an outer-level mutex I haven't located via search.

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
