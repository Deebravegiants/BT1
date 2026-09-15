Confirmed: `Authorize` calls `h.jwtCache.isReplay(claims.ID)` at line 87 and, after several unrelated checks (workflow lookup, signer authorization), calls `h.jwtCache.recordUsage(claims.ID)` only at line 105 — with no lock held across the two calls and no other mutex serializing concurrent `Authorize` invocations for the same `jti`. [1](#0-0)  This confirms the claim's core assertion.

Audit Report

## Title
JWT Replay Protection Race Condition (TOCTOU) in `WorkflowMetadataHandler.Authorize` / `jwtReplayCache` - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` checks whether a JWT's `jti` has already been used via `h.jwtCache.isReplay(claims.ID)` and, only after performing workflow/signer lookups, marks it used via `h.jwtCache.recordUsage(claims.ID)`. [2](#0-1)  These are two independent, non-atomic lock acquisitions on `jwtReplayCache.mu` (`RLock` for the check, `Lock` for the record), so two concurrent requests carrying the same signed JWT can both pass `isReplay` before either calls `recordUsage`. [3](#0-2) 

## Finding Description
The call chain is: gateway receives an HTTP-trigger request → `httpTriggerHandler.HandleUserTriggerRequest` → `authorizeRequest` → `WorkflowMetadataHandler.Authorize(workflowID, req.Auth, req)`. [4](#0-3)  Inside `Authorize`, the replay check (`isReplay`) and the replay recording (`recordUsage`) are separated by workflow-ID lookup and signer-authorization logic, and each acquires the `jwtReplayCache.mu` lock independently rather than holding a single lock across the whole check-and-set. [1](#0-0)  There is no other synchronization (e.g., a mutex keyed by `jti`, or a `sync.Map.LoadOrStore`) protecting this sequence.

The `setupCallback` dedup logic in `http_trigger_handler.go` guards against duplicate `requestID`s [5](#0-4)  — but this runs *after* `authorizeRequest`/JWT check, and only protects against reuse of the same JSON-RPC request ID, not the same JWT. An attacker could therefore submit two concurrent requests with different `requestID`s (satisfying `setupCallback`'s dedup) but an identical signed JWT (same `jti`), racing the `Authorize` call so both pass `isReplay` before either records usage in `jwtReplayCache`. This would let a single valid JWT trigger two workflow executions instead of one, violating the single-use guarantee that the existing sequential test enforces. [6](#0-5) 

## Impact Explanation
If exploited, this allows an unprivileged external caller who has obtained one valid, signed JWT (which they would legitimately possess as an authorized key holder, or could replay if intercepted) to trigger duplicate workflow executions from a single-use credential — a concrete anti-replay / gateway request-impersonation bypass affecting workflow-trigger execution integrity, consistent with the "gateway request impersonation" impact class.

## Likelihood Explanation
Exploitation requires an attacker to send two requests carrying the identical signed JWT within the narrow window between the `isReplay` read and the `recordUsage` write in `Authorize` (bounded by workflow-ID resolution and map lookups, likely low microseconds), making it a low-probability but technically real race; it also requires the attacker to already possess (or intercept) a valid single-use JWT and to be able to fire near-simultaneous requests to the gateway, which is feasible for any external client capable of concurrent HTTP calls.

## Recommendation
Make the check-and-record atomic: acquire `jwtReplayCache.mu.Lock()` (write lock) once, check `cache[jti]` existence, and if absent, insert it, all under the same critical section (or replace the map with a `sync.Map` and use `LoadOrStore(jti, time.Now())`, returning "already used" if `loaded == true`). Perform this "claim" operation as the very first step of `Authorize`, before any further request-Auth-JWT verification, and reject with the "already used" error if the claim fails.

## Proof of Concept
Write a Go test that spins up two goroutines calling `WorkflowMetadataHandler.Authorize(workflowID, token, req)` (or `httpTriggerHandler.HandleUserTriggerRequest`) simultaneously with the same valid JWT (`req.Auth`) but two different `req.ID`s, using a registered workflow/authorized key as in the existing `createTestTriggerHandler`/`registerWorkflow` test helpers. [7](#0-6)  Insert a small synchronization barrier (e.g., a channel) so both goroutines call `isReplay` before either calls `recordUsage`, then assert both calls return success — demonstrating the single-use guarantee is bypassed under concurrency, unlike the existing sequential-only test.

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
