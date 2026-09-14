### Title
Workflow-node `web_api_trigger` handler accepts payloads without verifying event freshness before dispatching to workflows - ([File: core/capabilities/webapi/trigger/trigger.go])

### Summary
On the workflow-DON side, `triggerConnectorHandler.HandleGatewayMessage` / `processTrigger` in `core/capabilities/webapi/trigger/trigger.go` decode and dispatch a user-originated `webapicap.TriggerRequestPayload` to registered workflows without ever inspecting `payload.Timestamp`, even though the field is explicitly documented as needing to be "within certain freshness to be processed."

### Finding Description
The `TriggerRequestPayload.Timestamp` field is defined with the explicit contract: "Timestamp of the event (unix time), needs to be within certain freshness to be processed" [1](#0-0) , mirrored in the JSON schema [2](#0-1) .

The gateway ingress point (`handler.HandleLegacyUserMessage`) does enforce this contract when the message first enters the gateway from a user, comparing `payload.Timestamp` against `h.config.MaxAllowedMessageAgeSec` and rejecting stale payloads [3](#0-2) .

However, the actual consumer of the payload — the workflow-DON-side trigger handler `triggerConnectorHandler.HandleGatewayMessage` — unmarshals the same `webapicap.TriggerRequestPayload` and passes it straight into `processTrigger` without any re-validation of `Timestamp` [4](#0-3) . `processTrigger` itself only checks topic matching, `allowedSenders`, and the per-sender rate limiter before emitting a `capabilities.TriggerEvent` (which still carries the original, unverified `Timestamp` field inside `wrappedPayload`) into the workflow engine [5](#0-4) .

This is the direct structural analog of the reported bug class: a caller-supplied "freshness" field (there: oracle price timestamp; here: trigger event `Timestamp`) is defined by the protocol/schema as requiring a recency check, but the component that actually consumes/acts on the value (dispatching workflow executions) never performs that check itself — it relies entirely on an upstream, and potentially bypassable/duplicable, gate.

### Impact Explanation
If a message reaches the node's `HandleGatewayMessage` path with a stale or crafted `Timestamp` (e.g., a message re-signed and re-sent by a node operator through the DON→node channel, a bug/skip in the gateway's own freshness enforcement, or any future code path that constructs a `TriggerRequestPayload` and calls into `HandleGatewayMessage`/`processTrigger` without going through `HandleLegacyUserMessage`'s check), the workflow engine will execute the associated workflow believing the event is current. Workflows that make time-sensitive decisions (e.g., "daily_price_update" as used in the very same test/example payloads) based on `payload.Timestamp` could act on stale data, since the enforcement point and the consumption point are decoupled and only one of the two layers performs validation.

### Likelihood Explanation
Moderate. The primary ingress path (`HandleLegacyUserMessage`) does check freshness today, which mitigates the most obvious exploitation route through the standard gateway HTTP path. However, the lack of defense-in-depth means any additional caller of `triggerConnectorHandler.HandleGatewayMessage` (multiple gateways, alternate dispatch paths, or future code changes) silently loses the freshness guarantee, since the check lives only in one specific handler function rather than in the trigger-processing logic itself that actually consumes the field.

### Recommendation
Move (or duplicate) the staleness check into `triggerConnectorHandler.processTrigger` / `HandleGatewayMessage` in `core/capabilities/webapi/trigger/trigger.go`, comparing `payload.Timestamp` against a configured maximum allowed age before matching topics/senders and emitting the `TriggerResponse`. This ensures the component that actually consumes the timestamp enforces the freshness contract documented in the schema, independent of which upstream gateway handler forwarded the message.

### Proof of Concept
1. Construct a `webapicap.TriggerRequestPayload` with `Timestamp` set to a value far in the past (e.g., hours old) and valid `Topics`/`TriggerEventId`.
2. Wrap it in an `api.Message`, sign it with an allowed sender's key, and invoke `triggerConnectorHandler.HandleGatewayMessage` directly with a `jsonrpc.Request` built from this message (bypassing `handler.HandleLegacyUserMessage`'s `MaxAllowedMessageAgeSec` check, e.g., via a different gateway path or a compromised/duplicated dispatch call).
3. Observe that `processTrigger` proceeds to match topics/senders/rate-limit and emits a `capabilities.TriggerResponse` carrying the stale `Timestamp` into the registered workflow channel — no error is raised for the payload's age, as confirmed by reading `core/capabilities/webapi/trigger/trigger.go` lines 84-210, which contain no reference to `payload.Timestamp` at all [6](#0-5) .

### Citations

**File:** core/capabilities/webapi/webapicap/event_trigger_generated.go (L105-107)
```go
	// Timestamp of the event (unix time), needs to be within certain freshness to be
	// processed.
	Timestamp int64 `json:"timestamp" yaml:"timestamp" mapstructure:"timestamp"`
```

**File:** core/capabilities/webapi/webapicap/event_trigger-schema.json (L64-68)
```json
                "timestamp": {
                    "type": "integer",
                    "format": "int64",
                    "description": "Timestamp of the event (unix time), needs to be within certain freshness to be processed."
                },
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

**File:** core/capabilities/webapi/trigger/trigger.go (L84-139)
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
