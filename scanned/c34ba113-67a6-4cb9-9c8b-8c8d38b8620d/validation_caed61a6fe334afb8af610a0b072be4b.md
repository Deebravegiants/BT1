### Title
Web API Trigger requests can be replayed to trigger duplicate/unauthorized workflow executions - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Gateway's legacy user-message path (`api.Message`) is signed over `MessageID`, `Method`, `DonID`, `Receiver` and `Payload`, but the only replay defense applied by the receiving handler is a coarse timestamp-freshness check on the trigger payload. There is no dedicated, persisted record of "already-consumed" trigger events, so any signed `web-api-trigger` request can be resubmitted verbatim by anyone who has observed it (the caller itself, a logging/proxy layer, or anyone who intercepts the request) any number of times within the freshness window, causing the connected DON to re-execute the workflow trigger each time.

### Finding Description
`Message.Sign`/`Message.Validate` in `core/services/gateway/api/message.go` compute the signature over `MessageID`, `Method`, `DonID`, `Receiver`, and `Payload` [1](#0-0) . This binds the signature to the content of one specific request, but nothing in `Validate()` or downstream processing tracks whether a given signed message (or its `MessageID`/`trigger_event_id`) has ever been seen before [2](#0-1) .

The gateway's capabilities handler accepts the message and applies only a staleness check against `payload.Timestamp` compared to `MaxAllowedMessageAgeSec`: [3](#0-2) 

If the timestamp is within the allowed age, the handler unconditionally forwards the message to every DON member and stores a callback keyed by `MessageID`, silently overwriting any earlier entry for the same ID: [4](#0-3) 

On the node side, `triggerConnectorHandler.processTrigger` derives `TriggerEventID := body.Sender + payload.TriggerEventId` and immediately fires the trigger to the registered workflow — there is no lookup against previously-processed `TriggerEventID`s before dispatching: [5](#0-4) 

This mirrors the reported zNS class of bug: the signed payload authenticates *who* sent a message and *what* it contains, but does not uniquely and persistently mark a specific request as "spent," so a valid signature can legitimately be replayed as long as it remains within whatever loose freshness window is configured (`MaxAllowedMessageAgeSec`), just as the zNS `approvedBids`-based signature scheme could be replayed absent a dedicated used-nonce store.

### Impact Explanation
An attacker who can observe or capture one legitimately signed Web API Trigger request (e.g., via a compromised transport hop, a monitoring/logging pipeline, or simply resending their own earlier valid request) can resend it to the gateway multiple times before it becomes stale. Each resend causes the gateway to re-forward the message to all DON members, and each DON node re-fires the trigger into the connected workflow, resulting in duplicate/unauthorized workflow executions. Depending on what the triggered workflow does (e.g., initiating fund transfers, external calls, or job runs), this can produce duplicated side effects, resource exhaustion, or unintended repeated actions — comparable in class to unauthorized/duplicate job runs.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to have obtained a copy of a validly signed message (their own, or one they observed), and the replay only works inside the configured `MaxAllowedMessageAgeSec` window. There is no cryptographic barrier once a valid signed message is possessed — no server-side check ever renders a specific signed message "already used," so the only limiting factor is the freshness window, which is a deployment-configurable value and offers no protection at all against the sender itself simply resubmitting their own message multiple times within that window.

### Recommendation
Introduce a dedicated, persisted anti-replay store (e.g., an LRU/TTL cache or DB table) keyed by a unique identifier of the request (`Body.Sender + Body.MessageID` or `Body.Sender + payload.TriggerEventId`), and reject any request whose identifier has already been recorded, in addition to the existing timestamp-freshness check. This should be validated before the message is forwarded to DON members in `HandleLegacyUserMessage`, mirroring the fix pattern recommended for the zNS report (a dedicated mapping/record of previously consumed requests rather than relying solely on message freshness).

### Proof of Concept
1. Register a `web-api-trigger` workflow with an `allowedSender` and `allowedTopic`.
2. Send one valid signed `api.Message` (method `web_api_trigger`) to the gateway HTTP endpoint, with `payload.Timestamp` set to `now`.
3. Within `MaxAllowedMessageAgeSec` (handler.go:372), resend the exact same signed message bytes N more times.
4. Observe (per `handler.go:411-420` and `trigger.go:106-139`) that each resend passes `Validate()`/staleness checks, is forwarded to all DON members again, and `processTrigger` fires the workflow trigger again — resulting in N+1 workflow executions from a single originally authorized request.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-420)
```go
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

**File:** core/capabilities/webapi/trigger/trigger.go (L106-139)
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
```
