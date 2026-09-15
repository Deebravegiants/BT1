Audit Report

## Title
JWT replay-guard TOCTOU allows one-time HTTP-trigger token to authorize multiple concurrent workflow executions - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` checks whether a JWT `jti` has already been used via `isReplay` and only marks it as consumed via `recordUsage` at the very end of the function, with unrelated authorization work executed in between and no lock held across the whole sequence. Since Go's `net/http` server dispatches each incoming request on its own goroutine, an unprivileged external client can send multiple concurrent HTTP trigger requests bearing the identical single-use JWT, and any of them that reach the `isReplay` check before the first `recordUsage` commits will be treated as authorized, resulting in duplicate workflow executions from a single one-time-use token.

## Finding Description
The single-use guarantee for HTTP trigger JWTs is intended to be atomic (check-then-set), but it is implemented as two independently locked operations: [1](#0-0) 
called from `Authorize` at lines 87 and 105 with the authorized-key lookup logic executed in between and with no lock held across the whole span: [2](#0-1) 

`Authorize` is reached directly from `authorizeRequest`, which is called from `HandleUserTriggerRequest` — the entry point for external, unauthenticated HTTP trigger requests — before rate limiting is applied: [3](#0-2) [4](#0-3) 

Because `isReplay` (`RLock`) and `recordUsage` (`Lock`) are separate critical sections rather than a single atomic check-and-set, two concurrent requests carrying the same `jti` can both observe `isReplay == false` before either calls `recordUsage`, both of them passing authorization. An existing test only validates the *sequential* case (`"JWT token has already been used"`) and does not exercise the concurrent race: [5](#0-4) 

Notably, the codebase already contains a correct atomic pattern for this exact problem — `RequestReplayGuard.CheckAndRecord`, which performs the seen-check and insert under a single lock — showing the check-and-set-in-one-lock approach is the established, achievable fix elsewhere in the code: [6](#0-5) 

## Impact Explanation
An attacker holding a single-use signed HTTP-trigger JWT can dispatch multiple concurrent requests with that same token and cause more than one to be authorized and trigger a workflow execution, defeating the intended one-time-use control on that credential and bypassing the implicit per-token quota (rate limiting only runs after `authorizeRequest` succeeds). This maps to an in-scope "unauthorized job run" / authentication-bypass class of impact for the CRE Gateway's HTTP trigger path.

## Likelihood Explanation
The race window is real but narrow — it exists only between the `isReplay` read and the `recordUsage` write inside a single `Authorize` call, and is only exploitable while two requests bearing the identical JWT happen to interleave during that brief span. It requires no privileged role, network position, or node compromise — any external client capable of sending JSON-RPC gateway requests with the same JWT concurrently (e.g., via HTTP client goroutines/racing sockets) can attempt it, since each inbound HTTP connection is served on its own goroutine per standard `net/http` semantics. Exploitability is probabilistic (a genuine TOCTOU race) rather than deterministic, so success depends on timing, but it is a reproducible class of bug with realistic feasibility under load or a tight fan-out of requests.

## Recommendation
Make the check-and-record operation atomic by holding a single lock across both the lookup and insert — e.g., add a `CheckAndRecord(jti string) bool` method to `jwtReplayCache` mirroring the pattern in `RequestReplayGuard.CheckAndRecord`, and call it once from `Authorize` in place of the separate `isReplay`/`recordUsage` calls, ensuring the authorized-key lookup either occurs under the same lock or does not affect the atomicity of the replay-cache write.

## Proof of Concept
1. Register a workflow and obtain a valid signed HTTP-trigger JWT with `jti = X` for that workflow.
2. Fire two (or more) concurrent goroutines each calling `handler.HandleUserTriggerRequest` (or issuing concurrent HTTP requests to the gateway's `MethodWorkflowExecute` endpoint) with the identical token/`jti`.
3. Both goroutines independently call `WorkflowMetadataHandler.Authorize`, which invokes `h.jwtCache.isReplay(X)` before either goroutine reaches `h.jwtCache.recordUsage(X)`.
4. Observe that both calls return `isReplay(X) == false` and both proceed to authorize and trigger workflow execution — violating the intended single-use invariant. This can be demonstrated deterministically in a Go unit test by using a synchronization barrier (e.g., a channel/WaitGroup) to force both goroutines to call `isReplay` before either calls `recordUsage`.

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
