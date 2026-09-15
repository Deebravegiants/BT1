### Title
JWT Replay-Cache Check-Then-Act Race Condition Allows Duplicate HTTP Trigger Execution - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The Redpanda report criticizes exposing an off-chain broker directly to the internet without adequate access controls, allowing attackers to exploit weaknesses in a component that should have been protected. The closest reachable analog in this codebase is the Chainlink Gateway's internet-facing HTTP Trigger endpoint (`gatewayHandler.HandleJSONRPCUserMessage` → `httpTriggerHandler.HandleUserTriggerRequest`), which authenticates unprivileged, external requests using a one-time JWT scheme. The anti-replay protection for that JWT is implemented as a non-atomic check-then-act sequence, allowing an external caller to bypass the "one-time use" guarantee via a race condition.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the sole authorization gate on inbound, internet-facing HTTP trigger requests processed by the Gateway (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`, `authorizeRequest` → `workflowMetadataHandler.Authorize`): [1](#0-0) 

The replay check is implemented with two separately-locked operations on `jwtReplayCache`: [2](#0-1) 

`isReplay` takes an `RLock`, checks for existence, and releases the lock; only afterward (after further processing, including signer/authorized-key lookups) does `recordUsage` take a separate `Lock` and write the entry. Because these are not combined into a single atomic "check-and-set" operation guarded by one lock, two (or more) concurrent requests carrying the identical signed JWT (same `jti`) can both pass `isReplay` before either calls `recordUsage`, since neither request holds the lock across the whole authorize-then-record sequence.

This directly undermines the design intent stated in the code itself and tested behavior (`TestHttpTriggerHandler_HandleUserTriggerRequest` "duplicate JWT token and request ID" test expects the *second* sequential call to fail), which only verifies sequential, non-concurrent replay — not concurrent replay: [3](#0-2) 

### Impact Explanation
An external, unprivileged caller (anyone who can reach the Gateway's HTTP trigger endpoint over the internet) who possesses one validly-signed JWT-authenticated trigger request can send it concurrently multiple times. If the requests race through `Authorize` before `recordUsage` is committed, all of them will be treated as authorized and forwarded to the DON via `sendWithRetries`, resulting in duplicate workflow executions from a single signed authorization. Depending on what the triggered workflow does (e.g., initiating on-chain transactions, external side effects, disbursements), this can cause duplicate/unintended executions — directly paralleling the "unauthorized job run" impact category, and structurally analogous to the exposed-broker report's theme where an internet-facing component's protections can be trivially circumvented by an attacker who can freely reach it.

### Likelihood Explanation
The HTTP trigger handler is explicitly internet-facing (per its own documentation, "Receiving inbound HTTP trigger requests ... to initiate workflows"). Any attacker capable of capturing/replaying a single valid JWT-signed request (e.g., by observing one legitimate call, since JWTs are bearer tokens sent as `req.Auth`) can trivially fire multiple simultaneous HTTP requests carrying the same token; no privileged access or insider position is needed. The race window exists on every authorization for every request, since the check and the record are always non-atomic.

### Recommendation
- **Short term**: Make the JWT replay check-and-record atomic — e.g., use a single mutex-protected method (or `sync.Map` `LoadOrStore`) that performs "if not present, insert; else reject" as one operation, and perform this atomic reservation *before* the more expensive signer/authorization lookups (or ensure the entire sequence from `isReplay` check to `recordUsage` is protected by holding the same lock throughout).
- **Long term**: Consider re-using request/JTI de-duplication infrastructure already used elsewhere in the gateway (e.g., the `activeRequests` request-ID map pattern in `core/services/gateway/handlers/confidentialrelay/handler.go`, which correctly performs an atomic "insert-if-absent" under a single lock) as a reference implementation for the JWT cache.

### Proof of Concept
1. Register a workflow and its authorized signer key with the Gateway's `WorkflowMetadataHandler` (as in `registerWorkflow` test helper).
2. Sign one HTTP trigger `jsonrpc.Request` with a JWT (`createTestJWTToken`).
3. From an external client, fire the same signed request N times concurrently (e.g., N goroutines each calling the Gateway's public HTTP trigger endpoint at the same instant) rather than sequentially.
4. Because `isReplay`/`recordUsage` are separate lock acquisitions, more than one of the N concurrent calls can observe `isReplay(claims.ID) == false` before any of them calls `recordUsage`, allowing more than one to pass authorization and be forwarded to the DON — contrary to the single-execution guarantee demonstrated by the sequential test `"duplicate JWT token and request ID"` at [3](#0-2) , which only proves protection against sequential replay, not concurrent replay.

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
