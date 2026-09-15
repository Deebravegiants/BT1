Based on my investigation, there is a concrete analog: the gateway's `jwtReplayCache`, which implements JWT (single-use, request-authorizing token) replay protection with a non-atomic check-then-record pattern — the same bug class as the CVE (TOCTOU race allowing single-use credential reuse via concurrent requests).

### Title
JWT Replay Protection Race Condition (TOCTOU) in Gateway `jwtReplayCache` - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The Chainlink gateway protects HTTP-trigger workflow-execution requests from JWT replay using an in-memory `jwtReplayCache` [1](#0-0) . The cache exposes separate `isReplay` (read-lock check) and `recordUsage` (write-lock insert) methods rather than a single atomic check-and-set operation [2](#0-1) . This mirrors the CVE's root cause in `JCacheCodeDataProvider`: the "is this code/token already used" check and the "mark it used" write are two separate operations, leaving a race window.

### Finding Description
`jwtReplayCache.isReplay(jti)` acquires `cache.mu.RLock()`, checks map membership, and releases the lock [3](#0-2) . `jwtReplayCache.recordUsage(jti)` separately acquires `cache.mu.Lock()` and inserts the entry [4](#0-3) . Because these are two independent lock acquisitions rather than one atomic "check-and-insert" (e.g., a single `LoadOrStore`), two concurrent requests carrying the *same* JWT (`jti`) can both call `isReplay` before either calls `recordUsage`, both observe "not yet used," and both proceed to be treated as valid, distinct authorized requests — exactly the concurrent-request replay pattern described in the CVE report.

The test suite's existing "duplicate JWT token and request ID" case confirms replay is normally rejected sequentially with error "token has already been used" [5](#0-4) , which validates that this mechanism is the intended single-use enforcement point for gateway workflow-trigger requests — but the test only exercises the sequential (non-concurrent) path, not truly simultaneous racing calls, so the TOCTOU window is not covered by existing tests.

I was not able to fully trace the exact call site in `http_trigger_handler.go` that invokes `isReplay`/`recordUsage` together (only one textual match was found there before the iteration budget was exhausted), so I cannot confirm with certainty whether callers wrap both calls under one already-held lock or a higher-level mutex that would close the race. This should be verified directly in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go` before treating this as fully confirmed.

### Impact Explanation
If the race is exploitable, an attacker who can issue two near-simultaneous requests with the same signed JWT could bypass the single-use / anti-replay guarantee for gateway-triggered workflow executions, allowing duplicate execution of a workflow trigger from one token — analogous to obtaining multiple valid "sessions"/executions from one authorization artifact, as in the CVE. This is a request-impersonation / anti-replay bypass reachable by an unprivileged external caller of the gateway's HTTP trigger path.

### Likelihood Explanation
Requires an attacker to race two requests with an already-obtained valid JWT against the gateway within a very small window (lock hold time is microseconds), so likelihood is Low-to-Medium — comparable to the CVE's own AC:H (high attack complexity) rating for the same bug class.

### Recommendation
Replace the separate `isReplay`/`recordUsage` calls with a single atomic check-and-insert operation (e.g., hold the write lock across both the existence check and the insert, or use `sync.Map.LoadOrStore` keyed by `jti`) so that only one of two racing requests can ever pass the replay check.

### Proof of Concept
Not independently reproduced; concurrency PoC would require two goroutines issuing `HandleUserTriggerRequest` with an identical `req.Auth` JWT simultaneously and asserting whether both are accepted, but I could not confirm the exact call-site locking behavior in `http_trigger_handler.go` within available tool budget — this must be verified by reading that file directly.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L29-34)
```go
// jwtReplayCache manages used JWT IDs to prevent replay attacks
type jwtReplayCache struct {
	mu            sync.RWMutex
	cleanupPeriod time.Duration
	cache         map[string]time.Time // jti -> timestamp
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
