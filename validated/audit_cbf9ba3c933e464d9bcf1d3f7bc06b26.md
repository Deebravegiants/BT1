### Title
JWT replay-check is not atomic with usage recording, allowing signed HTTP-trigger requests to be replayed via concurrent submission - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The `AzukiDAO` report is a signature-replay bug: a single signed authorization (`claim()` signature) could be submitted repeatedly because the contract never atomically marked it "consumed" before executing side effects, so concurrent/repeated calls all validated successfully. The `WorkflowMetadataHandler.Authorize` path in the chainlink gateway's internet-facing HTTP trigger handler has the same class of flaw: the JWT replay check (`isReplay`) and the mark-as-used step (`recordUsage`) are two independent, non-atomic operations, separated by additional work (workflow/key lookup). Concurrent submissions of the same signed JWT can both pass the replay check before either records usage.

### Finding Description
`WorkflowMetadataHandler.Authorize` verifies the JWT signature/digest and then checks for replay and workflow authorization before marking the JWT `jti` as used: [1](#0-0) 

The replay cache implementation performs the read-check and the write-record under two *separate* lock acquisitions rather than a single atomic check-and-set: [2](#0-1) 

Between `isReplay(claims.ID)` returning `false` and `recordUsage(claims.ID)` being called (after the `authorizedKeys` lookup and key match), there is a window where two goroutines processing the same valid, signed JWT concurrently can both pass the replay check. This is exactly the anti-pattern the AzukiDAO report exploited: a signature (here, a JWT authorizing a specific request digest) is accepted as valid multiple times because "already used" state is not committed atomically with validation.

This is directly reachable by an unprivileged internet client: the HTTP trigger handler (`httpTriggerHandler.authorizeRequest` → `workflowMetadataHandler.Authorize`) is invoked for every inbound `HandleUserTriggerRequest` call from the public gateway endpoint, using attacker-supplied JSON-RPC requests and JWT tokens signed by any registered workflow signer key: [3](#0-2) 

By contrast, the Vault capability's equivalent replay guard performs the check-and-record as a single atomic operation under one lock, which is exactly the correct fix pattern already used elsewhere in the codebase: [4](#0-3) 

### Impact Explanation
If an attacker (or a legitimate workflow client, maliciously or accidentally) fires the same signed JWT-authorized HTTP trigger request concurrently (e.g., two parallel HTTP POSTs to the gateway), both can pass `Authorize()` before either is recorded as used. This defeats the intended "one-time use" guarantee of a signed request and results in duplicate workflow trigger executions/job runs for a single authorized signature — a request-impersonation-adjacent/duplicate-execution issue analogous to the unauthorized repeated `claim()` calls in the AzukiDAO exploit. Downstream impact depends on the workflow being triggered (e.g., duplicate on-chain transactions, duplicate resource consumption, duplicate business logic execution), i.e., an unauthorized duplicate job run.

### Likelihood Explanation
Exploitation requires only the ability to send the same HTTP request (with its already-obtained valid Authorization JWT) twice in quick succession/concurrently — trivial for any client that already possesses a legitimately signed request (its own, or one observed/replayed within the JWT's expiry window, since the JWT itself is a bearer credential). No privileged access is needed; the window is small but deterministically exploitable with concurrent requests, and the sequential test suite (`TestHttpTriggerHandler_HandleUserTriggerRequest`, "duplicate JWT token and request ID") only demonstrates the *sequential* rejection path, not the concurrent race, so the race is not covered by existing tests.

### Recommendation
Make `jwtReplayCache`'s check-and-record atomic (a single locked "check-and-set" operation, as already implemented correctly in `core/capabilities/vault/request_replay_guard.go`), or acquire a single lock spanning `isReplay` + `recordUsage` in `WorkflowMetadataHandler.Authorize` so no two goroutines can observe the JWT as unused simultaneously.

### Proof of Concept
Not independently executable in this ask-only session (no filesystem/terminal access to run tests), but the race is demonstrable by calling `WorkflowMetadataHandler.Authorize` (or `httpTriggerHandler.HandleUserTriggerRequest`) twice concurrently (e.g., via `go func` from two goroutines) with the same valid signed JWT/request pair, analogous to the existing sequential test at: [5](#0-4) 
but issuing both `HandleUserTriggerRequest` calls concurrently instead of sequentially, and asserting that both succeed instead of the second being rejected.

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
