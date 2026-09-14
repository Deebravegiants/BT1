### Title
Signature Replay on Web API Trigger Gateway Messages Enables Unbounded Re-Triggering of Workflow Executions - ([File: core/capabilities/webapi/trigger/trigger.go])

### Summary
The gateway `Message` signing scheme used across `core/services/gateway/api/message.go` binds a signature only to `MessageID`, `Method`, `DonID`, `Receiver`, and `Payload` [1](#0-0) , with no chain/session/nonce-lifetime binding beyond an attacker-controlled `MessageID` field. The `triggerConnectorHandler.HandleGatewayMessage` in `core/capabilities/webapi/trigger/trigger.go` consumes such signed messages to fire workflow executions via `processTrigger`, and performs **no replay/dedup check** against previously-seen `MessageID`/signature before invoking the trigger logic [2](#0-1) . This mirrors the root cause of the Sherlock M-3 finding: a validly-signed request lacking a nonce/expiry can be captured and resubmitted indefinitely to repeatedly trigger privileged effects.

### Finding Description
`Message.Sign`/`Message.Validate` recovers the signer strictly from the message body bytes (`GetRawMessageBody`) and signature, with no timestamp or monotonically-increasing nonce enforced against the signer's prior usage [3](#0-2) . `RequestCache.NewRequest` in `core/services/gateway/handlers/common/requestcache.go` does deduplicate concurrently-pending requests keyed by `(sender, MessageID)`, but the entry is deleted as soon as a response is produced/timed out [4](#0-3) [5](#0-4)  — this is a transient in-flight guard, not persistent replay protection.

Critically, `triggerConnectorHandler.HandleGatewayMessage` does not even use `RequestCache`; it validates the message via `hc.ValidatedMessageFromReq` (signature/shape check only) and immediately calls `processTrigger`, which fans the payload out to every registered workflow whose `allowedTopics`/`allowedSenders` match [6](#0-5) [7](#0-6) . There is no persistent record preventing the exact same `(Signature, Body)` from being resubmitted by any party who observes it in transit or in logs, since the gateway is an internet-facing component receiving JSON-RPC requests from external callers.

### Impact Explanation
An attacker who captures one valid signed web-api-trigger message (e.g., by observing network traffic, logs, or a legitimate but non-confidential channel) can replay it repeatedly against the gateway. Each replay passes signature validation (the signature is still valid — nothing invalidates it after first use) and re-enters `processTrigger`, re-emitting a `TriggerResponse` that starts workflow execution for every matching registered workflow, subject only to the per-sender/global `rateLimiter`. This allows unauthorized, repeated triggering of workflow executions without the original signer's continued consent — an analog to "unauthorized job run" impact, and could be leveraged to exhaust workflow execution capacity/state or, if a workflow performs fund-moving actions on trigger, to repeatedly re-invoke those actions.

### Likelihood Explanation
Likelihood is dependent on an attacker being able to observe a previously-submitted, validly-signed message (e.g., via network capture, verbose logging, or a compromised/malicious client relay), which is a realistic scenario for JSON-RPC payloads sent over the gateway's connector interface. Given the rate limiter only throttles volume and does not block distinct-in-time replay of an already-used message, a patient attacker retains a permanently valid "replay token."

### Recommendation
Bind gateway `Message` signatures to a bounded validity window and/or a per-sender monotonic nonce that is persisted (not just held transiently in `RequestCache`), and reject messages whose `MessageID`/nonce has already been consumed by that sender, similar to the fix pattern recommended in the referenced report (add nonce/timestamp to the signed payload and track consumed nonces per signer) — apply this specifically in `triggerConnectorHandler.HandleGatewayMessage`/`processTrigger` before dispatching to registered workflow channels, not only in the transient `RequestCache`.

### Proof of Concept
Not executed (index-only analysis, no runtime access). Conceptual PoC: (1) legitimate sender signs and submits a `web_api_trigger` `Message` via the gateway; (2) attacker captures the full JSON-RPC request (`Signature` + `Body`); (3) attacker resubmits the identical request to the gateway any number of times after the original request has been processed and evicted from `RequestCache`; (4) each resubmission passes `Message.Validate`/`ExtractSigner` and re-invokes `processTrigger`, causing repeated workflow trigger events for all matching registered workflows.

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

**File:** core/services/gateway/api/message.go (L90-107)
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
```

**File:** core/capabilities/webapi/trigger/trigger.go (L85-164)
```go
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
```

**File:** core/capabilities/webapi/trigger/trigger.go (L167-201)
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

```

**File:** core/services/gateway/handlers/common/requestcache.go (L50-76)
```go
func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
	codec := api.JSONRPCCodec{}
	timer := time.AfterFunc(c.timeout, func() {
		err := c.deleteAndSendOnce(key, handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(request), ErrorCode: api.RequestTimeoutError})
		if err != nil {
			lggr.Errorw("failed to send timeout response", "error", err)
		}
	})
	c.cache[key] = &pendingRequest[T]{Callback: callback, responseData: responseData, timeoutTimer: timer}
	return nil
}
```

**File:** core/services/gateway/handlers/common/requestcache.go (L111-122)
```go
func (c *requestCache[T]) deleteAndSendOnce(key globalID, callbackResponse handlers.UserCallbackPayload) error {
	c.mu.Lock()
	entry, deleted := c.cache[key]
	delete(c.cache, key)
	c.mu.Unlock()
	if deleted {
		entry.timeoutTimer.Stop()
		return entry.SendResponse(callbackResponse)
	}

	return nil
}
```
