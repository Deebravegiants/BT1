### Title
Missing allowlist check lets any signer trigger free DON-wide compute via legacy WebAPI trigger handler - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The `capabilities` gateway handler's `HandleLegacyUserMessage` forwards every well-formed, self-signed legacy request to **all** members of a DON, with an explicit `// TODO: apply allowlist and rate-limiting here` marking that the intended authorization check was never implemented. This mirrors the UNCX report's core issue: a protocol-operated, gas/compute-free service (`AUTO_COLLECT_ACCOUNT` calling `collect` for anyone; here, the Gateway relaying to all DON nodes) executes work on behalf of an arbitrary, unauthenticated caller because the only "authentication" performed is a self-generated ECDSA signature check, not an authorization/allowlist check.

### Finding Description
`Message.Validate()` only verifies signature format/length and recovers a signer address from the signature — it does not check that the signer is a known/allowlisted client: [1](#0-0) 

`HandleLegacyUserMessage` receives this validated message, performs staleness/method checks, then — per its own comment — is missing the allowlist/rate-limit enforcement that was intended to gate it, and unconditionally broadcasts the request to every DON member: [2](#0-1) 

Since anyone can generate an ECDSA keypair and self-sign an arbitrary payload with a valid `MessageID`/`Method`/`DonID`, this signature check imposes no real access control on who may invoke this path. This is reached directly from the internet-facing gateway entrypoint `gateway.ProcessRequest`, which routes legacy requests (identified by a non-empty `DonID`) to the handler after only calling `msg.Validate()`: [3](#0-2) 

This is structurally the same defect pattern as the UNCX bug: a component designated to act as a trusted intermediary that spends the protocol's own resources (there: `AUTO_COLLECT_ACCOUNT`'s gas; here: every node in the DON's compute/bandwidth to process and act on `web_api_trigger` payloads) does so for input chosen entirely by an unauthenticated/unprivileged caller, with no whitelist enforced at the point of dispatch, despite the code explicitly acknowledging (via the TODO) that such a check was intended.

### Impact Explanation
An unprivileged, unauthenticated caller who can reach the Gateway's legacy endpoint can force every node of a target DON to receive and process a `web_api_trigger` message and (per `handleWebAPIOutgoingMessage`) subsequently trigger an outbound HTTP request to an attacker-controlled URL for every node in the DON. This is a "free" resource-consumption/griefing primitive analogous to gas siphoning: the caller supplies zero cost/collateral while causing DON-wide compute and network I/O, and can be used to run unauthorized triggers on nodes that were never intended to serve this specific unauthenticated client.

### Likelihood Explanation
Reachability requires only crafting a JSON-RPC (or legacy) request with a valid `DonID`, a self-signed `Message`, and a `web_api_trigger` payload against the internet-facing gateway HTTP endpoint — no privileged credentials or node compromise are needed, only knowledge of a valid `DonID` (which is not treated as a secret). The explicit `TODO: apply allowlist and rate-limiting here` in shipped code confirms the gap is not a hypothetical.

### Recommendation
Enforce an allowlist/subscription check (e.g., verifying `msg.Body.Sender` against a per-DON or per-workflow allowlist) and rate limiting in `HandleLegacyUserMessage` before dispatching to `don.SendToNode` for any DON member, matching the TODO and mirroring the allowlist enforcement already used elsewhere in the gateway/vault handlers (e.g., `Authorizer.AuthorizeRequest` in the vault gateway handler).

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration needed).
2. Construct an `api.Message` with a valid `MessageID`, `Method: "web_api_trigger"`, a target `DonID` of a live DON, and a `webapicap.TriggerRequestPayload` with a fresh `Timestamp`.
3. Sign it with the throwaway key via `Message.Sign`, satisfying `Validate()`.
4. Submit it to the Gateway's HTTP endpoint invoking `gateway.ProcessRequest` (legacy path, `DonID` set).
5. Observe `HandleLegacyUserMessage` skip any allowlist check (per the TODO) and call `don.SendToNode` for every member in `h.donConfig.Members`, causing all DON nodes to process the message and, if configured to act on `web_api_target`/outgoing payloads, issue outbound HTTP calls dictated by the attacker. [4](#0-3)

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

**File:** core/services/gateway/gateway.go (L253-266)
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

```
