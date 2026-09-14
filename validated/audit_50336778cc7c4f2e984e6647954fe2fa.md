Confirmed: `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` only enforces a lower bound on the client-supplied `payload.Timestamp` (rejecting messages that are too old), but never validates an upper bound (rejecting timestamps set arbitrarily far in the future). This is the direct structural analog of the reported bug class: an unvalidated, unprivileged-client-controlled time parameter that is later relied upon for freshness/staleness decisions.

### Title
Missing upper-bound validation on client-supplied `Timestamp` in Gateway WebAPI trigger message allows indefinite staleness-check bypass - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`HandleLegacyUserMessage` accepts a `webapicap.TriggerRequestPayload` from an unprivileged external node/message sender and validates its `Timestamp` field only against a lower bound (`MaxAllowedMessageAgeSec`), never against the current time as an upper bound. [1](#0-0)  This mirrors the reported bug class: a client/deployer-controlled time-like parameter is trusted without a sanity check against "now," letting a value far outside the intended range slip past a freshness gate meant to bound its validity window.

### Finding Description
The JSON schema for the trigger payload documents that `timestamp` "needs to be within certain freshness to be processed" [2](#0-1) , implying a bounded window (both past and future). The actual enforcement in the handler is:

```go
if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) {
    // "stale message" rejected
}
``` [3](#0-2) 

This only rejects timestamps that are too old. A caller can set `Timestamp` to any arbitrarily large future value (e.g., years in the future) and the check `now - maxAge > timestamp` will never be true, so the message is treated as "fresh" indefinitely. The only other validation on `Timestamp` is that it must be non-zero. [4](#0-3) 

Once past this check, the message is forwarded unchanged to all DON members via `common.ValidatedRequestFromMessage` and `don.SendToNode`, with the callback for the original caller saved keyed by `MessageID`. [5](#0-4)  The `Timestamp` value itself is opaque payload data forwarded to capability nodes/workflows, so any freshness assumptions made downstream by nodes or workflow logic that trust this field (as the schema comment implies) are undermined by the gateway's incomplete validation.

### Impact Explanation
This is a Medium-severity input-validation gap rather than a direct fund-loss or authentication bypass: the message is still signature-validated (`msg.Validate()`/`ExtractSigner`), so this is not an unauthenticated request forgery. However, it defeats the intended purpose of the freshness check entirely for the "too far in the future" direction, which is a partial control bypass of a security-relevant validation (staleness/freshness gating), directly analogous to the reported vesting-escrow issue where a missing bound on a time parameter caused downstream logic (which assumes the value is sane) to behave incorrectly. Depending on how downstream capability/workflow logic interprets `Timestamp` (e.g., ordering, deduplication, or "needs to be within certain freshness" per the schema's own documentation), this could enable stale/replay-like processing or bypass freshness-dependent logic that other components rely on.

### Likelihood Explanation
Likelihood is high for triggering the code path itself: any unprivileged external initiator/webhook client that can sign and submit a `web_api_trigger` message controls the `Timestamp` field freely, and the only server-side check is the one-sided staleness comparison shown above. No special privileges, node compromise, or network-layer access are required — just a validly-signed message through the existing public message-signing flow.

### Recommendation
Add an upper-bound check alongside the existing lower-bound check in `HandleLegacyUserMessage`, e.g.:
```go
now := uint(time.Now().Unix())
if now - h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) ||
   uint(payload.Timestamp) > now + h.config.MaxAllowedMessageAgeSec {
    // reject as stale/out-of-window
}
```
This ensures `Timestamp` values are bounded on both sides of "now," matching the schema's documented freshness intent. [2](#0-1) 

### Proof of Concept
1. Construct a `webapicap.TriggerRequestPayload` with `Timestamp` set to, e.g., `time.Now().Unix() + 10_000_000` (far future) and valid `TriggerId`, `TriggerEventId`, `Topics`, `Params`.
2. Sign the enclosing `api.Message` with any valid node key (per `msg.Sign(key)` as used in tests) [6](#0-5) .
3. Submit it through `HandleLegacyUserMessage`.
4. Observe the staleness check `uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp)` evaluates to `false` regardless of how far in the future `Timestamp` is, so the message passes and is forwarded to all DON members. [3](#0-2)

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L397-420)
```go
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
