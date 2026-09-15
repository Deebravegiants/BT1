### Title
JWT replay-guard check-then-act race breaks single-use nonce mutual exclusion, allowing JWT reuse under concurrent requests - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
`WorkflowMetadataHandler.Authorize` implements JWT single-use (`jti`) replay protection by calling `jwtCache.isReplay(claims.ID)` and, later, `jwtCache.recordUsage(claims.ID)` as two separate, independently-locked operations rather than one atomic check-and-set. This is the same class of bug as the reported `spin` `RwLock` issue: an operation that is supposed to provide mutual exclusion (only one holder/one accepted use at a time) is implemented with a check and a subsequent write that are not synchronized as a single critical section, so two concurrent callers can both pass the check before either performs the write.

### Finding Description
`Authorize` is defined as: [1](#0-0) 

The relevant sequence is:
1. `h.jwtCache.isReplay(claims.ID)` takes `cache.mu.RLock()`, checks the map, and releases the lock.
2. Additional non-locked logic runs (`authorizedKeys` map lookup, signer authorization check).
3. `h.jwtCache.recordUsage(claims.ID)` takes `cache.mu.Lock()`, writes the entry, releases the lock.

`jwtReplayCache.isReplay`/`recordUsage` are implemented as two independent critical sections: [2](#0-1) 

Because the "check" and the "record" are not one atomic operation, two goroutines handling concurrent requests that carry the same JWT (same `jti`) can both execute `isReplay` and get `exists == false` before either has called `recordUsage`. Both then proceed to pass authorization for the same one-time JWT. This is a textbook check-then-act (TOCTOU) race that defeats the intended mutual-exclusion guarantee ("this JWT id can be consumed at most once").

Contrast with the correct pattern used elsewhere in the same codebase area (Vault authorizer), where the check and the record are combined into a single locked operation: [3](#0-2) 
That implementation is explicitly proven race-safe by a concurrency test: [4](#0-3) 

The `WorkflowMetadataHandler`'s `jwtReplayCache` has no equivalent combined `CheckAndRecord` primitive, and its test suite only demonstrates sequential (non-concurrent) replay rejection: [5](#0-4) 
which does not exercise the race window between `isReplay` and `recordUsage`.

`Authorize` is invoked from the gateway's capability handler path used to authorize workflow/HTTP trigger requests: [6](#0-5) 
This is the internet-facing gateway path that accepts requests carrying an unprivileged client- or workflow-supplied JWT.

### Impact Explanation
Reachable from the gateway's request-handling path, this race allows a single-use JWT nonce to be accepted twice (or more) if concurrent requests with the identical token race the gateway. In a JWT-based authorization scheme whose entire security property is "one signature, one use," this defeats the replay-prevention control and could enable request impersonation / duplicate authorized actions (e.g., duplicate workflow trigger authorization) using a token that was meant to be single-use, mirroring the mutual-exclusion violation in the original `spin` advisory (two "writers"/consumers gaining exclusive access simultaneously).

### Likelihood Explanation
Exploitability requires the attacker (or a legitimately racing client) to submit the same JWT concurrently to the gateway before the first request completes `recordUsage`. This is a narrow but realistic race window (the gap between the RLock-protected check and the later Lock-protected write, during which map lookups and signer verification run unlocked). It does not require any privileged access — only the ability to send two requests carrying the same previously-obtained token concurrently to the gateway endpoint that calls `Authorize`.

### Recommendation
Merge `isReplay` and `recordUsage` into a single atomically-locked "check-and-record" operation (mirroring `RequestReplayGuard.CheckAndRecord` in `core/capabilities/vault/request_replay_guard.go`), so the replay check and the marking of the `jti` as used happen under one critical section with no intervening unlocked logic. Add a concurrency test analogous to `TestRequestReplayGuard_ConcurrentAccess` that fires many goroutines with the identical `jti` and asserts exactly one succeeds.

### Proof of Concept
Conceptually (Go-style):
```go
var successCount atomic.Int32
var wg sync.WaitGroup
for i := 0; i < 50; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        if _, err := handler.Authorize(workflowID, sameTokenString, req); err == nil {
            successCount.Add(1)
        }
    }()
}
wg.Wait()
// Expected: successCount == 1
// Actual (racy isReplay/recordUsage split): successCount can be > 1
```
Because `isReplay` and `recordUsage` acquire and release the mutex independently (see lines 399-412 of `workflow_metadata_handler.go`), running the above concurrently against the same `jti` can yield `successCount > 1`, unlike the atomic `RequestReplayGuard.CheckAndRecord`, which the existing test at `request_replay_guard_test.go:96-126` proves always yields exactly one success.

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

**File:** core/capabilities/vault/request_replay_guard_test.go (L96-126)
```go
func TestRequestReplayGuard_ConcurrentAccess(t *testing.T) {
	guard := NewRequestReplayGuard()
	futureExpiry := time.Now().UTC().Unix() + 100

	const goroutines = 100
	results := make([]error, goroutines)
	var wg sync.WaitGroup
	wg.Add(goroutines)

	for i := range goroutines {
		go func(idx int) {
			defer wg.Done()
			results[idx] = guard.CheckAndRecord("same-digest", futureExpiry)
		}(i)
	}
	wg.Wait()

	successCount := 0
	duplicateCount := 0
	for _, err := range results {
		if err == nil {
			successCount++
		} else {
			require.ErrorIs(t, err, ErrRequestAlreadySeen)
			duplicateCount++
		}
	}

	assert.Equal(t, 1, successCount, "exactly one goroutine should succeed")
	assert.Equal(t, goroutines-1, duplicateCount, "all others should be rejected as duplicates")
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L1-1)
```go
package v2
```
