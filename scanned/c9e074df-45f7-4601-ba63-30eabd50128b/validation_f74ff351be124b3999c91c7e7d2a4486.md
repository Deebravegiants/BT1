### Title
Web API Trigger requests from unprivileged workflow-owner clients are forwarded to the entire DON with no allowlist or rate-limit enforcement - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`handler.HandleLegacyUserMessage` (the entry point that processes user-submitted `web_api_trigger` messages arriving at the gateway) validates only payload decodability, a non-zero timestamp, staleness, and method name, then unconditionally forwards the request to every member of the DON. An explicit `// TODO: apply allowlist and rate-limiting here` marks the missing authorization/quota check that the DODO analog ("no slippage or deadline control" = missing bound/validation on a user-supplied request before it is acted upon) maps to.

### Finding Description
`HandleLegacyUserMessage` unmarshals the caller-supplied `webapicap.TriggerRequestPayload`, checks `payload.Timestamp` for staleness, and checks `msg.Body.Method == MethodWebAPITrigger`, but performs no check that the requester (workflow owner / message sender) is allowlisted or is within a rate/quota limit before broadcasting the request to all DON members: [1](#0-0)  The TODO explicitly documents the gap: [2](#0-1)  After the checks, the message is saved and forwarded to every DON member without further gating: [3](#0-2) 

This is directly analogous to the DODO issue: in DODO, `liquidate` accepted attacker/caller-controlled parameters (`collateralAmount`, `debtToCover`) with only loose bound checks and no additional protective gate (slippage/deadline), letting unintended/abusive calls execute with real economic effect. Here, an unprivileged, unauthenticated caller's `web_api_trigger` message is likewise accepted with only superficial validation (payload parses, timestamp present/fresh, method name correct) and, missing the intended allowlist/rate-limit gate, is broadcast to the entire DON — the "action" analogous to fund movement/execution in the audited contract.

By contrast, other gateway handlers in the same codebase (e.g., the Vault gateway pipeline) enforce `AuthorizeRequest` via an `Authorizer` before processing: [4](#0-3)  and the v2 HTTP trigger handler enforces rate limiting per workflow: [5](#0-4)  This confirms allowlist/rate-limit enforcement is the intended and implemented pattern elsewhere, making its absence in the legacy capabilities `web_api_trigger` path a genuine gap rather than by design.

### Impact Explanation
Any unauthenticated/unprivileged client able to reach the gateway's legacy user-message endpoint for `web_api_trigger` can cause the gateway to fan out arbitrary trigger requests to every node in the DON, with no allowlist check restricting who may submit and no rate limiting to bound volume. This can be leveraged for resource exhaustion of DON nodes (each node processes and potentially performs outbound HTTP work per `handleWebAPIOutgoingMessage`) and to trigger workflow execution paths that were meant to be gated to allowlisted callers, i.e., an allowlist/quota bypass on an internet-facing gateway handler.

### Likelihood Explanation
The check is entirely absent (not merely misconfigured), and the code path is reachable from any external caller invoking the standard `HandleJSONRPCUserMessage` → `HandleLegacyUserMessage` flow for `web_api_trigger` messages; the developer-authored TODO confirms this is a known, unaddressed gap rather than a hypothetical.

### Recommendation
Implement the allowlist check (verify the requester/workflow owner against a DON-configured or workflow-registry allowlist, similar to `allowListBasedAuth.AuthorizeRequest` used by the Vault handler) and enforce per-sender/per-workflow rate limiting before saving the callback and forwarding to DON members in `HandleLegacyUserMessage`, mirroring the pattern already implemented in `core/capabilities/vault/gw_handler.go` and `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`.

### Proof of Concept
1. An unprivileged client sends a JSON-RPC user message with `Method: web_api_trigger` and a `TriggerRequestPayload` containing a valid, non-zero, non-stale `Timestamp` to the gateway.
2. `HandleLegacyUserMessage` passes the decode check, the zero-timestamp check, and the staleness check: [6](#0-5) 
3. No allowlist or rate-limit check is applied (per the TODO), so the request is saved to `savedCallbacks` and sent to every DON member: [7](#0-6) 
4. Repeating this from a script with distinct message IDs causes unrestricted fan-out of trigger requests to the whole DON, unbounded by allowlist membership or rate limits.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-396)
```go
func (h *handler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback handlers.Callback) error {
	body := msg.Body
	var payload webapicap.TriggerRequestPayload
	codec := api.JSONRPCCodec{}
	err := json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw(ErrDecodingPayload, "err", err)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload+" "+err.Error(),
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if payload.Timestamp == 0 {
		h.lggr.Errorw(ErrDecodingPayload)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115: comparing unix timestamps, both fit within uint
		h.lggr.Errorw("stale message")
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.HandlerError),
				"stale message",
				nil,
			),
			ErrorCode: api.HandlerError,
		})
	}
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L410-420)
```go

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/capabilities/vault/gw_handler.go (L180-206)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L1977-2020)
```go
	t.Run("rate limit exceeded returns proper error", func(t *testing.T) {
		// Create a rate limiter with very restrictive limits
		restrictiveRateLimiter := limits.WorkflowRateLimiter(1, 0)
		handler := newTestTriggerHandler(t, lggr, cfg, donConfig, mockDon, metadataHandler, restrictiveRateLimiter, testMetrics)

		privateKey := createTestPrivateKey(t)
		workflowID := "0x1234567890abcdef1234567890abcdef12345678901234567890abcdef123456"
		workflowOwner := "0x1234567890abcdef1234567890abcdef12345678"

		// Register workflow with reference
		registerWorkflow(t, handler, workflowID, privateKey)
		handler.workflowMetadataHandler.workflowIDToRef[workflowID] = workflowReference{
			workflowOwner: workflowOwner,
			workflowName:  "test-workflow",
			workflowTag:   "v1.0",
		}

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
			ID:      "test-request-id-rate-limit",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}
		req.Auth = createTestJWTToken(t, req, privateKey)

		callback := hc.NewCallback()

		// First request should consume the burst capacity and exceed the rate limit
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback, time.Now())
		require.Error(t, err)
		r, err := callback.Wait(t.Context())
		require.NoError(t, err)
		requireUserErrorSent(t, r, jsonrpc.ErrLimitExceeded)
	})
```
