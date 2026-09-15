### Title
Legacy WebAPI trigger handler admits unauthenticated-caller requests to all DON nodes with no allowlist or rate limiting - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Gateway's internet-facing user endpoint (`gateway.ProcessRequest`) routes legacy JSON-RPC requests to `handler.HandleLegacyUserMessage` in the `capabilities` package. For `web_api_trigger` messages, this function performs only basic structural checks (payload decoding, timestamp freshness) and then, per an explicit `// TODO: apply allowlist and rate-limiting here` comment, fans the request out to **every** DON member node and stores unbounded per-request state, with no allowlist check and no rate limiter consulted at all. This mirrors the analog bug class: the intended admission-time throttle/allowlist gate is documented as required but is entirely absent from the code path that actually decides whether to admit and forward the request, while sibling handlers (the v2 HTTP handler, vault handler, confidentialrelay handler) do enforce allowlist/rate-limit checks at their equivalent admission points.

### Finding Description
The Gateway's `ProcessRequest` (called directly by the HTTP server) decodes and signature-validates (`msg.Validate()`) an inbound message, then dispatches legacy requests to the resolved handler: [1](#0-0) 

For the `capabilities` handler, `HandleLegacyUserMessage` implements the `web_api_trigger` path. It checks payload decodability, a non-zero timestamp, and message staleness — but the rate-limit/allowlist gate is called out as a TODO and never implemented: [2](#0-1) 

After that point, the handler unconditionally stores callback state in the shared `savedCallbacks` map and broadcasts the request to **every** node in `donConfig.Members`: [3](#0-2) 

`msg.Validate()` only proves the request carries a valid ECDSA signature recoverable to *some* address — it is not a membership/allowlist check tying the caller to a specific authorized identity for this DON, so any external caller who can produce a signed, well-formed, non-stale `web_api_trigger` message is admitted. This is functionally identical to the reported pattern: an intended throttle (`WeightsSetRateLimit` in the report vs. rate-limiting/allowlist here) exists as a documented requirement, but the actual admission code path that fans work out (the dispatch body / here, `don.SendToNode` to all members) does not consult it, so the "gate" is a no-op.

By contrast, the newer/adjacent handlers in the same package tree correctly enforce these checks at admission:
- The v2 HTTP trigger handler enforces per-workflow-owner rate limiting via `checkRateLimit` before dispatching to nodes: [4](#0-3) 
- The vault gateway handler defers only owner-scoped limiter checks (not authorization) until after authorization, but always authorizes before doing any allowlisted/limited work: [5](#0-4) 

The legacy `capabilities.handler.HandleLegacyUserMessage` path has neither an authorization/allowlist check nor a rate limit — it only rate-limits/authenticates in the opposite direction (node → gateway outbound HTTP messages, via `nodeRateLimiter` in `handleWebAPIOutgoingMessage`), never user → gateway inbound trigger requests: [6](#0-5) 

### Impact Explanation
An unprivileged remote caller who can produce a validly-signed (but not necessarily allowlisted or specially-privileged) `web_api_trigger` JSON-RPC request can flood the Gateway's `/user` HTTP endpoint. Each accepted request:
- is broadcast to every member node of the target DON via `don.SendToNode`, consuming node/connection bandwidth and node-side processing for all DON members per single caller-submitted request, with no per-caller throttle;
- allocates an entry in `h.savedCallbacks`, a map that grows unbounded except for periodic pruning (`defaultCallbackPruneIntervalSec = 30`, `defaultMaxSavedCallbacks = 20000`), meaning between prune cycles an attacker can push well beyond the intended cap.

This is a resource-exhaustion / flooding primitive against the Gateway and every node behind it, sourced from a single unprivileged caller — the same class of harm described in the report (fee-free/cost-free block-fill via a rate limit that exists conceptually but is not enforced at the actual admission point).

### Likelihood Explanation
High: the request-construction requirements are low. `msg.Validate()` requires only a valid ECDSA signature over the message and does not require the signer to be on any allowlist for the target DON; the handler's own tests explicitly exercise this method with a fabricated node keypair (`triggerRequest(t, nodes[0].PrivateKey, ...)`), confirming any signer, not a privileged/pre-registered identity, can trigger the flow: [7](#0-6) 
The code's own maintainers flag the gap with the `TODO` comment and a corresponding unresolved test-suite TODO ("Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated"): [8](#0-7) 

### Recommendation
Implement the allowlist and rate-limiting gate called out in the TODO before dispatching to DON members and before storing entries in `savedCallbacks`, mirroring the pattern already used in `http_trigger_handler.checkRateLimit` (v2) and the vault gateway's `Authorizer` check: resolve caller identity/topic authorization first, then apply a per-sender/per-topic rate limiter, and only on success proceed to `don.SendToNode` and callback registration. Add regression tests asserting that an unauthorized/over-rate `web_api_trigger` request is rejected before any `SendToNode` call and before any `savedCallbacks` entry is created (paralleling `TestGatewayVaultRequestProcessor_ProcessRequest_UnauthorizedWriteNeverTouchesCiphertextLimiter`).

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no DON-membership required).
2. Construct a `web_api_trigger` `api.Message` with a fresh (non-stale) timestamp and valid `TriggerRequestPayload`, sign it with the arbitrary key (as done in `triggerRequest` helper).
3. POST it repeatedly to the Gateway's `/user` HTTP endpoint (`gateway.ProcessRequest`).
4. Observe that each request passes payload/timestamp checks, is never rejected by an allowlist or rate limiter (none exists on this path), is stored in `savedCallbacks`, and is broadcast via `don.SendToNode` to every member of `donConfig.Members` — repeatable at will to flood all DON nodes and grow the gateway's callback map, exactly as demonstrated by the existing "happy case" test in `handler_test.go` which requires nothing more than an arbitrary signed message. [9](#0-8)

### Citations

**File:** core/services/gateway/gateway.go (L253-276)
```go
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-396)
```go
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-420)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L392-417)
```go
func (h *httpTriggerHandler) checkRateLimit(ctx context.Context, workflowID, requestID string, callback handlers.Callback) error {
	workflowRef, found := h.workflowMetadataHandler.GetWorkflowReference(workflowID)
	if !found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflow reference not found", callback)
		return errors.New("workflow reference not found")
	}

	orgID := h.resolveOrgID(ctx, workflowRef.workflowOwner)
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: workflowRef.workflowOwner, Org: orgID, Workflow: workflowID})
	if err := h.userRateLimiter.AllowErr(ctx); err != nil {
		lggr := logger.With(h.lggr, platform.KeyWorkflowID, workflowID, platform.KeyWorkflowOwner, workflowRef.workflowOwner, "requestID", requestID, "err", err)
		if errLimited, ok := errors.AsType[limits.ErrorRateLimited](err); ok {
			switch errLimited.Scope {
			case settings.ScopeWorkflow:
				lggr.Errorf("failed to start execution: per workflow rate limit exceeded")
				h.metrics.IncrementWorkflowThrottled(ctx, h.lggr)
			default:
				lggr.Errorf("failed to start execution: unexpected rate limit for scope %s", errLimited.Scope)
			}
			h.handleUserError(ctx, requestID, jsonrpc.ErrLimitExceeded, "rate limit exceeded", callback)
			return err
		}
		return fmt.Errorf("failed to check rate limit: %w", err)
	}
	return nil
}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L30-41)
```go
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
type GatewayVaultRequestProcessor struct {
	validator               *RequestValidator
	authorizer              Authorizer
	stripOwnerPrefixForAuth bool
	lggr                    logger.Logger
}

```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L193-234)
```go
func triggerRequest(t *testing.T, key *ecdsa.PrivateKey, topics []string, methodName, timestamp, payload string) *api.Message {
	messageID := "12345"
	if methodName == "" {
		methodName = MethodWebAPITrigger
	}
	if timestamp == "" {
		timestamp = strconv.FormatInt(time.Now().Unix(), 10)
	}
	donID := "workflow_don_1"
	var payloadJSON []byte
	if payload == "" {
		ts, err := strconv.ParseInt(timestamp, 10, 64)
		require.NoError(t, err)
		reqPayload := webapicap.TriggerRequestPayload{
			TriggerId:      "web-api-trigger@1.0.0",
			TriggerEventId: "action_1234567890",
			Timestamp:      ts,
			Topics:         topics,
			Params: webapicap.TriggerRequestPayloadParams(map[string]any{
				"bid": "101",
				"ask": "102",
			}),
		}
		payloadJSON, err = json.Marshal(reqPayload)
		require.NoError(t, err)
	} else {
		payloadJSON = []byte(payload)
	}
	msg := &api.Message{
		Body: api.MessageBody{
			MessageID: messageID,
			Method:    methodName,
			DonID:     donID,
			Payload:   json.RawMessage(payloadJSON),
		},
	}
	err := msg.Sign(key)
	require.NoError(t, err)
	err = msg.Validate()
	require.NoError(t, err)
	return msg
}
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L242-265)
```go
	t.Run("happy case", func(t *testing.T) {
		// sends to 2 dons
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			nodeReq := nodeRequest(msg)
			require.Equal(t, nodeReq, args.Get(2))
		}).Return(nil).Once()
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			nodeReq := nodeRequest(msg)
			require.Equal(t, nodeReq, args.Get(2))
		}).Return(nil).Once()

		cb := hc.NewCallback()
		err := handler.HandleLegacyUserMessage(ctx, msg, cb)
		require.NoError(t, err)

		resp, err := hc.ValidatedResponseFromMessage(msg)
		require.NoError(t, err)
		err = handler.HandleNodeMessage(ctx, resp, nodes[0].Address)
		require.NoError(t, err)

		r, err := cb.Wait(t.Context())
		require.NoError(t, err)
		require.Equal(t, handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError}, r)
	})
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```
