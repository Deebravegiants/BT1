### Title
Missing Allowlist Enforcement on Gateway Legacy WebAPI Trigger Messages Permits Unauthenticated DON Message Injection - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The Chainlink gateway's legacy message path validates only that an inbound `api.Message` carries a *syntactically valid, self-consistent* ECDSA signature — it never checks that the recovered signer is an allowlisted/authorized caller before the message is forwarded to every node in the target DON. This mirrors the MacVim IPC flaw: a channel intended to be usable only by a vetted counterpart instead accepts input from *any* caller who can produce a valid credential (there, any local process; here, any keypair the attacker controls), because the enforcement point the code assumes exists is missing.

### Finding Description
`api.Message.Validate()` in [1](#0-0)  only checks field lengths and that the signature recovers to *some* Ethereum address via `ExtractSigner`; it does not verify that address against any allowlist, DON membership list, or workflow-owner registry. `ExtractSigner` simply recovers whichever key signed the payload — an attacker can generate an arbitrary private key locally, sign an `api.Message`, and it will pass `Validate()` unconditionally.

The gateway's public entrypoint `gateway.ProcessRequest` decodes the JSON-RPC request and, for legacy DON-ID-addressed messages, calls `msg.Validate()` and routes directly to the target DON's handler: [2](#0-1) .

That handler, `handler.HandleLegacyUserMessage` in the WebAPI capabilities handler, performs payload decoding, a staleness/timestamp check, and a method check — but the allowlist/rate-limit step is explicitly a stub, marked by its own `TODO` comment, and is never implemented before the message is broadcast to every DON member: [3](#0-2) 

There is no other authorization gate on this path: the only "authentication" performed is the self-consistency check in `Validate()`, which any unprivileged actor can satisfy trivially by signing with a throwaway key they generate themselves.

### Impact Explanation
Any unauthenticated network client that can reach the gateway's HTTP JSON-RPC endpoint can craft a `web_api_trigger` legacy message, sign it with a self-generated key, and have the gateway broadcast it to every node (`don.SendToNode`) in a target workflow DON. This is a request-forwarding/allowlist bypass at the internet-facing gateway: the caller does not need to be a registered workflow owner, an allowlisted requester, or hold any node-issued credential. Depending on downstream node-side trigger handling, this can result in unauthorized workflow trigger invocation (unauthorized job run) originating from an unprivileged actor — directly matching the "allowlist or quota bypass" / "unauthorized job run" impact classes for this report.

### Likelihood Explanation
High. The only barrier is producing a message that satisfies `Message.Validate()`, which requires nothing more than a valid ECDSA signature over the message body — trivially generated client-side with no interaction with the gateway or DON operators. The missing check is explicitly called out by the developers' own `TODO: apply allowlist and rate-limiting here` comment, confirming the gap is a known incomplete implementation rather than a hardened design decision.

### Recommendation
Implement the allowlist and rate-limiting check called out by the TODO in `HandleLegacyUserMessage` before saving the callback and forwarding to DON members — validate the recovered `msg.Body.Sender` against the DON's configured allowlist (or an equivalent owner/subscription registry, similar to `AllowListBasedAuth` used by the vault gateway handler) and enforce per-sender rate limits, rejecting unallowlisted senders with an authorization error prior to any `don.SendToNode` call.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration with the gateway/DON required).
2. Construct an `api.Message` with `Body.Method = "web_api_trigger"`, a fresh `MessageID`, a valid `DonID` for a target DON, and a `TriggerRequestPayload` with a current `Timestamp`.
3. Sign the message with the throwaway key via `Message.Sign`, producing a signature that passes `Message.Validate()`.
4. Wrap it as a legacy JSON-RPC request (`DonID` populated) and POST it to the gateway's public HTTP endpoint handled by `gateway.ProcessRequest`.
5. Observe that `HandleLegacyUserMessage` skips any allowlist check and forwards the request to every member of `h.donConfig.Members` via `don.SendToNode`, despite the sender never having been vetted. [4](#0-3) [1](#0-0) [2](#0-1)

### Citations

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
