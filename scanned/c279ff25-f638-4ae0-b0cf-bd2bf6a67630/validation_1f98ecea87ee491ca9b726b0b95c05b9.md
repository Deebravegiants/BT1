Found it: `processTrigger` in `core/capabilities/webapi/trigger/trigger.go` is the legacy WebAPI trigger handler, invoked from `HandleGatewayMessage` after `hc.ValidatedMessageFromReq` validates the signature. The `TriggerRequestPayload` schema declares a `timestamp` field described as needing "to be within certain freshness to be processed," but `processTrigger` never checks it — it only checks `allowedSenders`, `allowedTopics`, and a per-sender rate limiter.### Title
Missing timestamp/freshness and event-ID replay validation in `triggerConnectorHandler#processTrigger` allows repeated execution of a signed WebAPI trigger message - ([File: core/capabilities/webapi/trigger/trigger.go])

### Summary
The legacy WebAPI trigger capability signs and validates messages via the Gateway's generic `Message` signature scheme (`MessageID`, `Method`, `DonID`, `Receiver`, `Payload`), but the trigger-specific payload's `timestamp` field — explicitly documented as needing to be "within certain freshness to be processed" — is never checked in the handler that actually fires the workflow trigger. This mirrors the audited HardenedTopupProxy bug class: a signature/message that authorizes an action is not bound to a single-use nonce/freshness window, so it can be resubmitted to repeat the authorized action.

### Finding Description
`triggerConnectorHandler.HandleGatewayMessage` in `core/capabilities/webapi/trigger/trigger.go` validates the incoming Gateway message via `hc.ValidatedMessageFromReq`, which only checks the ECDSA signature over `MessageID`/`Method`/`DonID`/`Receiver`/`Payload` fields [1](#0-0) . It then unmarshals the payload into a `webapicap.TriggerRequestPayload` and dispatches to `processTrigger` [2](#0-1) .

`processTrigger` only checks: (1) that topics are non-empty, (2) that the sender is in `trigger.allowedSenders`, and (3) a per-sender rate limiter — it never inspects `payload.Timestamp` or de-duplicates by `payload.TriggerEventId` before delivering the event to the registered workflow channel: [3](#0-2) 

The `TriggerRequestPayload.Timestamp` field's JSON-schema comment explicitly states this freshness requirement, implying an intended (but unimplemented) protection: [4](#0-3) 

Because signature validation covers only the outer `Message` envelope (which includes `MessageID`, a value chosen by the sender and not tracked/consumed by the Gateway or the trigger handler as a one-time nonce), a previously captured, validly-signed trigger `Message`/`TriggerRequestPayload` can be resubmitted to the Gateway (`HandleGatewayMessage`) any number of times before rate-limiting resets, each time passing signature validation and re-invoking `processTrigger`, which re-delivers the trigger event to the subscribed workflow with no timestamp or event-ID replay check.

This is analogous to the reported bug class: the message that authorizes/triggers an action (`constructMsg`/signature in the original report) omits a nonce, letting a legitimately-signed message be replayed to re-trigger the protected action multiple times.

### Impact Explanation
A replayed trigger message causes the connected workflow(s) subscribed to the matching topic/sender to be re-triggered with stale data, potentially causing duplicate downstream actions (e.g., duplicate on-chain writes, duplicate external side effects, or workflow-execution ID collisions/logic errors) driven by data that is no longer fresh. Unlike the well-protected v2 HTTP trigger handler (`http_trigger_handler.go`), which explicitly rejects duplicate request IDs/JWTs ("in-flight request", "token has already been used"), and unlike the remote trigger publisher/subscriber, which use `messageCache`/`ackReplayCache` with `MessageExpiry` to bound and dedupe events, this legacy v1 WebAPI trigger path in `trigger.go` has no equivalent protection.

### Likelihood Explanation
Exploitation requires an attacker to capture a validly-signed `Message` for the WebAPI trigger (e.g., by observing gateway traffic, a compromised/eavesdropping intermediary, or a malicious downstream consumer of the message), which is a non-trivial but realistic threat in a system designed with per-message signing specifically to prevent tampering and forgery. Given that the surrounding v2 trigger paths and remote trigger paths in the same codebase implement explicit freshness/replay defenses, the omission in this specific v1 handler appears to be a gap rather than an accepted design decision, and the rate limiter (`trigger.rateLimiter.Allow`) does not prevent replay — it only throttles request frequency and would still allow periodic repeated replays.

### Recommendation
In `processTrigger` (or earlier, in `HandleGatewayMessage`), before delivering the event to `trigger.ch`:
1. Validate `payload.Timestamp` against current time within an allowed skew window, rejecting stale messages, consistent with the documented "freshness" intent in the schema.
2. Track already-processed `(sender, TriggerEventId)` pairs (similar to `messagecache`/`ackReplayCache` used in `core/capabilities/remote/trigger_subscriber.go`) with a TTL-bound cache, and reject/ignore duplicates instead of re-delivering to the workflow trigger channel.

### Proof of Concept
1. A workflow registers a WebAPI trigger with `allowedSenders`/`allowedTopics` via `triggerConnectorHandler.RegisterTrigger`.
2. An authorized sender signs and sends one valid `Message` containing a `TriggerRequestPayload` (as constructed in `triggerRequest` test helper) to the Gateway, which forwards it to `HandleGatewayMessage` → `processTrigger`, successfully delivering a `TriggerResponse` to the workflow.
3. An attacker who has captured this exact signed `Message` (bytes unchanged) resubmits it to the Gateway again (assuming it is not rate-limited or after the rate-limit window resets). Because `msg.Validate()`/`ExtractSigner()` only re-verify the same static signature and `processTrigger` performs no timestamp/staleness or event-ID dedup check, the message passes validation again and is redelivered to `trigger.ch`, re-triggering the workflow with the original (now stale) payload. [3](#0-2) [5](#0-4)

### Citations

**File:** core/services/gateway/handlers/common/message_util.go (L34-57)
```go
// ValidatedMessageFromReq validated and extracts a legacy Gateway Message
// from params field of JSON-RPC request
func ValidatedMessageFromReq(req *jsonrpc.Request[json.RawMessage]) (*api.Message, error) {
	if req.Version != "2.0" {
		return nil, errors.New("incorrect jsonrpc version")
	}
	if req.Method == "" {
		return nil, errors.New("empty method field")
	}
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
	var m api.Message
	err := json.Unmarshal(*req.Params, &m)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal request params: %w", err)
	}
	m.Body.Method = req.Method
	m.Body.MessageID = req.ID
	err = m.Validate()
	if err != nil {
		return nil, err
	}
	return &m, nil
```

**File:** core/capabilities/webapi/trigger/trigger.go (L85-120)
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
```

**File:** core/capabilities/webapi/trigger/trigger.go (L167-184)
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
```

**File:** core/capabilities/webapi/webapicap/event_trigger-schema.json (L64-68)
```json
                "timestamp": {
                    "type": "integer",
                    "format": "int64",
                    "description": "Timestamp of the event (unix time), needs to be within certain freshness to be processed."
                },
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L193-234)
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
}
```
