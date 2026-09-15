## Analysis



### Title
Legacy gateway user-message path bypasses sender allowlist enforced on the JSON-RPC trigger path - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The WebAPI capability gateway handler exposes two entry points for delivering trigger requests to a DON: the modern JSON-RPC path and the legacy path (`HandleLegacyUserMessage`). Only the modern trigger implementation enforces a sender allowlist check; the legacy path forwards attacker-controlled requests to every DON node with no such check, exactly mirroring the audit finding where a "second" code path to a privileged operation omitted the origin verification performed by the primary path.

### Finding Description
`gateway.ProcessRequest` in [1](#0-0)  routes any HTTP request that includes a legacy `DonID` in its body to `h.HandleLegacyUserMessage`, bypassing the JSON-RPC handler branch (`HandleJSONRPCUserMessage`).

`HandleLegacyUserMessage` in the WebAPI capabilities handler explicitly defers allowlist/rate-limit enforcement: [2](#0-1) 

It only validates the payload's method name and timestamp before broadcasting the request to every DON member via `don.SendToNode`, with no verification of who the message purports to be from.

By contrast, the actively-maintained trigger implementation used for JSON-RPC style requests, `core/capabilities/webapi/trigger`, enforces a sender allowlist and rejects unauthorized senders, as exercised by its test: [3](#0-2) 

The `handler.HandleJSONRPCUserMessage` for the legacy-capable handler itself is stubbed out entirely (`"capabilities handler does not support JSON-RPC user messages"`): [4](#0-3) 

confirming that the legacy path is the only way this handler processes messages, and it is the one lacking the allowlist/authorization gate that its sibling implementation applies for equivalent functionality — the same root cause pattern as the reported `OptimismHubConnector` bug: a secondary path to a sensitive operation that omits the origin check performed elsewhere.

### Impact Explanation
An unprivileged, unauthenticated HTTP client hitting the gateway's public endpoint can craft a legacy-format `web_api_trigger` request naming any `DonID`/method it likes. Because `HandleLegacyUserMessage` performs no sender/allowlist check, the request is broadcast to every member node of that DON as if it came from an authorized workflow trigger source. Depending on how nodes act on `MethodWebAPITrigger` messages, this can lead to spoofed/unauthorized trigger events being injected into workflows running on the DON — a request-impersonation / allowlist-bypass condition.

### Likelihood Explanation
Likelihood is high for any deployment that still routes legacy-format (`DonID`-carrying) requests to this handler, since no credential, signature, or allowlist membership is required — only knowledge of the expected message shape (`MethodWebAPITrigger`, valid `Timestamp`), which is discoverable from the codebase/tests.

### Recommendation
Apply the same sender allowlist verification used by `core/capabilities/webapi/trigger` (or an equivalent check) inside `HandleLegacyUserMessage` before forwarding requests to DON nodes, removing the `// TODO: apply allowlist and rate-limiting here` gap, or retire/disable the legacy path entirely if it's no longer required.

### Proof of Concept
1. Send an HTTP POST to the gateway's public listener with a legacy-format JSON body: `{"body": {"donId": "<target-don>", "method": "web_api_trigger", "messageId": "<id>", "payload": {"timestamp": <now>, ...}}}` and no valid signature/allowlisted sender.
2. `gateway.ProcessRequest` detects `msg.Body.DonID != ""`, sets `isLegacyRequest = true`, and calls `h.HandleLegacyUserMessage` (`core/services/gateway/gateway.go:253-276`).
3. `HandleLegacyUserMessage` validates only the method name and timestamp, then calls `don.SendToNode` for every DON member (`core/services/gateway/handlers/capabilities/handler.go:384-420`) — no allowlist check is performed, unlike the equivalent check enforced in `core/capabilities/webapi/trigger/trigger.go`.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L295-297)
```go
func (h *handler) HandleJSONRPCUserMessage(_ context.Context, _ jsonrpc.Request[json.RawMessage], _ handlers.Callback) error {
	return errors.New("capabilities handler does not support JSON-RPC user messages")
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
```go
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
```

**File:** core/capabilities/webapi/trigger/trigger_test.go (L276-289)
```go
	t.Run("sad case Not Allowed Sender", func(t *testing.T) {
		gatewayRequest := gatewayRequest(t, privateKey2, []string{"ad_hoc_price_update"}, "")
		th.connector.EXPECT().SignMessage(mock.Anything, mock.Anything).Return([]byte("signature"), nil).Once()
		th.connector.On("SendToGateway", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			resp, err2 := getResponseFromArg(args.Get(2))
			require.NoError(t, err2)

			require.Equal(t, ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: "unauthorized Sender 0x2dAC9f74Ee66e2D55ea1B8BE284caFedE048dB3A, messageID 12345"}, resp)
		}).Return(nil).Once()

		th.trigger.HandleGatewayMessage(ctx, "gateway1", gatewayRequest)
		requireNoChanMsg(t, channel)
		requireNoChanMsg(t, channel2)
	})
```
