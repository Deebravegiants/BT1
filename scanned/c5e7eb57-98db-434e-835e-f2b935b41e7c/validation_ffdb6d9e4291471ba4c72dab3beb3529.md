## Title
Missing sender allowlist enforcement in Gateway `HandleLegacyUserMessage` allows any signer to trigger workflow DON requests - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The LayerZero report describes a relayer that lets any user agent (UA) push messages into another UA's packet queue because sender-scoping is not enforced at the relaying layer, only checked deep inside `lz_receive`/`assert_trusted_packet` — after the packet is already queued and can no longer be safely discarded, freezing the bridge. The Chainlink Gateway has the analogous unprivileged-actor gap: `handler.HandleLegacyUserMessage`, which processes internet-facing `MethodWebAPITrigger` requests, has an explicit `// TODO: apply allowlist and rate-limiting here` and performs **no** sender/allowlist check before broadcasting the request to every DON member and reserving a callback slot keyed only by `MessageID`.

### Finding Description
`gateway.ProcessRequest` decodes and validates any signed message and dispatches legacy requests straight to `h.HandleLegacyUserMessage`: [1](#0-0) 

Inside the capabilities handler, `HandleLegacyUserMessage` validates payload structure, timestamp freshness, and method name, but the sender/UA is never checked against any allowlist before the message is dispatched to the whole DON — the TODO comment confirms this is a known, unaddressed gap: [2](#0-1) 

The handler's own test suite documents the same unresolved gap: "TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated." [3](#0-2) 

Just like the Move `endpoint::send` function accepting any `UA` capability and enqueuing a packet destined for the bridge before any trust check occurs, `HandleLegacyUserMessage` accepts any correctly-signed message (any Ethereum key can sign, since signature validity is the only cryptographic gate — see `Message.Validate` / `ExtractSigner`) and immediately fans it out to `don.SendToNode` for every DON member, and reserves an entry in `h.savedCallbacks` keyed solely by `MessageID`: [4](#0-3) [5](#0-4) 

There is no check that the signer/sender is a member of any allowlist authorized to trigger the target workflow before the request consumes DON node bandwidth and a saved-callback slot.

### Impact Explanation
Any external, unprivileged caller who can produce a validly-signed `MethodWebAPITrigger` message (an ordinary ECDSA keypair, not any special role) can:
- Force the Gateway to broadcast attacker-controlled payloads to every member of a workflow DON via `don.SendToNode`, regardless of whether that sender is authorized to trigger that DON's workflow.
- Occupy `savedCallbacks` slots (bounded only by `MaxSavedCallbacks`, default 20000) with unauthorized requests, contributing to resource exhaustion/DoS of the legitimate trigger pipeline, mirroring the "freeze/DoS via unauthorized message occupying the pending-request slot" pattern in the analog report.
- Because the allowlist check that should gate "who is allowed to trigger this workflow" doesn't exist at this layer, downstream node-side processing is the only remaining safeguard — matching the report's observation that unauthorized messages can occupy shared resources before deeper checks (if any exist there) reject them.

### Likelihood Explanation
High: the code path is reachable directly from `gateway.ProcessRequest`, the internet-facing entrypoint for legacy DON requests, and requires nothing more than a valid ECDSA signature over a `MethodWebAPITrigger` payload with a non-stale timestamp — no allowlist membership, no capability, no prior registration. The TODO comments in both the handler and its test file confirm the gap is known and currently unaddressed.

### Recommendation
Enforce a sender/UA allowlist check in `HandleLegacyUserMessage` (and equivalently in `HandleJSONRPCUserMessage`/`HandleGatewayMessage` paths that share this pattern) before dispatching to DON members or reserving a `savedCallbacks` entry. Scope the check per-DON/workflow the way LayerZero's remediation recommends scoping message channels by chain ID and UA address — i.e., validate `msg.Body.Sender` against the configured set of senders authorized for the target DON/workflow before any side effects (broadcast, callback reservation) occur.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair not present in any workflow-owner allowlist.
2. Craft an `api.Message` with `Body.Method = MethodWebAPITrigger`, a valid `Body.MessageID`, `Body.DonID` pointing at a real DON, and a `webapicap.TriggerRequestPayload` with a fresh `Timestamp`.
3. Sign the message with the arbitrary key (`msg.Sign(privateKey)`), producing a message that passes `Message.Validate()`.
4. POST it through the Gateway's HTTP endpoint to `gateway.ProcessRequest`.
5. Observe that `HandleLegacyUserMessage` accepts the message (no allowlist check), stores a `savedCallback`, and broadcasts the request to every member of the target DON — despite the sender having no authorization relationship with that DON/workflow.

### Citations

**File:** core/services/gateway/gateway.go (L253-275)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
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
