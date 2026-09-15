## Analysis Result

### Title
JWT replay guard in the Gateway HTTP Trigger handler uses non-atomic check-then-act, allowing concurrent replay of the same signed workflow-trigger request - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
The reported TokenLocker bug is a class of vulnerability where a state check and the corresponding state update that should be atomic are split into two separate operations, so a stale/pre-update value is used to make a security-relevant decision. The Chainlink Gateway's `jwtReplayCache`, which is meant to guarantee a signed HTTP-trigger JWT can only be used once, exhibits the same class of bug: the "already used?" check and the "mark as used" update are two independently-locked operations rather than one atomic operation, unlike the vault package's equivalent `RequestReplayGuard.CheckAndRecord`, which correctly performs the check-and-record under a single critical section.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the function that enforces JWT single-use semantics for the internet-facing HTTP Trigger capability of the Gateway: [1](#0-0) 

It calls `h.jwtCache.isReplay(claims.ID)` to check whether a JWT ID (`jti`) has been seen before, and only later — after resolving the authorized key — calls `h.jwtCache.recordUsage(claims.ID)` to mark it used. These two calls acquire and release the cache's mutex independently: [2](#0-1) 

Because `isReplay` (RLock) and `recordUsage` (Lock) are not combined into one atomic "check-and-record" critical section, two goroutines processing two concurrent HTTP-trigger requests carrying the exact same signed JWT can both execute `isReplay` and observe `false` before either one executes `recordUsage`. Both requests then pass the replay check and proceed to `authorizeRequest` -> `HandleUserTriggerRequest`, ultimately dispatching the *same* signed, single-use JWT to trigger the workflow twice (or more) concurrently: [3](#0-2) 

This is directly analogous to the TokenLocker bug: a value used in a security-relevant decision (`totalDecayRate` / "has this JWT been used") is read before the mutating side-effect (`totalDecayRate -= lockedPlusPenalties` / `recordUsage`) has committed, letting the same input be “spent” more than once. The existing regression tests only exercise this sequentially (`"duplicate JWT token and request ID"`), which cannot detect a TOCTOU race, so the non-atomicity has gone unnoticed: [4](#0-3) 

For comparison, the Vault capability's equivalent replay guard was implemented correctly, performing the check and the record under a single lock so no such race is possible: [5](#0-4) 

### Impact Explanation
The JWT-based auth model for the Gateway's HTTP Trigger capability is explicitly designed so that a signed request (JWT with a given `jti` bound to a specific request digest) can be used exactly once — this is the core anti-replay/anti-impersonation guarantee for an unprivileged, internet-facing endpoint. The race in `jwtReplayCache` breaks that guarantee under concurrency: an attacker (or a buggy/duplicate client) who fires the same signed trigger request twice in quick succession can cause the workflow to be triggered multiple times using a JWT that was only supposed to authorize a single execution. This can lead to duplicate/unauthorized workflow executions (unauthorized job runs), which for workflows that move funds or trigger on-chain side effects is a direct integrity and fund-movement risk, in addition to violating the single-use security property that the "token has already been used" error message promises callers.

### Likelihood Explanation
This requires only sending two (or more) copies of the same already-signed request concurrently to the Gateway, something any client that can reach the internet-facing HTTP Trigger endpoint can do without any special privilege — no on-chain access, no node compromise, and no cryptographic break is needed. Winning the race is a matter of timing (both goroutines must interleave between `isReplay` and `recordUsage`), which is a common outcome under real network conditions where a client or intermediary naturally retries/duplicates requests.

### Recommendation
Merge the check and the record into a single atomic critical section, the same way `vault.RequestReplayGuard.CheckAndRecord` does, e.g.:
```go
func (cache *jwtReplayCache) checkAndRecord(jti string) bool {
    cache.mu.Lock()
    defer cache.mu.Unlock()
    if _, exists := cache.cache[jti]; exists {
        return false // replay
    }
    cache.cache[jti] = time.Now()
    return true
}
```
and update `Authorize` to call this single atomic method instead of the separate `isReplay` + `recordUsage` calls, rejecting the request immediately if it returns false.

### Proof of Concept
1. Create a valid signed JWT for a `WorkflowExecute` request using `utils.CreateRequestJWT`, as done in `workflow_metadata_handler_test.go`'s `"JWT replay protection"` subtest.
2. Instead of calling `handler.Authorize(workflowID, tokenString, req)` twice sequentially (as the existing test does), spawn two goroutines that call it concurrently with the same `tokenString`/`req`, e.g.:
```go
var wg sync.WaitGroup
results := make([]error, 2)
wg.Add(2)
for i := 0; i < 2; i++ {
    go func(i int) {
        defer wg.Done()
        _, err := handler.Authorize(workflowID, tokenString, req)
        results[i] = err
    }(i)
}
wg.Wait()
```
3. Under the current implementation, both calls can observe `isReplay(jti) == false` before either calls `recordUsage(jti)`, so both `results[0]` and `results[1]` can be `nil` (success) instead of exactly one succeeding and one returning "JWT token has already been used" — demonstrating that the single-use guarantee is not enforced atomically.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-106)
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
