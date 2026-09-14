## Analysis

The reported bug class is **missing validation of attacker-controlled input (`userData`) before it is trusted and acted upon by a privileged execution path** (Balancer flash-loan callback executing arbitrary encoded instructions without validating the caller/data). The closest reachable analog in this repo is the Chainlink Gateway's **capabilities handler**, which forwards unauthenticated, unauthorized user messages straight to all DON member nodes without any allowlist or sender authorization check — an explicitly acknowledged gap in the code itself.

### Title
Unauthenticated/unauthorized `web_api_trigger` messages are forwarded to all DON nodes without allowlist or sender validation - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`HandleLegacyUserMessage` in the gateway's capabilities handler accepts any correctly-signed `api.Message` from an unprivileged HTTP client, and — apart from checking payload shape, method name, and staleness — forwards it to every member node of the target workflow DON without verifying that the sender is allowlisted or otherwise authorized to trigger that workflow's DON.

### Finding Description
`msg.Validate()` in `core/services/gateway/api/message.go` only checks structural constraints (signature length, field lengths, null-byte suffixes) and recovers the signer address into `Body.Sender` from an ECDSA signature that anyone can produce with any keypair [1](#0-0) . `HandleLegacyUserMessage` then decodes the payload, checks it is not stale, checks the method equals `MethodWebAPITrigger`, and immediately fans the raw request out to every DON member — with an explicit `// TODO: apply allowlist and rate-limiting here` comment marking the missing check [2](#0-1) . The handler's own test suite documents this same gap: `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated` [3](#0-2) . This mirrors the AffineDeFi root cause: user-supplied data (here, an arbitrary signed trigger message with attacker-chosen `Topics`/`Params`) is accepted and propagated into node-side execution without validating that the sender is entitled to invoke it, relying only on downstream node logic (not the gateway) to potentially catch abuse.

Note that this is different from the sibling V2 HTTP trigger handler path (`core/capabilities/webapi/trigger/trigger.go`), which does enforce `trigger.allowedSenders[sender.String()]` before dispatching a trigger event [4](#0-3) . The legacy `capabilities` gateway handler's `HandleLegacyUserMessage` path lacks this equivalent check entirely before forwarding to nodes.

### Impact Explanation
Because the message is forwarded to all DON member nodes before any allowlist check, any unprivileged caller able to reach the gateway's public endpoint and produce a validly-shaped signed message can cause the gateway to relay attacker-chosen `web_api_trigger` payloads (arbitrary `Topics`, `Params`, `TriggerEventId`) to every node in a workflow DON. Depending on how node-side capability/trigger logic consumes this forwarded message, this could result in spurious/unauthorized workflow trigger events being considered by nodes, resource exhaustion (broadcasting to all DON members per request), or bypass of the intended allowlist boundary that other trigger paths (e.g., the V2 HTTP handler) explicitly enforce.

### Likelihood Explanation
High reachability: this is a public, unauthenticated (from the gateway's perspective) HTTP-facing entrypoint — signature validity does not imply authorization, since anyone can generate an ECDSA keypair and sign their own message. The missing check is explicitly flagged by two independent TODO comments in production code and tests, confirming it is a known, unresolved gap rather than a false positive from downstream enforcement.

### Recommendation
Before forwarding a `HandleLegacyUserMessage` request to DON member nodes, validate the recovered `msg.Body.Sender` against a workflow/DON-scoped allowlist (mirroring `allowedSenders` in `core/capabilities/webapi/trigger/trigger.go`) and apply per-sender rate limiting, exactly as flagged by the existing TODOs, prior to inserting the callback into `savedCallbacks` and calling `don.SendToNode`.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair not associated with any registered/allowlisted sender.
2. Construct an `api.Message` with `Body.Method = "web_api_trigger"`, a fresh `TriggerRequestPayload` (`TriggerId`, `TriggerEventId`, current `Timestamp`, arbitrary `Topics`/`Params`), and sign it with the arbitrary key (as done in `triggerRequest` helper) [5](#0-4) .
3. Submit it to the gateway's legacy user-message endpoint for the target DON.
4. Observe that `HandleLegacyUserMessage` accepts it (payload/method/staleness checks pass) and forwards the request to every member node of the DON without any allowlist check, per the current implementation lacking the marked TODO enforcement [6](#0-5) .

### Citations

**File:** core/services/gateway/api/message.go (L54-87)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L193-233)
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
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L106-114)
```go
	for _, trigger := range triggers {
		for _, topic := range topics {
			if trigger.allowedTopics[topic] {
				matchedWorkflows++
				if !trigger.allowedSenders[sender.String()] {
					err = fmt.Errorf("unauthorized Sender %s, messageID %s", sender.String(), body.MessageID)
					h.lggr.Debugw(err.Error())
					continue
				}
```
