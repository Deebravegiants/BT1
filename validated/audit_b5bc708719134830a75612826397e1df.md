### Title
DoS of HTTP Trigger workflow execution via JWT replay-cache front-running — ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The Gateway's HTTP Trigger flow authorizes each inbound user request using a self-signed, ECDSA-based JWT that is bound to the JSON-RPC request digest and de-duplicated by a single global, in-memory replay cache keyed on the JWT `jti` claim. Because `HandleJSONRPCUserMessage`/`HandleUserTriggerRequest` is a public, unauthenticated (pre-JWT-check) gateway entry point that accepts *any* caller's JSON-RPC request bundled with its `Auth` token, any third party who obtains a copy of a valid signed request+JWT pair can submit it to the gateway ahead of the legitimate sender. This consumes the one-time `jti` in the shared `jwtReplayCache`, so when the legitimate request subsequently arrives (e.g., after a network retry, proxy resend, or any path where the exact same signed payload is observed and replayed), it is rejected as an already-used token — a direct DoS of the intended workflow execution, mirroring the reported Permit2 nonce front-run pattern (a signature-bound one-time authorization consumable by an unrelated third party).

### Finding Description
`WorkflowMetadataHandler.Authorize` verifies the JWT and checks `h.jwtCache.isReplay(claims.ID)` before checking authorized keys, then calls `h.jwtCache.recordUsage(claims.ID)` on success: [1](#0-0) 

The replay cache itself is a simple global map keyed only by `jti`, with no binding to the specific caller/session that first presented it: [2](#0-1) 

This is invoked from `authorizeRequest` inside `HandleUserTriggerRequest`, which is the gateway's handling path for inbound JSON-RPC user trigger requests: [3](#0-2) [4](#0-3) 

`HandleUserTriggerRequest` is reached via `HandleJSONRPCUserMessage`, the generic gateway entry point for user-submitted JSON-RPC messages (equivalent to the internet-facing gateway handler surface): [5](#0-4) 

The JWT is a signed representation of the request digest (not encrypted), created via `CreateRequestJWT`/verified via `VerifyRequestJWT`, and is only unique per `jti`; anyone possessing the full `(request, Auth)` pair — regardless of whether they are the legitimate sender — can submit it directly to the gateway and it will be treated as fully authorized: [6](#0-5) 

The existing tests confirm the failure mode explicitly: submitting the identical `(req, Auth)` pair a second time — regardless of who submits it — is rejected with "JWT token has already been used", proving this is a global, submitter-agnostic nonce: [7](#0-6) [8](#0-7) 

This is directly analogous to the reported Permit2 issue: a one-time, signature-bound authorization token intended to be redeemed exactly once by the legitimate flow can instead be redeemed by any party who obtains a copy of it (e.g., via network observation, proxy/CDN logging, retries traversing shared infrastructure, or a malicious intermediary), permanently invalidating it for the legitimate requester before their own request lands.

### Impact Explanation
A third party who captures a valid `(request, Auth)` pair — for example by sitting on a shared network path, a misconfigured logging/proxy layer, or simply because the legitimate caller retries the exact same signed request through a different route after a timeout — can submit it to the gateway first. This permanently burns the `jti` in the process-lifetime replay cache, causing the legitimate workflow-triggering request to be rejected with `"JWT token has already been used"`. This denies the legitimate user their intended HTTP-triggered workflow execution, which is the same class of impact (denial of a rightful action due to consumption of a one-time signature-bound resource by an unauthorized party) as the original report.

### Likelihood Explanation
Exploitation requires the attacker to first obtain a byte-identical copy of a legitimate, not-yet-consumed `(request, Auth)` pair. This is a meaningfully harder precondition than the original on-chain report (where any pending mempool transaction is trivially publicly observable), since gateway traffic is typically over TLS between the caller and gateway. However, the failure mode is realistic in retry/proxy scenarios (the same signed payload naturally gets resent verbatim by clients, load balancers, or during idempotent retries) and the JWT/cache design provides no defense once a valid pair is observed by anyone other than the original sender — there is no per-caller/session binding, only a bare `jti` uniqueness check.

### Recommendation
- Bind the replay-cache entry to more than just `jti`: additionally verify that the recorded consumer (e.g., a caller-supplied idempotency/session token established via TLS-authenticated channel) matches on redemption, or ensure jti replay checks are only meaningful in combination with a channel-bound nonce that an eavesdropper cannot replay.
- Consider using short-lived, single-channel-bound tokens (e.g., binding the JWT to the specific gateway TLS session or requiring an additional client-held secret) so that merely observing the wire bytes of a legitimate request is insufficient to redeem it elsewhere.
- Alternatively, treat a duplicate-`jti` submission from a different apparent origin as suspicious and return a retry-safe error rather than a terminal failure, or allow the original legitimate caller (identified by a persistent session/connection) to still succeed while rejecting only the confirmed duplicate origin.

### Proof of Concept
1. A legitimate workflow owner constructs and signs an HTTP trigger request `req` with `Auth = JWT(jti=X, digest=D)` per `CreateRequestJWT`.
2. Before the legitimate request reaches the gateway (e.g., it is observed in transit, or the client's retry logic resends the exact same signed payload through an alternate path), an attacker captures the full `(req, Auth)` byte sequence.
3. The attacker submits this exact payload directly to the gateway's `HandleJSONRPCUserMessage` endpoint. `WorkflowMetadataHandler.Authorize` verifies the JWT successfully, finds no `jti=X` replay, and calls `jwtCache.recordUsage(X)` — as validated by `TestHttpTriggerHandler_HandleUserTriggerRequest`/`TestWorkflowMetadataHandler_Authorize`'s "duplicate JWT" cases.
4. When the legitimate request with the same `Auth` reaches the gateway, `isReplay("X")` returns true and the request is rejected with `"JWT token has already been used. Please generate a new one with new id (jti)"`, denying the legitimate workflow execution. [9](#0-8)

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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L392-402)
```go
func (h *gatewayHandler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback handlers.Callback) error {
	h.metrics.IncrementTriggerRequestCount(ctx, h.lggr)
	err := h.triggerHandler.HandleUserTriggerRequest(ctx, &req, callback, time.Now())
	if err != nil {
		h.lggr.Errorw("failed to handle user trigger request", "requestID",
			req.ID, "err", err)
		// error response is sent to the response channel by the trigger handler
		// so return nil after logging
	}
	return nil
}
```

**File:** core/utils/jwt.go (L228-304)
```go
// VerifyRequestJWT verifies a signed JWT for a JSON-RPC request
// It recovers and returns the public key used to sign the JWT, checks the issuer, validates the digest,
// and performs all validations done by jwt.ParseWithClaims() including expiration checks.
func VerifyRequestJWT[T any](tokenString string, req jsonrpc.Request[T], opts ...VerifyOption) (*JWTClaims, gethcommon.Address, error) {
	options := &verifyOptions{}
	for _, opt := range opts {
		opt(options)
	}

	maxExpiryDuration := maxJWTExpiryDuration
	if options.maxExpiryDuration != nil {
		maxExpiryDuration = *options.maxExpiryDuration
	}

	issuedAtTolerance := defaultIssuedAtTolerance
	if options.issuedAtTolerance != nil {
		issuedAtTolerance = *options.issuedAtTolerance
	}
	signedString, signature, err := splitToken(tokenString)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	decodedSignature, err := base64.RawURLEncoding.DecodeString(signature)
	if err != nil {
		return nil, gethcommon.Address{}, fmt.Errorf("signature segment is not valid base64url: %w", err)
	}
	pubKey, err := GetSignersEthAddress([]byte(signedString), decodedSignature)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	verifiedToken, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (any, error) {
		if token.Method.Alg() != EthereumSigningMethod.Alg() {
			return nil, fmt.Errorf("unsupported JWT 'alg': '%s'. Expected '%s'", token.Method.Alg(), EthereumSigningMethod.Alg())
		}
		if _, ok := token.Method.(*SigningMethodEth); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return pubKey, nil
	})
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	verifiedClaims, ok := verifiedToken.Claims.(*JWTClaims)
	if !ok {
		return nil, gethcommon.Address{}, errors.New("claims payload is not in the expected format")
	}
	if !verifiedToken.Valid {
		return nil, gethcommon.Address{}, errors.New("signature or claims validation failed")
	}
	reqDigest, err := req.Digest()
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	if verifiedClaims.ID == "" {
		return nil, gethcommon.Address{}, errors.New("JWT ID (jti) is required but missing")
	}
	if verifiedClaims.ExpiresAt == nil {
		return nil, gethcommon.Address{}, errors.New("expiredAt (exp) is required but missing")
	}
	if verifiedClaims.IssuedAt == nil {
		return nil, gethcommon.Address{}, errors.New("issuedAt (iat) is required but missing")
	}
	now := time.Now()
	issuedAt := verifiedClaims.IssuedAt
	if issuedAt.After(now.Add(issuedAtTolerance)) {
		return nil, gethcommon.Address{}, fmt.Errorf("issuedAt (iat) is too far in the future (beyond tolerance of %.0f seconds)", issuedAtTolerance.Seconds())
	}
	duration := verifiedClaims.ExpiresAt.Sub(verifiedClaims.IssuedAt.Time)
	if duration > maxExpiryDuration {
		return nil, gethcommon.Address{}, fmt.Errorf("token lifetime %.0f sec exceeds the maximum allowed %.0f sec. Reduce the gap between 'iat' and 'exp'", duration.Seconds(), maxExpiryDuration.Seconds())
	}
	if verifiedClaims.Digest != "0x"+reqDigest {
		return nil, gethcommon.Address{}, fmt.Errorf("claim digest '%s' does not match calculated request digest '0x%s'", verifiedClaims.Digest, reqDigest)
	}

	return verifiedClaims, pubKey, nil
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
