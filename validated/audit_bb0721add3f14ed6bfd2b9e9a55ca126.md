This confirms every element of the claim exactly matches the current code. Let me verify there's no allowlist enforcement elsewhere (e.g., in `ValidatedRequestFromMessage` or `don.SendToNode`) that would refute the claim.All claims in the report are verified against the current code exactly as described. `api.Message.Validate()` performs only field-length/format checks and calls `ExtractSigner()`, which recovers whatever address signed the payload with no check against any authorization list [1](#0-0) . `ExtractSigner` simply recovers the signer from the ECDSA signature over the message body with no allowlist lookup [2](#0-1) . `gateway.ProcessRequest` validates legacy DON-ID-addressed messages via `msg.Validate()` and routes straight to `h.HandleLegacyUserMessage` [3](#0-2) . Inside `HandleLegacyUserMessage`, the only checks performed are payload decoding, a timestamp/staleness check, and a method check; the allowlist/rate-limit step is an explicit `TODO` stub immediately before the message is forwarded to every DON member via `don.SendToNode` [4](#0-3) . A grep for `Allowlist`/`AllowList` in `handler.go` confirms there is no allowlist enforcement logic anywhere in this file — the two "matches" the search initially reported turn out to be non-existent on closer inspection (0 real matches), while the vault handler elsewhere in the gateway does implement `AllowListBasedAuth`, confirming the pattern exists in the codebase but is simply not applied here.

This is a genuine, currently-unfixed gap: the code path is fully reachable by any unauthenticated network client capable of POSTing to the gateway's public JSON-RPC endpoint, requires no operator/admin privilege, and the broken assumption (that some caller-authorization step exists before broadcasting to the DON) is explicitly acknowledged by the developers' own `TODO` comment rather than being a deliberate design choice under some other compensating control.

Audit Report

## Title
Missing Allowlist Enforcement on Gateway Legacy WebAPI Trigger Messages Permits Unauthenticated DON Message Injection - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
The gateway's legacy message path only verifies that an inbound `api.Message` carries a self-consistent ECDSA signature (via `Message.Validate()` / `ExtractSigner`), never checking the recovered signer against any allowlist, DON-owner registry, or subscription before forwarding the message to every node in the target DON. The allowlist/rate-limit check is an explicit, unimplemented `TODO` in `HandleLegacyUserMessage`, so any attacker who signs a message with a self-generated throwaway key can have it broadcast to all DON members.

## Finding Description
`api.Message.Validate()` checks field lengths/format and calls `ExtractSigner()`, which recovers whichever address signed the raw message body — it does not consult any allowlist [1](#0-0) , and `ExtractSigner` itself performs no authorization lookup [2](#0-1) . `gateway.ProcessRequest` calls this `Validate()` for legacy, DON-ID-addressed messages and then dispatches directly to `HandleLegacyUserMessage` on the target handler [3](#0-2) . Inside `HandleLegacyUserMessage`, after payload decoding and a staleness/timestamp check, the code has the comment `// TODO: apply allowlist and rate-limiting here` immediately followed by only a method-name check before the message is transformed and sent to every member of `h.donConfig.Members` via `don.SendToNode` [5](#0-4) . No other authorization gate exists on this path in this handler.

## Impact Explanation
Any unauthenticated network client reachable at the gateway's public JSON-RPC endpoint can craft and self-sign a `web_api_trigger` legacy message and have it forwarded to every node of a target workflow DON, without being a registered workflow owner or holding any node-issued credential. This is a concrete allowlist bypass / gateway request impersonation at the internet-facing boundary that can result in unauthorized workflow trigger invocation downstream, matching the in-scope "allowlist or quota bypass" / "unauthorized job run" impact categories.

## Likelihood Explanation
High. The only barrier is producing a syntactically valid signature over the message body, which requires nothing more than generating an ECDSA keypair locally — no interaction with the gateway or DON operators is needed beforehand, and the gap is confirmed by the developers' own unimplemented `TODO` rather than an intentional compensating control elsewhere in the codebase.

## Recommendation
Implement the allowlist/rate-limiting check called out by the `TODO` in `HandleLegacyUserMessage` before saving the callback and calling `don.SendToNode`: validate `msg.Body.Sender` against the DON's configured allowlist or owner/subscription registry (mirroring `AllowListBasedAuth` used in the vault gateway handler) and enforce per-sender rate limits, rejecting unallowlisted senders with an authorization error prior to broadcasting to DON members.

## Proof of Concept
1. Generate an arbitrary ECDSA keypair locally (no registration required).
2. Construct an `api.Message` with `Body.Method = "web_api_trigger"`, a fresh `MessageID`, a valid target `DonID`, and a `TriggerRequestPayload` with a current `Timestamp`.
3. Sign it with the throwaway key via `Message.Sign`, producing a signature that passes `Message.Validate()`.
4. Wrap as a legacy JSON-RPC request (with `DonID` populated) and POST to the gateway's public HTTP endpoint (`gateway.ProcessRequest`).
5. Observe `HandleLegacyUserMessage` skips any allowlist check and calls `don.SendToNode` for every member of `h.donConfig.Members`, despite the sender never having been vetted.

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

**File:** core/services/gateway/api/message.go (L124-134)
```go
func (m *Message) ExtractSigner() (signerAddress []byte, err error) {
	if m == nil {
		return nil, errors.New("nil message")
	}
	rawData := GetRawMessageBody(&m.Body)
	signatureBytes, err := hex.DecodeString(m.Signature)
	if err != nil {
		return nil, err
	}
	return gw_common.ExtractSigner(signatureBytes, rawData...)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-420)
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
