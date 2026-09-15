### Title
Gateway forwards unauthenticated user-supplied `web_api_trigger` messages to all DON nodes without sender allowlist checks, allowing timestamp forgery and trigger impersonation - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The Gateway's legacy user-message path (`HandleLegacyUserMessage`) accepts JSON-RPC/HTTP requests from any client hitting the Gateway's public user-facing HTTP server and forwards them, largely unfiltered, to every node in the configured DON. The message's `Timestamp` field — fully controlled by the caller — is used only for a staleness bound check, not for verifying the sender's identity or workflow authorization. The code contains an explicit `// TODO: apply allowlist and rate-limiting here` marking that sender/topic authorization is not yet implemented. This mirrors the reported Nord vulnerability, where an unprivileged HTTP client could submit a privileged, timestamp-bearing update message that should only originate from a trusted internal source.

### Finding Description
`gateway.ProcessRequest` in [1](#0-0)  decodes an inbound HTTP request into an `api.Message`, calls `msg.Validate()` (which only checks the message's structural/signature validity, not that the signer is an authorized caller for the target DON/workflow), then dispatches directly to `h.HandleLegacyUserMessage(ctx, msg, callback)`.

`HandleLegacyUserMessage` then:
- Decodes the caller-supplied `TriggerRequestPayload`, including a `Timestamp` field fully controlled by the caller.
- Rejects the message only if it's "stale" relative to `MaxAllowedMessageAgeSec`, but does **not** validate that the timestamp is not in the future or that the sender is authorized to submit this trigger.
- Explicitly skips authorization: `// TODO: apply allowlist and rate-limiting here` immediately before dispatching to nodes.
- Forwards the request to **every DON member** via `don.SendToNode(ctx, member.Address, req)`. [2](#0-1) 

This is the same bug class as the Nord report: a message type intended to represent a privileged/trusted event (there, an oracle price update with an authoritative timestamp; here, a workflow trigger event with a client-controlled timestamp) is accepted directly from an untrusted, internet-facing HTTP endpoint and forwarded into the trusted system (DON nodes) without verifying that the submitter is actually authorized to originate that specific trigger/topic. The staleness check alone (comparable to Nord's timestamp-ordering check) is insufficient to prevent impersonation or forged/duplicate trigger submissions, since any external caller can pick any fresh timestamp and any `MessageID`/topics, and the code's own comment acknowledges the missing allowlist enforcement.

### Impact Explanation
An unauthenticated/unprivileged external actor reaching the Gateway's public HTTP endpoint can:
- Submit forged `web_api_trigger` messages for workflows/topics they should not be able to trigger, since sender-to-topic allowlisting is not enforced at this layer (per the TODO).
- Control the message timestamp to satisfy the staleness check, enabling replay/impersonation-style requests that get broadcast to the entire DON.
- Potentially disrupt legitimate trigger processing by flooding all DON nodes with spoofed/duplicate trigger messages sharing crafted `MessageID`s, interfering with `savedCallbacks` bookkeeping used to route legitimate node responses back to the correct caller.

This is analogous to the reported impact in Nord (unauthorized message injection affecting price/timestamp state), translated to Chainlink's Gateway/DON trigger path: unauthorized workflow trigger injection and DON-wide message flooding from unprivileged clients.

### Likelihood Explanation
High. The path is reachable directly from `gateway.ProcessRequest`, which is the exact function wired to the public-facing HTTP server (`httpServer.SetHTTPRequestHandler(gw)`), and reaching `HandleLegacyUserMessage` requires only a well-formed, self-signed `api.Message` with `DonID` set and `Method == "web_api_trigger"` — `msg.Validate()` checks structural validity/signature format, not sender-to-topic authorization. The absence of allowlist logic is explicitly acknowledged in code via the TODO comment, indicating this is a known, currently-unaddressed gap rather than a speculative one.

### Recommendation
Enforce sender/topic authorization (allowlist) in `HandleLegacyUserMessage` before forwarding messages to DON nodes, and apply rate-limiting per-sender as already noted in the TODO. Additionally, validate that the caller-supplied `Timestamp` cannot be manipulated to bypass ordering assumptions on the DON side, and ensure `MessageID` collisions from unauthorized senders cannot be used to interfere with legitimate `savedCallbacks` entries.

### Proof of Concept
Not independently reproduced against a running Gateway instance in this analysis; the code path is demonstrated purely via static review of [1](#0-0)  and [2](#0-1) , showing that any structurally-valid, self-signed `web_api_trigger` `api.Message` submitted to the Gateway's public HTTP endpoint reaches `don.SendToNode` for all DON members without a sender/topic allowlist check.

### Citations

**File:** core/services/gateway/gateway.go (L220-272)
```go
// Called by the server
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
