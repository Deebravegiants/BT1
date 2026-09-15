### Title
Missing upper-bound timestamp validation in gateway web-api-trigger staleness check allows permanent bypass of message freshness/replay protection - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`HandleLegacyUserMessage` in the internet-facing gateway's `web-api-capabilities` handler validates a client-supplied `payload.Timestamp` only against a lower bound (message not too old), but never checks that the timestamp is not unreasonably far in the future. This mirrors the reported oracle bug class: a timestamp field is validated in only one direction, allowing it to be pushed to an extreme value that defeats the intended freshness/anti-replay protection indefinitely.

### Finding Description
The gateway's `HandleLegacyUserMessage` handler decodes a client-supplied `TriggerRequestPayload` (containing a caller-controlled `Timestamp` field) from an unprivileged HTTP-facing trigger request, and performs a one-sided staleness check: [1](#0-0) 

Specifically:
```go
if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) {
    // ... "stale message" rejection
}
```
This only rejects timestamps that are *too old*. There is no corresponding check that `payload.Timestamp` is not *too far in the future* (e.g. `payload.Timestamp > time.Now().Unix() + tolerance`). The schema for `TriggerRequestPayload` documents the intent that the timestamp "needs to be within certain freshness to be processed" [2](#0-1) , but the implementation only enforces half of that freshness window.

Because the timestamp is part of the caller-signed message payload, an authorized sender (present in `allowedSenders`) can craft and sign a message with an artificially inflated `Timestamp` value. Such a message will pass the staleness check unconditionally (for as long as the freshness clock runs, since `now - maxAge` will never exceed an inflated future timestamp), effectively defeating the freshness protection the check is meant to provide. If the signed message is later captured (e.g., via logging, an insecure transport hop, or an unauthorized replay of stored data), it can be resubmitted to the gateway and will always be treated as fresh, regardless of how long ago it was actually issued — permanently bypassing the intended anti-replay/staleness safeguard, analogous to how an unbounded `putPrice` timestamp permanently breaks staleness checks in the referenced report.

Additionally, `h.savedCallbacks` is keyed only by the client-supplied `msg.Body.MessageID` and unconditionally overwritten on each accepted message: [3](#0-2) . A message that is always treated as "fresh" due to the missing upper bound increases the practical window during which a colliding/replayed `MessageID` can overwrite another in-flight caller's saved callback, allowing a subsequent node response for that ID to be routed to the attacker's callback instead of the original caller's.

### Impact Explanation
The primary impact is defeat of the staleness/freshness control on `web-api-trigger` messages processed by the internet-facing gateway. This can enable:
- Indefinite replay of a previously valid, signed trigger message, causing repeated/unauthorized workflow execution triggers long after the message should have expired.
- An increased opportunity for `MessageID` collision to divert a node's response to an attacker-controlled callback (cross-user response confusion), since accepted (never-stale) messages continue to overwrite the `savedCallbacks` map indefinitely.

This does not directly move funds but can cause unauthorized/duplicate job/workflow runs and response misdelivery on the gateway's user-facing message path, which are within the accepted impact categories.

### Likelihood Explanation
Exploitation requires the ability to submit a request via the gateway's public trigger endpoint and either be an `allowedSenders`-listed identity willing to self-issue a permanently "fresh" message, or otherwise obtain/replay a previously valid signed message. Because signature validation covers the payload (including the timestamp) but the freshness check design flaw is purely a missing upper bound, the likelihood is moderate — it doesn't require breaking cryptography, only crafting/replaying a message with an inflated timestamp field.

### Recommendation
Add a symmetric upper-bound check in `HandleLegacyUserMessage` (and any successor v2 handlers using the same staleness pattern):
```go
now := time.Now().Unix()
maxAge := int64(h.config.MaxAllowedMessageAgeSec)
if payload.Timestamp < now-maxAge || payload.Timestamp > now+maxAge {
    // reject as stale/invalid
}
```
Additionally, consider binding `MessageID` uniqueness/idempotency to a nonce-or-digest scheme independent of caller-supplied timestamp, and reject overwriting an active `savedCallbacks` entry for a `MessageID` that has not yet been completed/expired, to close the response-confusion vector.

### Proof of Concept
1. As an authorized sender (in `allowedSenders`), construct a `TriggerRequestPayload` with `Timestamp` set to a value far in the future (e.g., `time.Now().Unix() + 10_000_000`).
2. Sign and submit the message via the gateway's public trigger endpoint (same flow as `triggerRequest` test helper) [4](#0-3) .
3. The `HandleLegacyUserMessage` staleness check `uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp)` evaluates false regardless of how much time has passed, since the future timestamp is always greater than `now - maxAge` [5](#0-4) .
4. Store/replay the signed message at any later time; it will continue to be accepted as "fresh" and forwarded to DON nodes, triggering the workflow again.

Note: I was unable to fully verify within index limits whether a v2 handler path (e.g. `http_trigger_handler.go`) applies the same or a corrected staleness check, since its full timestamp-validation logic was not retrieved. If a full audit of that alternate path is needed, a Devin session with full repository access should confirm whether it shares this same one-sided check.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/capabilities/webapi/webapicap/event_trigger-schema.json (L64-68)
```json
                "timestamp": {
                    "type": "integer",
                    "format": "int64",
                    "description": "Timestamp of the event (unix time), needs to be within certain freshness to be processed."
                },
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
