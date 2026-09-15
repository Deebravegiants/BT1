### Title
Legacy web_api_trigger gateway path forwards unauthenticated/unallowlisted requests to the workflow DON, bypassing the authorization checks enforced on the JSON-RPC trigger path - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The Vault.sol finding shows that a secondary entry point (`fallback()`) can execute privileged plugin logic without the permission checks that the primary entry point (`execute()`) enforces. Chainlink's WebAPI gateway handler has the same structural pattern: it exposes two parallel entry points for the same underlying trigger capability — `HandleLegacyUserMessage` (legacy `api.Message` path) and `HandleJSONRPCUserMessage`/`HandleUserTriggerRequest` (the newer JSON-RPC v2 trigger path) — but only the newer path performs sender/workflow authorization before dispatching to the DON.

### Finding Description
`gateway.ProcessRequest` (`core/services/gateway/gateway.go:221-295`) is the internet-facing entry point invoked for every incoming client HTTP request. Depending on whether the request carries a legacy `DonID`, it routes to either:
- `h.HandleLegacyUserMessage(ctx, msg, callback)` for legacy requests [1](#0-0) 
- `h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)` for new-style requests [1](#0-0) 

For the WebAPI capabilities handler (`core/services/gateway/handlers/capabilities/handler.go`), `HandleLegacyUserMessage` only validates payload structure, timestamp freshness, and method name, then immediately forwards the message to every DON member — there is no sender/allowlist check: [2](#0-1) 

The code contains an explicit acknowledgment of the gap right before the method check:
```
// TODO: apply allowlist and rate-limiting here
``` [3](#0-2) 

The accompanying unit test file confirms this is a known, unresolved gap rather than logic covered elsewhere:
```
// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
``` [4](#0-3) 

By contrast, the newer HTTP trigger path for the same capability family explicitly authorizes the caller before dispatching:
```go
key, err := h.authorizeRequest(ctx, workflowID, req, callback)
if err != nil {
    return err
}
if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
    return err
}
``` [5](#0-4) 

`msg.Validate()` (invoked inside `HandleLegacyUserMessage` via `common.ValidatedRequestFromMessage`) only checks that the message carries a well-formed, self-consistent signature — it does not check that the signer is a member of any allowlist or authorized sender set. Any caller can generate their own ECDSA keypair, sign an arbitrary `web_api_trigger` message, and have it forwarded to the DON, exactly as the vault fallback bug allowed any caller to invoke an installed plugin method without the permission checks imposed on the primary, permissioned entry point.

### Impact Explanation
An unprivileged HTTP client can submit a legacy-format `web_api_trigger` request directly to the gateway. Because `HandleLegacyUserMessage` skips allowlist/authorization checks (unlike the JSON-RPC trigger path), the forged request is forwarded to all DON node members as if it were a legitimate, authorized trigger event. This can result in:
- Unauthorized workflow trigger invocation (bypassing the intended per-workflow/topic sender authorization that the parallel path enforces),
- Potential resource exhaustion / DoS on DON nodes since rate limiting is also explicitly noted as unimplemented on this path,
- Cross-user confusion if a malicious sender can spoof `Topics`/payload fields that downstream node-side logic uses to route or attribute the trigger.

The severity depends on what downstream node-side/workflow logic assumes about the authenticity of legacy-routed messages; if nodes trust the gateway to have performed authorization (as the TODO comment on the gateway side implies it should), then this is a genuine authorization-bypass vector reachable from any unauthenticated internet client.

### Likelihood Explanation
The legacy path is reachable directly from `gateway.ProcessRequest`, the top-level function that processes all raw incoming HTTP requests [6](#0-5) , with no authentication middleware required beyond a self-generated signature. Because the gap is explicitly called out via TODO comments in both the implementation and its test file, it is a known, currently-unaddressed condition rather than a hypothetical one. Likelihood is High for reaching this code path; actual exploitability depends on whether callers can obtain a valid legacy `DonID`/method combination, which the code does not appear to gate behind any secret.

### Recommendation
Mirror the mitigation pattern from the Vault report: track authorization requirements alongside the message dispatch and enforce them uniformly across both entry points. Concretely:
- Implement the allowlist/rate-limit check called out by the `// TODO: apply allowlist and rate-limiting here` comment in `HandleLegacyUserMessage` before forwarding to DON members, using the same authorization mechanism (`authorizeRequest`/`checkRateLimit`) already implemented for `HandleUserTriggerRequest` on the JSON-RPC path.
- Alternatively, if the legacy path is deprecated, reject `web_api_trigger` legacy messages outright (similar to how `http_handler.go`'s `HandleLegacyUserMessage` already returns an explicit "does not support legacy messages" error) rather than silently forwarding unauthenticated requests.
- Add regression tests asserting that unallowlisted/unauthorized senders are rejected on the legacy path, matching existing coverage on the JSON-RPC path (e.g., `TestHttpTriggerHandler_HandleUserTriggerRequest_JWTAuthorization`).

### Proof of Concept
Not independently exploitable via static analysis alone — this requires a running gateway + DON to observe that a self-signed legacy message reaches node members without allowlist rejection. Based on the code, the reachable path is:
1. Craft an `api.Message` with `Body.Method = "web_api_trigger"`, a fresh unregistered ECDSA key, and a valid `TriggerRequestPayload` (non-zero timestamp).
2. Call `msg.Sign(unregisteredKey)` and submit via `gateway.ProcessRequest` (legacy request format, as exercised in `TestHandlerReceiveHTTPMessageFromClient`'s "happy case" using `nodes[0].PrivateKey`, but substituting any arbitrary key not present in `donConfig.Members`) [7](#0-6) .
3. Observe that `HandleLegacyUserMessage` performs no check tying the signer to an authorized sender/allowlist before calling `don.SendToNode` for every DON member [8](#0-7) .

I was not able to fully verify within the available searches whether some other layer (e.g., a wrapping middleware, or node-side logic upon receipt) independently re-validates the sender before actually acting on the trigger — this would need to be confirmed in a live/dynamic test environment (e.g., a Devin session) to determine the full end-to-end exploitability and blast radius.

### Citations

**File:** core/services/gateway/gateway.go (L221-276)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-420)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L236-265)
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
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
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
