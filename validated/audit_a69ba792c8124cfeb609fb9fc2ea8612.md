Audit Report

## Title
Unprivileged users can DOS the Gateway and DON nodes via unrestricted `web_api_trigger` legacy messages - ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
`gateway.ProcessRequest` routes any legacy JSON-RPC request with a valid `DonID` to `handler.HandleLegacyUserMessage`, which only performs payload-decode, non-zero-timestamp, and staleness checks before fanning the message out to every DON member. [1](#0-0)  The code contains an explicit `// TODO: apply allowlist and rate-limiting here` immediately preceding the fan-out, and no allowlist or rate limiter is actually invoked on this path. [2](#0-1) 

## Finding Description
`msg.Validate()` requires a well-formed ECDSA signature and derives `m.Body.Sender` from it via `ExtractSigner`, [3](#0-2)  but this only proves message integrity/self-consistency — it does not check `Sender` against any allowlist. Since any attacker can generate their own keypair and self-sign an arbitrary payload, this signature check provides no actual authorization barrier. After `Validate()` succeeds, `HandleLegacyUserMessage` checks only timestamp freshness and method name before storing a callback and sending the request to `don.SendToNode` for every DON member — exactly as the TODO comment states, no allowlist or per-sender rate limit is applied. [4](#0-3)  This contrasts with the node-outgoing message path in the same handler, which does invoke `nodeRateLimiter.Allow`, confirming rate-limiting infrastructure exists but is not wired into this legacy user-message path. The maintainers' own test comment corroborates the gap is known and unresolved. [5](#0-4) 

## Impact Explanation
An attacker who can reach the gateway's public HTTP endpoint can generate arbitrary self-signed `web_api_trigger` messages with fresh timestamps and unique `MessageID`s, causing each to be fanned out to every DON member node and stored in `savedCallbacks` (bounded only by `MaxSavedCallbacks`, default 20000). This is a legitimate availability/DOS impact against the internet-facing Gateway and DON nodes, consuming gateway memory and node processing/network capacity without any authorization or throttling gate.

## Likelihood Explanation
High. No credential beyond the ability to compute an ECDSA signature over attacker-chosen data (trivial, self-generated key) is required — this is not gated by any pre-registered identity or role. The request only needs a valid `DonID`, `MethodWebAPITrigger`, and a recent timestamp, all attacker-controlled. This is reachable by any unauthenticated external client and repeatable at will.

## Recommendation
Implement the allowlist and rate-limiting logic referenced by the TODO in `HandleLegacyUserMessage` (`core/services/gateway/handlers/capabilities/handler.go`), checking `msg.Body.Sender` against a configured allowlist and applying a per-sender/global rate limiter (mirroring `nodeRateLimiter.Allow` or the v2 HTTP trigger handler's `authorizeRequest`/`checkRateLimit`) before storing the callback and forwarding the request to DON members.

## Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration/allowlisting required).
2. Construct a legacy `Message` with `Body.Method = "web_api_trigger"`, a valid `DonID`, unique `MessageID`, and a `TriggerRequestPayload` with `Timestamp = time.Now().Unix()`; sign it with the generated key via `Message.Sign`.
3. POST the JSON-RPC-wrapped message repeatedly to the gateway's HTTP endpoint (`gateway.ProcessRequest`).
4. Observe each request passes `Validate()` and the staleness/method checks in `HandleLegacyUserMessage`, is added to `savedCallbacks`, and is forwarded via `don.SendToNode` to every DON member — with no rejection based on sender identity or request rate, until `MaxSavedCallbacks` pruning is triggered.

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

**File:** core/services/gateway/api/message.go (L54-88)
```go
func (m *Message) Validate() error {
	if m == nil {
		return errors.New("nil message")
	}
	if len(m.Signature) != MessageSignatureHexEncodedLen {
		return errors.New("invalid hex-encoded signature length")
	}
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
	if len(m.Body.Method) == 0 || len(m.Body.Method) > MessageMethodMaxLen {
		return errors.New("invalid method name length")
	}
	if strings.HasSuffix(m.Body.Method, NullChar) {
		return errors.New("method name ending with null bytes")
	}
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L360-366)
```go
		handler.mu.Lock()
		require.Empty(t, handler.savedCallbacks, "error paths must not leave entries in savedCallbacks")
		handler.mu.Unlock()
	})

	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```
