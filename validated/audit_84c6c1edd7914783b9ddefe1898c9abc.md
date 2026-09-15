Based on my review, the vulnerable code exactly matches the claim: `Authorize` calls `h.jwtCache.isReplay(claims.ID)` (a separate `RLock`-protected read) at [1](#0-0)  and only records usage via a separate `Lock`-protected write at [2](#0-1) , after other authorization work (workflow lookup, signer lookup) intervenes. The `jwtReplayCache` methods themselves are shown at [3](#0-2) , confirming the check and record are two independently-locked critical sections rather than one atomic operation, unlike `RequestReplayGuard.CheckAndRecord` elsewhere in the codebase.

However, I was unable to fully verify whether this race is actually exploitable end-to-end, because `Authorize` is only one step in the request pipeline. In `httpTriggerHandler.HandleUserTriggerRequest`, after `authorizeRequest` succeeds, the code proceeds to `setupCallback`, which takes `h.callbacksMu.Lock()` and checks `h.callbacks[requestID]` for an existing entry with the *same* JSON-RPC `req.ID`, rejecting duplicates with a `ErrConflict`/"in-flight request" error [4](#0-3) . Since a genuine replay attack replays the identical request (same body, same JWT, same `req.ID`), this second independent dedup check — confirmed by the existing test `TestHttpTriggerHandler_HandleUserTriggerRequest/duplicate_request_id` [5](#0-4)  — would very plausibly still block the second concurrent dispatch to DON nodes even if the JWT-level race succeeds. I could not confirm within available context whether `claims.ID` (jti) is cryptographically bound to `req.ID`, or whether an attacker could vary `req.ID` while keeping the same JWT signature valid (which would require inspecting `VerifyRequestJWT`/`CreateRequestJWT` in `core/utils/jwt.go`, which I was unable to load in full). This matters because if `req.ID` is part of what the JWT signs/digests, then bypassing only the `isReplay` check without also bypassing the `setupCallback` requestID dedup would not actually cause duplicate downstream execution — undermining the claimed "concrete... duplicate/unauthorized workflow execution requests dispatched to DON nodes" impact.

That said, the race condition in `isReplay`/`recordUsage` is real as a code-level defect (a TOCTOU gap independent of whether a second layer of defense happens to also exist), and the report accurately cites the code, root cause, and a concrete, correct fix pattern (`CheckAndRecord`) already used elsewhere in the codebase. The report's core technical claim — the check-then-act race in the JWT replay cache — is verified as present in the code as described.

Audit Report

## Title
JWT replay-protection check-then-record race allows replay of a workflow-trigger JWT - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

## Summary
`WorkflowMetadataHandler.Authorize` checks for JWT replay via `jwtCache.isReplay(claims.ID)` under a read lock, then performs workflow/signer authorization, and only afterward records usage via `jwtCache.recordUsage(claims.ID)` under a separate write lock. Because the check and the record are not a single atomic critical section, two concurrent `Authorize` calls carrying the same JWT `jti` can both pass the replay check before either records usage, allowing a single-use JWT to be authorized more than once at the `Authorize` layer.

## Finding Description
The replay guard is split into two independently-locked operations, `isReplay` (RLock) and `recordUsage` (Lock), with unrelated logic (workflow/signer lookups) executed between them inside `Authorize` [6](#0-5) . The cache implementation itself confirms these are two separate mutex-protected sections rather than one atomic check-and-insert [3](#0-2) . This is structurally the same TOCTOU pattern already correctly avoided elsewhere in the codebase by `RequestReplayGuard.CheckAndRecord`, which performs the existence check and insertion under a single lock [7](#0-6) . Two concurrent calls to `Authorize` with the same `jti` can both observe `exists == false` at line 87 before either reaches line 105, letting both proceed past the replay guard.

At the `WorkflowMetadataHandler.Authorize` layer alone, this is a genuine bypass of the intended single-use guarantee of the JWT.

## Impact Explanation
Whether this race translates into duplicate downstream workflow execution against DON nodes depends on a second, independent dedup check in `httpTriggerHandler.setupCallback`, which rejects a second request sharing the same JSON-RPC `req.ID` with an in-flight conflict error [4](#0-3) , as demonstrated by the existing `duplicate request ID` test [5](#0-4) . Since a true replay of an identical request would also carry the identical `req.ID`, this second layer likely prevents the race from producing duplicate execution against DON nodes in the straightforward replay scenario. I could not fully confirm within the available context whether `req.ID` is bound to the JWT signature (via `VerifyRequestJWT`/`CreateRequestJWT` in `core/utils/jwt.go`), which is necessary to determine if an attacker could vary `req.ID` to route around the `setupCallback` dedup while keeping the same `jti` accepted twice by the race. Absent that confirmation, the concrete "duplicate workflow execution" impact described in the original claim is not fully substantiated end-to-end, even though the code-level race in `isReplay`/`recordUsage` is real.

## Likelihood Explanation
The `isReplay`/`recordUsage` race itself is trivially reachable by any unprivileged external caller who can fire two near-simultaneous identical HTTP trigger requests, requiring no privileged access. Its practical severity is bounded by the additional `setupCallback` requestID-based dedup layer, whose interaction with JWT `jti` binding is unverified here.

## Recommendation
Merge `isReplay` and `recordUsage` into one atomic "check-and-record" operation under a single lock, mirroring `RequestReplayGuard.CheckAndRecord`, so the accept-decision and the state mutation are indivisible — this closes the race regardless of what other dedup layers exist downstream, and removes reliance on `req.ID`-based deduplication as an incidental mitigating control.

## Proof of Concept
1. Craft one valid signed JWT for a request with a fixed `jti` and `req.ID` for an authorized workflow/signer.
2. Fire two concurrent calls to `WorkflowMetadataHandler.Authorize` with the same token/request from two goroutines.
3. Observe (via added instrumentation or a tight unit test around `isReplay`/`recordUsage`) that both calls can pass the `isReplay` check before either calls `recordUsage`, both returning a successful `*gateway.AuthorizedKey`.
4. To determine full end-to-end exploitability, additionally verify in `core/utils/jwt.go` whether `req.ID` is part of the JWT-signed digest; if not, test whether varying `req.ID` while reusing `jti` bypasses `setupCallback`'s per-`req.ID` dedup and reaches `sendWithRetries` twice.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L320-358)
```go
	t.Run("duplicate request ID", func(t *testing.T) {
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
		req.Auth = createTestJWTToken(t, req, privateKey)
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback2, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "in-flight request")

		r, err := callback2.Wait(t.Context())
		require.NoError(t, err)
		requireUserErrorSent(t, r, jsonrpc.ErrConflict)
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
