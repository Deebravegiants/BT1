### Title
Missing allowlist and rate-limiting enforcement on legacy web-API-trigger gateway path allows unauthenticated/unthrottled workflow triggering - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`handler.HandleLegacyUserMessage` (the legacy user-message entry point for the WebAPI capabilities gateway handler) contains an explicit `// TODO: apply allowlist and rate-limiting here` comment and performs no sender-allowlist or rate-limit check before fanning the request out to every DON node [1](#0-0) . This mirrors the report's bug class: a reachable, unprivileged-actor entry point that omits a guard which sibling/equivalent code paths enforce.

### Finding Description
The gateway's `ProcessRequest` dispatches unauthenticated (JSON-RPC signed but not allowlist-checked at this layer) incoming HTTP requests to `HandleLegacyUserMessage` whenever the decoded message carries a `DonID` (i.e., "legacy" request format) [2](#0-1) . Inside `HandleLegacyUserMessage`, the code validates payload decoding, a non-zero timestamp, and message staleness, but then jumps straight to method dispatch and forwards the trigger request to all DON members without any allowlist or rate-limit check, as flagged by the inline TODO comment [3](#0-2) .

This is a "sibling function skips a check that the equivalent function enforces" pattern, directly analogous to the `depositAndAllocateForPartyB` bug: the newer v2 HTTP trigger handler for the same gateway subsystem (`httpTriggerHandler.HandleUserTriggerRequest`) explicitly performs `authorizeRequest` (allowlist/authorization) and `checkRateLimit` before processing the request [4](#0-3) . The legacy capabilities handler's `HandleLegacyUserMessage`, which serves the same purpose (accepting a web API trigger request from an external, unprivileged workflow owner and fanning it out to DON nodes), has no equivalent authorization or rate-limit call at all.

The handler's own test suite acknowledges this is an unresolved gap: `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated` [5](#0-4) , and none of the "sad case" tests cover sender/allowlist enforcement — only malformed payload, stale timestamp, and invalid method are tested [6](#0-5) .

### Impact Explanation
Any external party able to reach the gateway's `/` HTTP endpoint and construct a validly-signed legacy `web_api_trigger` message (signature-only integrity check, not identity authorization) can have the gateway broadcast the request to every member node of the DON, with no allowlist restriction on which senders/workflow owners are permitted to trigger a given DON, and no rate limiting to prevent flooding. This can lead to unauthorized workflow-run triggering across DON nodes and resource-exhaustion/DoS against the DON, undermining the same "quota bypass / unauthorized job run" impact category called out in the validation rules.

### Likelihood Explanation
The legacy code path is still live and reachable: `gateway.ProcessRequest` routes to it whenever a request decodes with a non-empty `DonID` [7](#0-6) , and the `multiHandler`/`DummyHandler` wiring shows `HandleLegacyUserMessage` remains an actively invoked interface method across the gateway handler abstraction [8](#0-7) . The missing check is not hypothetical — it is explicitly acknowledged as an open gap in both the production code comment and the test suite, indicating the vulnerability is real and unmitigated rather than compensated elsewhere in this code path.

### Recommendation
Add sender/workflow-owner allowlist verification and rate-limiting to `HandleLegacyUserMessage` before dispatching to DON nodes, mirroring the `authorizeRequest`/`checkRateLimit` pattern already implemented in `httpTriggerHandler.HandleUserTriggerRequest` [4](#0-3) . At minimum, reject requests from senders not present in the DON's configured allowlist and enforce a per-sender/per-workflow rate limit prior to the `don.SendToNode` fan-out loop [9](#0-8) .

### Proof of Concept
1. Craft a validly-signed legacy `api.Message` with `Body.Method = "web_api_trigger"`, a fresh timestamp, and a well-formed `TriggerRequestPayload` (as done in the test helper `triggerRequest`) [10](#0-9) .
2. Submit it to the gateway's HTTP endpoint so it is routed through `gateway.ProcessRequest` → `HandleLegacyUserMessage` [2](#0-1) .
3. Observe that the message passes all checks (decode, non-zero timestamp, staleness, method) and is forwarded to every DON member via `don.SendToNode`, with no allowlist or rate-limit rejection possible, regardless of whether the signer/sender is an authorized workflow owner for that DON [11](#0-10) .
4. Repeating step 2 in a tight loop demonstrates unrestricted request flooding to DON nodes since no rate limiter guards this path (contrast with `httpTriggerHandler`'s `checkRateLimit`, which explicitly denies excess requests) [12](#0-11) .

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L372-421)
```go
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
	req, err := common.ValidatedRequestFromMessage(msg)
	if err != nil {
		h.lggr.Errorw(ErrTransformingMessageToRequest)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrTransformingMessageToRequest,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
}
```

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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L236-338)
```go
func TestHandlerReceiveHTTPMessageFromClient(t *testing.T) {
	handler, _, don, nodes := setupHandler(t)
	ctx := t.Context()
	msg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "", "")
	codec := api.JSONRPCCodec{}

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

	t.Run("sad case invalid method", func(t *testing.T) {
		invalidMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "foo", "", "")
		cb := hc.NewCallback()
		err := handler.HandleLegacyUserMessage(ctx, invalidMsg, cb)
		require.NoError(t, err)

		r, err := cb.Wait(t.Context())
		require.NoError(t, err)
		require.Equal(t, handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				invalidMsg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method foo",
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		}, r)
	})

	t.Run("sad case stale message", func(t *testing.T) {
		invalidMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "123456", "")
		cb := hc.NewCallback()
		err := handler.HandleLegacyUserMessage(ctx, invalidMsg, cb)
		require.NoError(t, err)
		r, err := cb.Wait(t.Context())
		require.NoError(t, err)
		require.Equal(t, handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				invalidMsg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.HandlerError),
				"stale message",
				nil,
			),
			ErrorCode: api.HandlerError,
		}, r)
	})

	t.Run("sad case empty payload", func(t *testing.T) {
		invalidMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "123456", "{}")
		cb := hc.NewCallback()
		err := handler.HandleLegacyUserMessage(ctx, invalidMsg, cb)
		require.NoError(t, err)
		r, err := cb.Wait(t.Context())
		require.NoError(t, err)
		require.Equal(t, handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				invalidMsg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				"error decoding payload field params in TriggerRequestPayload: required",
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		}, r)
	})

	t.Run("sad case invalid payload", func(t *testing.T) {
		invalidMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "123456", `{"foo":"bar"}`)
		cb := hc.NewCallback()
		err := handler.HandleLegacyUserMessage(ctx, invalidMsg, cb)
		require.NoError(t, err)
		r, err := cb.Wait(t.Context())
		require.NoError(t, err)
		require.Equal(t, handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				invalidMsg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				"error decoding payload field params in TriggerRequestPayload: required",
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		}, r)
	})
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```

**File:** core/services/gateway/handlers/handler.go (L31-47)
```go
type Handler interface {
	job.ServiceCtx

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleJSONRPCUserMessage(ctx context.Context, jsonRequest jsonrpc.Request[json.RawMessage], callback Callback) error

	// Handlers should not make any assumptions about goroutines calling HandleNodeMessage.
	// should be non-blocking
	// should validate the message inside the response
	HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L2094-2099)
```go
	callback := hc.NewCallback()
	err = handler.checkRateLimit(t.Context(), restrictedWfID, "req-3", callback)
	require.Error(t, err)
	payload, waitErr := callback.Wait(t.Context())
	require.NoError(t, waitErr)
	requireUserErrorSent(t, payload, jsonrpc.ErrLimitExceeded)
```
