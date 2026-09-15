### Title
Missing sender allowlist authorization on the gateway's legacy `web_api_trigger` capability handler allows any signer to enqueue workflow trigger requests to all DON nodes - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
`HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` accepts any structurally-valid, signed `web_api_trigger` message and forwards it to every member of the DON, gated only by payload decoding, a timestamp freshness check, and a method-name check. [1](#0-0)  Directly before the method check, the code contains an explicit `// TODO: apply allowlist and rate-limiting here` comment, and no allowlist, sender authorization, or per-sender rate limit is actually invoked in this path. [2](#0-1) 

### Finding Description
The gateway's `ProcessRequest` dispatches "legacy" (DON-ID-addressed) requests by first calling `msg.Validate()`, which only checks structural constraints (field lengths, null-byte suffixes) and recovers the signer's address from the ECDSA signature via `ExtractSigner` — it does not check the signer against any allowlist or role. [3](#0-2)  Any actor holding an arbitrary ECDSA keypair can self-sign a message with `Sign` (no privileged key required) and produce a message that passes `Validate()`. [4](#0-3) 

After `Validate()` succeeds, `gateway.ProcessRequest` routes the message straight into `HandleLegacyUserMessage`. [5](#0-4)  Inside `HandleLegacyUserMessage`, the only checks performed are: payload JSON-decodability, non-zero timestamp, message-age/staleness, and that `msg.Body.Method == MethodWebAPITrigger`. [6](#0-5)  None of these checks constrain *who* (which `msg.Body.Sender`) may submit the trigger. The code explicitly flags this gap with the inline TODO immediately preceding the method-name check. [7](#0-6)  The request is then forwarded to every DON member via `don.SendToNode`. [8](#0-7) 

This is architecturally analogous to the CVE's missing-authorization pattern: an unprivileged, unauthenticated (in the authorization sense — merely self-signed, not permissioned) actor can invoke a privileged operation (triggering a workflow across an entire DON) because the enforcement point was never implemented, only stubbed with a TODO. The codebase's own test suite acknowledges this: a test comment states `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated`, confirming that sender authorization for this path is not verified anywhere in this handler's test coverage. [9](#0-8) 

By contrast, the newer non-legacy JSON-RPC trigger path (`v2/http_handler.go`'s `HandleJSONRPCUserMessage`) explicitly rejects legacy messages and routes through `triggerHandler.HandleUserTriggerRequest`, and the `webapi/trigger` package's `HandleGatewayMessage` performs an explicit allowed-sender check ("unauthorized Sender...") as shown in its test suite. [10](#0-9)  This confirms that sender-allowlisting is a known, implemented control elsewhere in the codebase for the equivalent operation, but is missing specifically in the legacy capabilities `handler.go` path.

### Impact Explanation
An external, unprivileged client that can reach the gateway's HTTP endpoint (the same internet-facing entry point used for legitimate `web_api_trigger` submissions) can self-sign and submit trigger messages for any DON ID it knows, causing the gateway to broadcast the message to all nodes in that DON as if from an authorized workflow trigger. This can result in unauthorized job/workflow runs being dispatched to node infrastructure, consuming node resources, potentially triggering downstream on-chain or state-changing actions (depending on what capability node-side handlers do with `web_api_trigger` payloads), and enabling request flooding since there's no per-sender rate limiting.

### Likelihood Explanation
High. No special privileges, credentials, or knowledge of internal secrets are required — an attacker only needs to know (or guess) a valid `DonID`, sign a syntactically valid message with any keypair they control, and send it to the gateway's public endpoint. The gap is self-documented via the TODO comment and an accompanying pending test-TODO, indicating this is a known, intentional deferral rather than a hardened control.

### Recommendation
Implement the sender allowlist/authorization check that the TODO comment references before forwarding requests in `HandleLegacyUserMessage`, mirroring the pattern used in `core/capabilities/webapi/trigger` (explicit allowed-sender verification) or the vault gateway handler's `AllowListBasedAuth`/`Authorizer` chain. Reject any messages whose recovered `msg.Body.Sender` is not present in a DON-configured allowlist, and add per-sender rate limiting as also flagged by the TODO.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no relation to any authorized workflow owner or node operator).
2. Construct an `api.Message` with `Body.Method = "web_api_trigger"`, a valid `Body.DonID` for a target DON, a fresh `Body.Payload` containing a `webapicap.TriggerRequestPayload` (with non-zero `Timestamp`), then call `msg.Sign(attackerPrivateKey)`.
3. Submit this message to the gateway's HTTP endpoint so it reaches `gateway.ProcessRequest` → `msg.Validate()` (succeeds, since it only checks structure/signature format, not sender identity) → `HandleLegacyUserMessage`.
4. Observe that `HandleLegacyUserMessage` proceeds past all checks (payload decodes, timestamp fresh, method matches) with no allowlist check invoked, and calls `don.SendToNode` for every DON member, delivering the attacker-controlled trigger request to the DON nodes. [11](#0-10)

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-421)
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

**File:** core/services/gateway/api/message.go (L96-108)
```go
func (m *Message) Sign(privateKey *ecdsa.PrivateKey) error {
	if m == nil {
		return errors.New("nil message")
	}
	rawData := GetRawMessageBody(&m.Body)
	signature, err := gw_common.SignData(privateKey, rawData...)
	if err != nil {
		return err
	}
	m.Signature = utils.StringToHex(string(signature))
	m.Body.Sender = strings.ToLower(crypto.PubkeyToAddress(privateKey.PublicKey).Hex())
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
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
