## Title
Web API Trigger Gateway Messages Lack Replay Protection, Enabling Signature Replay to Repeatedly Trigger Workflow Executions - (File: `core/capabilities/webapi/trigger/trigger.go`)

### Summary
The `web-api-trigger` capability's gateway message handler validates only the ECDSA signature, sender allowlist membership, and topic matching on incoming `TriggerRequestPayload` messages — it never enforces uniqueness or freshness of the signed message itself. A single previously-observed, validly-signed trigger message can be resent to the DON any number of times (subject only to a per-sender rate limiter) and will be accepted and re-processed every time, exactly the "signature replay" bug class flagged in the referenced report (`castVoteBySig` lacking a nonce).

### Finding Description
Gateway messages are signed over `MessageID`, `Method`, `DonID`, `Receiver`, and `Payload` in `core/services/gateway/api/message.go`: [1](#0-0) 

`Message.Validate()` verifies the signature is well-formed and recovers the signer, but does not track whether that exact `(MessageID, Signature)` pair has been seen before: [2](#0-1) 

The Web API Trigger's `HandleGatewayMessage` decodes the signed message and immediately dispatches to `processTrigger`, performing only sender-allowlist and per-topic rate-limit checks — no message ID uniqueness check, no timestamp/staleness check, and no consumption of a nonce: [3](#0-2) [4](#0-3) 

This is in stark contrast to the sibling legacy handler `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go`, which explicitly checks `payload.Timestamp` for staleness before further processing: [5](#0-4) 

and the vault/confidential-relay/JWT-based flows in this same repo which do enforce single-use semantics via `RequestReplayGuard` (digest-based) or JWT `jti` tracking: [6](#0-5) [7](#0-6) 

The web-api-trigger path has none of these protections — the `webapiTrigger` struct only tracks `allowedSenders`, `allowedTopics`, and a `rateLimiter`, with no seen-message-ID cache: [8](#0-7) 

### Impact Explanation
Because the trigger message's signature does not bind to a single-use nonce that is checked server-side, any actor who observes (or is the original sender of) a validly signed trigger message can replay it to the DON's gateway connector repeatedly. Each successful replay re-enters `processTrigger`, matches the same `allowedSenders`/`allowedTopics` checks, and pushes a new `capabilities.TriggerResponse` onto the registered workflow's channel, causing the workflow to execute again. This allows unauthorized/duplicated job (workflow) execution purely from re-transmission of a previously valid signed request, consistent with the "unauthorized job run" impact category. Since `TriggerEventID` is derived deterministically from `body.Sender + payload.TriggerEventId` (not from the DON-side message ID), downstream execution-ID generation does not itself prevent duplicate workflow starts at the trigger layer — the check happens only at dispatch time, not accumulation of prior deliveries.

### Likelihood Explanation
Likelihood is bounded primarily by two factors: (1) an actor must obtain a copy of a previously valid signed message (e.g., by being the original sender, or observing gateway traffic since Gateway↔node transport is not guaranteed confidential end-to-end in all deployments), and (2) the per-sender/per-topic `ratelimit.RateLimiter` throttles repeat submissions but does not prevent them entirely — a sender within their rate budget can resend the same captured message indefinitely. No cryptographic or state-based nonce check blocks this at any layer of the trigger's gateway message handling.

### Recommendation
Add replay protection to the Web API Trigger's gateway message pipeline, analogous to the `RequestReplayGuard` used in the vault handlers: track `MessageID` (or the full message digest) per sender/DON with an expiry window and reject any message whose ID has already been consumed, similar to how `HandleLegacyUserMessage` already checks payload timestamps for staleness. Concretely, in `processTrigger`/`HandleGatewayMessage` (`core/capabilities/webapi/trigger/trigger.go`), record `body.MessageID` (or `body.Sender+body.MessageID`) upon first successful processing and reject duplicate/reused IDs, and/or require the signed payload to include a timestamp that is validated for freshness the same way the legacy handler does.

### Proof of Concept
1. A valid `allowedSender` signs and sends a `web_api_trigger` message via the gateway (as in `TestTriggerExecute`'s "happy case single topic to single workflow"): [9](#0-8) 
2. Capture the exact signed `jsonrpc.Request[json.RawMessage]` (`gatewayRequest`) that was sent.
3. Call `h.trigger.HandleGatewayMessage(ctx, gatewayID, req)` again with the identical, unmodified request object (same `MessageID`, same signature).
4. Observe that the request again passes `hc.ValidatedMessageFromReq` (valid signature, unchanged fields) and `processTrigger` again dispatches to the sender-allowed/topic-matched workflow trigger channel, resulting in a second `capabilities.TriggerResponse` being emitted for what should be a single, already-processed request — with no error such as "message already processed" ever being raised, unlike the JWT-based or vault-based flows which explicitly reject a repeat request ID/digest.

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

**File:** core/services/gateway/api/message.go (L90-108)
```go
// Message signatures are over the following data:
//  1. MessageID aligned to 128 bytes
//  2. Method aligned to 64 bytes
//  3. DonID aligned to 64 bytes
//  4. Receiver (in hex) aligned to 42 bytes
//  5. Payload (raw bytes before parsing)
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

**File:** core/capabilities/webapi/trigger/trigger.go (L41-49)
```go
type webapiTrigger struct {
	workflowID     string
	allowedSenders map[string]bool
	allowedTopics  map[string]bool
	ch             chan<- capabilities.TriggerResponse // set nil after closing
	chWriteMu      sync.Mutex                          // must hold to send or close
	config         webapicap.TriggerConfig
	rateLimiter    *ratelimit.RateLimiter
}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L84-165)
```go
// processTrigger iterates over each topic, checking against senders and rateLimits, then starting event processing and responding
func (h *triggerConnectorHandler) processTrigger(ctx context.Context, gatewayID string, body *api.MessageBody, sender ethCommon.Address, payload webapicap.TriggerRequestPayload) error {
	// Pass on the payload with the expectation that it's in an acceptable format for the executor
	wrappedPayload, err := values.WrapMap(payload)
	if err != nil {
		return fmt.Errorf("error wrapping payload %w", err)
	}
	topics := payload.Topics

	// empty topics is error for V1
	if len(topics) == 0 {
		return errors.New("empty Workflow Topics")
	}

	h.mu.Lock()
	triggers := slices.Collect(maps.Values(h.registeredWorkflows))
	h.mu.Unlock()

	// workflows that have matched topics
	matchedWorkflows := 0
	// workflows that have matched topic and passed all checks
	fullyMatchedWorkflows := 0
	for _, trigger := range triggers {
		for _, topic := range topics {
			if trigger.allowedTopics[topic] {
				matchedWorkflows++
				if !trigger.allowedSenders[sender.String()] {
					err = fmt.Errorf("unauthorized Sender %s, messageID %s", sender.String(), body.MessageID)
					h.lggr.Debugw(err.Error())
					continue
				}
				if !trigger.rateLimiter.Allow(body.Sender) {
					err = fmt.Errorf("request rate-limited for sender %s, messageID %s", sender.String(), body.MessageID)
					continue
				}
				fullyMatchedWorkflows++
				TriggerEventID := body.Sender + payload.TriggerEventId

				// Emit trigger execution started event
				workflowExecutionID, genErr := events.GenerateExecutionID(trigger.workflowID, TriggerEventID)
				if genErr != nil {
					h.lggr.Errorw("failed to generate execution ID", "err", genErr)
					workflowExecutionID = ""
				}
				emitErr := events.EmitTriggerExecutionStarted(ctx, map[string]string{}, TriggerEventID, workflowExecutionID)
				if emitErr != nil {
					h.lggr.Errorw("failed to emit trigger execution started event", "err", emitErr)
				}

				tr := capabilities.TriggerResponse{
					Event: capabilities.TriggerEvent{
						TriggerType: TriggerType,
						ID:          TriggerEventID,
						Outputs:     wrappedPayload,
					},
				}
				trigger.chWriteMu.Lock()
				if trigger.ch == nil {
					trigger.chWriteMu.Unlock()
					return nil
				}
				select {
				case <-ctx.Done():
					trigger.chWriteMu.Unlock()
					return nil
				case trigger.ch <- tr:
					trigger.chWriteMu.Unlock()
					// Sending n topics that match a workflow with n allowedTopics, can only be triggered once.
					break
				}
			}
		}
	}
	if matchedWorkflows == 0 {
		return errors.New("no Matching Workflow Topics")
	}

	if fullyMatchedWorkflows > 0 {
		return nil
	}
	return err
}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L167-210)
```go
func (h *triggerConnectorHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) error {
	msg, err := hc.ValidatedMessageFromReq(req)
	if err != nil {
		h.lggr.Errorw("error validating message from request", "err", err, "request", req)
		return nil
	}
	body := &msg.Body
	sender := ethCommon.HexToAddress(body.Sender)
	var payload webapicap.TriggerRequestPayload
	err = json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw("error decoding payload", "err", err)
		err = h.sendResponse(ctx, gatewayID, body, ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: fmt.Errorf("error %s decoding payload", err.Error()).Error()})
		if err != nil {
			h.lggr.Errorw("error sending response", "err", err)
		}
		return nil
	}

	switch body.Method {
	case ghcapabilities.MethodWebAPITrigger:
		resp := h.processTrigger(ctx, gatewayID, body, sender, payload)
		var response ghcapabilities.TriggerResponsePayload
		if resp == nil {
			response = ghcapabilities.TriggerResponsePayload{Status: "ACCEPTED"}
		} else {
			response = ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: resp.Error()}
			h.lggr.Errorw("Error processing trigger", "gatewayID", gatewayID, "body", body, "response", resp)
		}
		err = h.sendResponse(ctx, gatewayID, body, response)
		if err != nil {
			h.lggr.Errorw("Error sending response", "body", body, "response", response, "err", err)
		}
		return nil

	default:
		h.lggr.Errorw("unsupported method", "id", gatewayID, "method", body.Method)
		err = h.sendResponse(ctx, gatewayID, body, ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: fmt.Errorf("unsupported method %s", body.Method).Error()})
		if err != nil {
			h.lggr.Errorw("error sending response", "err", err)
		}
	}
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-383)
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
```

**File:** core/capabilities/vault/request_replay_guard.go (L30-47)
```go
// CheckAndRecord returns ErrRequestAlreadySeen if the digest was previously
// recorded and has not yet expired. Otherwise it records the digest with
// the given expiry timestamp (unix seconds, UTC).
//
// Expired entries are cleaned up on every call.
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler_test.go (L1193-1217)
```go
	t.Run("JWT replay protection", func(t *testing.T) {
		params := json.RawMessage(`{"test": "data"}`)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id-replay",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &params,
		}

		token, err := utils.CreateRequestJWT(*req)
		require.NoError(t, err)

		tokenString, err := token.SignedString(privateKey)
		require.NoError(t, err)

		key, err := handler.Authorize(workflowID, tokenString, req)
		require.NoError(t, err)
		require.NotNil(t, key)

		// Second authorization with same JWT should fail (replay attack)
		key, err = handler.Authorize(workflowID, tokenString, req)
		require.Error(t, err)
		require.Contains(t, err.Error(), "JWT token has already been used. Please generate a new one with new id (jti)")
		require.Nil(t, key)
	})
```

**File:** core/capabilities/webapi/trigger/trigger_test.go (L193-215)
```go
	t.Run("happy case single topic to single workflow", func(t *testing.T) {
		gatewayRequest := gatewayRequest(t, privateKey1, []string{"daily_price_update"}, "")

		th.connector.EXPECT().SignMessage(mock.Anything, mock.Anything).Return([]byte("signature"), nil).Once()
		th.connector.On("SendToGateway", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			resp, err2 := getResponseFromArg(args.Get(2))
			require.NoError(t, err2)
			require.Equal(t, ghcapabilities.TriggerResponsePayload{Status: "ACCEPTED"}, resp)
		}).Return(nil).Once()

		th.trigger.HandleGatewayMessage(ctx, "gateway1", gatewayRequest)

		received, chanErr := requireChanMsg(t, channel)
		require.Equal(t, TriggerType, received.Event.TriggerType)
		require.NoError(t, chanErr)

		requireNoChanMsg(t, channel2)
		data := received.Event.Outputs
		var payload webapicap.TriggerRequestPayload
		unwrapErr := data.UnwrapTo(&payload)
		require.NoError(t, unwrapErr)
		require.Equal(t, []string{"daily_price_update"}, payload.Topics)
	})
```
