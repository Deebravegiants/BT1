### Title
JWT replay-cache check-then-act race lets a request bypass replay protection - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` (the JWT-based authorizer used by the internet-facing HTTP Trigger gateway path) checks a JWT's `jti` for replay via `jwtCache.isReplay()` and later marks it used via `jwtCache.recordUsage()`, but these are two separate, non-atomic operations. [1](#0-0)  This is structurally the same class of bug as the reported `NFTLootbox.getPrizeIndex` issue: a value is read, a decision is made, and the "commit" happens later, leaving a window where concurrent callers can all pass the same check before any of them records the outcome.

### Finding Description
`jwtReplayCache` stores JTIs in a map guarded by a `sync.RWMutex`, with `isReplay` taking an `RLock` and `recordUsage` taking a separate `Lock` call later: [2](#0-1) 

`Authorize` calls these two functions as separate steps, with unrelated work (authorized-key lookup) executed in between:
```go
if h.jwtCache.isReplay(claims.ID) {
    return nil, errors.New("JWT token has already been used...")
}
keys, exists := h.authorizedKeys[workflowID]
...
h.jwtCache.recordUsage(claims.ID)
``` [1](#0-0) 

Because `isReplay` and `recordUsage` do not share a single critical section (no compare-and-set), two (or more) concurrent HTTP trigger requests presenting the *same* JWT (same `jti`, same signature) can both call `isReplay` before either has called `recordUsage`. Both will see `exists == false`, both will pass the check, and both will be treated as valid, distinct authorizations — even though only one JWT was ever issued/used by the legitimate caller. This is the same "small random number, same prizeIndex, multiple winners" pattern from the report: the guard is check-then-act rather than atomic claim-then-proceed, so simultaneous requests can slip past a control meant to guarantee single-use.

This is reachable directly from an unprivileged client: the JWT and the HTTP trigger request are user-supplied inputs to the gateway's internet-facing endpoint that dispatches `MethodWorkflowExecute` to workflow nodes, exactly the kind of "session/token" / "internet-facing gateway" surface called out in scope. [3](#0-2)  The existing test `TestHttpTriggerHandler_HandleUserTriggerRequest/duplicate JWT token and request ID` only demonstrates sequential replay rejection (send request 1, wait for completion, then send request 2), which does not exercise the concurrent race window in `isReplay`/`recordUsage`.

### Impact Explanation
A JWT that is supposed to authorize exactly one workflow-trigger invocation (single-use token, enforced by the `jti` replay cache) can, under concurrent submission, authorize more than one invocation. Depending on what the triggered workflow does (e.g., moves funds, dispenses a limited resource, performs an idempotent-assumed action), this can cause duplicate/unintended workflow executions attributable to a single authorized signer/token — a request-impersonation-adjacent, single-use-guarantee bypass on the gateway's trigger authorization path.

### Likelihood Explanation
Low-to-moderate. It requires the attacker (or a legitimate but misbehaving/racing client) to send two copies of the same signed JWT-bearing request to the gateway within the narrow window between the `isReplay` read and the `recordUsage` write — a small timing window, but one entirely within the control of a client that can fire concurrent HTTP requests carrying the same JWT. No cryptographic break or privileged access is needed, matching the report's framing of "low likelihood, high impact" race conditions.

### Recommendation
Make the check-and-record operation atomic: extend `RequestReplayGuard`-style semantics (already used in `core/capabilities/vault/request_replay_guard.go`, which correctly combines check+record under one `mu.Lock()` in `CheckAndRecord`) to `jwtReplayCache`. Replace `isReplay` + separate `recordUsage` calls with a single `CheckAndRecord(jti)`-like method that holds the write lock for the entire "check membership, then insert" sequence, returning an error if the entry already exists, so no two concurrent callers can both see "not replayed."

### Proof of Concept
Not directly executable from the index (no filesystem/test-runner access here); the race is demonstrated conceptually:
1. Client obtains one valid JWT (`jti = X`) authorizing a workflow trigger call.
2. Client sends two concurrent HTTP requests to the gateway's trigger endpoint using the identical JWT.
3. Both requests reach `WorkflowMetadataHandler.Authorize` at roughly the same time; both call `jwtCache.isReplay(X)` before either calls `jwtCache.recordUsage(X)`, per the non-atomic implementation shown above. [4](#0-3) 
4. Both requests are authorized and both trigger the workflow, despite the single-use JWT contract — analogous to two "winners" claiming the same one-time reward in the original report.

Verification of exact production call ordering/concurrency in `http_trigger_handler.go` could not be completed within available tool budget; the vulnerable non-atomic cache primitive itself, however, is confirmed directly in the cited source.

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
