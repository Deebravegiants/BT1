### Title
JWT replay-protection cache for HTTP trigger authentication is held only in process memory and is lost on gateway restart, allowing previously-used signed requests to be replayed - (File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go)

### Summary
The gateway's HTTP Trigger authentication path relies on a `jwtReplayCache` that tracks used JWT IDs (`jti`) to reject replayed signed requests. This cache is a plain in-memory map with no persistence backing it. Any gateway restart, redeploy, or process recycle wipes the entire replay history while previously-issued JWTs remain valid (their `exp` has not yet elapsed), letting an unprivileged external caller replay a previously captured, already-used, signed `HTTPTriggerRequest` to re-trigger a workflow execution.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the authentication entry point for inbound HTTP trigger requests reaching the internet-facing gateway. It verifies the JWT signature/digest and then consults `jwtReplayCache.isReplay(claims.ID)` before accepting the request, finally calling `recordUsage` to mark the `jti` as spent: [1](#0-0) 

The cache itself is defined as an unguarded-by-storage, purely in-memory structure: [2](#0-1) 

and its constructor/usage-recording functions only ever touch the in-process map, never any durable store: [3](#0-2) 

The default configured retention window for replay protection is 24 hours (`defaultJWTReplayPeriodMs = 1000 * 60 * 60 * 24`), meaning the system's own design intends already-used JWT IDs to remain rejected for up to a day: [4](#0-3) 

Because the "spent" record for a `jti` is process-local memory rather than durable/shared state, any event that restarts the gateway process (deploy, crash/recovery, rolling restart) silently and completely resets the replay-protection window to empty, even though the JWTs themselves remain cryptographically valid until their `exp` claim elapses. This is directly analogous to the OpenMLS root cause: state meant to prevent reuse of previously-processed material was not durably persisted, so upon reload the protection state reverts to a stale/empty condition and material that should be considered "already consumed" is treated as fresh again — enabling more use (here, replay) than the design intends.

The test suite explicitly documents that the intended behavior is one-time-use: a JWT reused for the same/duplicate request must be rejected with "JWT token has already been used": [5](#0-4) 

### Impact Explanation
If an adversary captures a previously-submitted, validly-signed `HTTPTriggerRequest` (e.g. via network observation, logging, proxy, or because they were the original legitimate caller and now wish to abuse it), they can resubmit the exact same signed payload after any gateway restart occurring before the JWT's `exp`. Since the replay cache has been wiped, `isReplay` returns false and the request is treated as fresh, allowing an unauthorized re-triggering of the workflow (unauthorized job/workflow run), which is an accepted analog impact category ("unauthorized job run"). This defeats the one-time-use guarantee the replay protection was specifically built to enforce, i.e. request impersonation/replay bypass on the internet-facing gateway path.

### Likelihood Explanation
Likelihood is limited by two factors: (1) the attacker must have captured a previously valid signed request (this could be the legitimate caller itself re-sending it, or a passive observer such as a shared proxy/log), and (2) a gateway process restart must occur within the token's validity window. Gateway restarts (deploys, crashes, scaling events, rolling upgrades) are routine operational events in production node/gateway fleets, and JWT `exp` windows are caller-controlled, so this is a realistic, low-effort condition for an already-possessing-a-token actor to exploit — no privileged access is required beyond having observed/held one previously valid signed request.

### Recommendation
Persist JWT replay state (jti + expiry) in a durable, restart-surviving store (e.g. the gateway's database, or a shared cache such as Redis for multi-instance deployments) instead of an in-process map, so that a process restart cannot erase already-consumed replay markers. At minimum, on Authorize, persisted state should be checked/written transactionally to avoid a resurrected empty cache from silently re-authorizing spent tokens.

### Proof of Concept
1. A legitimate workflow owner signs and submits an `HTTPTriggerRequest` with JWT `jti=X` and `exp` = now + 1 hour; the gateway's `Authorize` succeeds and records `X` as used in `jwtReplayCache`. [1](#0-0) 
2. An attacker who has captured this exact signed request (e.g., from a proxy log, retry queue, or as the original submitter attempting abuse) waits for or triggers conditions causing the gateway process to restart (deploy/crash/rolling update) — well within the `exp` window.
3. Because `jwtReplayCache.cache` is only an in-memory `map[string]time.Time` with no backing persistence, the restarted process starts with an empty cache. [6](#0-5) 
4. The attacker resubmits the identical previously-used signed request with `jti=X`. `isReplay(X)` returns `false` (cache is empty), so `Authorize` succeeds again and the workflow is re-triggered without new authorization — reproducing exactly the scenario the existing unit test asserts should be rejected. [5](#0-4)

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L392-426)
```go
func newJWTReplayCache(cleanupPeriod time.Duration) *jwtReplayCache {
	return &jwtReplayCache{
		cache:         make(map[string]time.Time),
		cleanupPeriod: cleanupPeriod,
	}
}

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

// cleanupOldEntries removes expired entries from the cache
func (cache *jwtReplayCache) cleanupOldEntries(cutoff time.Time) int {
	cache.mu.Lock()
	defer cache.mu.Unlock()
	var expiredCount int
	for jti, createdAt := range cache.cache {
		if createdAt.Before(cutoff) {
			delete(cache.cache, jti)
			expiredCount++
		}
	}
	return expiredCount
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L29-44)
```go
const (
	handlerName                          = "HTTPCapabilityHandler"
	defaultCleanUpPeriodMs               = 1000 * 60 * 10 // 10 minutes
	defaultMaxTriggerRequestDurationMs   = 1000 * 60      // 1 minute
	defaultNodeSendTimeoutMs             = 1000 * 10      // 10 seconds
	defaultInitialIntervalMs             = 100
	defaultMaxIntervalTimeMs             = 1000 * 30 // 30 seconds
	defaultMultiplier                    = 2.0
	defaultMetadataPullIntervalMs        = 1000 * 60 // 1 minute
	defaultMetadataAggregationIntervalMs = 1000 * 60 // 1 minute
	defaultMetadataPullRequestTimeoutMs  = 1000 * 30 // 30 seconds
	internalErrorMessage                 = "Internal server error occurred while processing the request"
	defaultOutboundRequestCacheTTLMs     = 1000 * 60 * 10      // 10 minutes
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
	defaultSendResponseTimeoutMs         = 1000 * 5            // 5 seconds
)
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
