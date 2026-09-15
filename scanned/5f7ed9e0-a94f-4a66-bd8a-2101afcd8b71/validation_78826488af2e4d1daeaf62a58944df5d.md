### Title
Missing upper-bound (future) timestamp validation in gateway WebAPI trigger message staleness check - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's `HandleLegacyUserMessage` handler validates the `Timestamp` field of an unprivileged, externally-submitted `web_api_trigger` message only against a "too old" bound, never against a "too far in the future" bound. This mirrors the reported StreamFactory analog: a caller-controlled timestamp is checked in one direction only, letting the caller pick a timestamp far outside the intended validity window to defeat the staleness/anti-replay purpose of the check.

### Finding Description
`HandleLegacyUserMessage` decodes an `api.Message` payload into a `webapicap.TriggerRequestPayload` and performs this staleness check: [1](#0-0) 

The only validations performed are:
1. `payload.Timestamp == 0` is rejected.
2. `uint(time.Now().Unix()) - h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp)` — i.e., the message is rejected only if it is *too old*.

There is no check that `payload.Timestamp` is not far in the future relative to `time.Now()`. Because `Timestamp` is an `int64` fully controlled by the external HTTP caller that submits the trigger message to the internet-facing gateway, an attacker can set it to an arbitrary large value (e.g., years in the future). Since the comparison `now - maxAge > timestamp` will be false for any timestamp greater than or equal to `now`, such a message always passes the staleness check regardless of how far in the future it claims to be — directly analogous to the reported issue where a caller sets `startTime`/`stopTime` arbitrarily far from `block.timestamp` with no upper-bound sanity check.

The message is subsequently forwarded to all DON members via `don.SendToNode`: [2](#0-1) 

Any downstream logic in node capability handlers that trusts `payload.Timestamp` as "fresh" (e.g., for dedup windows, ordering, or age-based cache eviction) can be manipulated by this out-of-range value, and there is no rejection path for it before the request reaches the DON.

### Impact Explanation
An unprivileged HTTP caller can submit `web_api_trigger` messages with a timestamp set arbitrarily far in the future and have it accepted as "not stale" by the gateway handler, bypassing the intent of the freshness/staleness check. This is a validation-bypass in the internet-facing gateway message envelope handling, matching the class of bug reported (timestamp far from current time to bypass intended time-window semantics). Actual severity is bounded by what downstream consumers do with `Timestamp` (e.g. potential confusion of trigger-event ordering/dedup, or indefinite "freshness" of a request), so this is a medium-severity input-validation gap rather than direct fund loss.

### Likelihood Explanation
High likelihood of reachability: this is a fully external, unauthenticated-by-the-check field (`Timestamp`) supplied in the JSON payload of a `web_api_trigger` message accepted by the gateway from any external submitter, requiring no privileged role — only the existing (separate) signature/allowlist checks on the message envelope itself, not on the timestamp value.

### Recommendation
Add a symmetric upper-bound check in `HandleLegacyUserMessage`, e.g. reject when `payload.Timestamp > time.Now().Unix() + <MaxAllowedClockSkewSec>`, mirroring the existing lower-bound (`MaxAllowedMessageAgeSec`) check, so timestamps cannot be set arbitrarily far in the future or trivially bypass the staleness window.

### Proof of Concept
1. Construct a `TriggerRequestPayload` with `Timestamp = time.Now().Unix() + 10*365*24*3600` (10 years in the future).
2. Sign/wrap it in an `api.Message` per `MethodWebAPITrigger` and submit it through the gateway's user-facing endpoint.
3. In `HandleLegacyUserMessage`, `payload.Timestamp != 0` passes, and `uint(time.Now().Unix()) - h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp)` evaluates false (since `payload.Timestamp` is far greater than `now`), so the "stale message" rejection branch at [3](#0-2)  is never taken.
4. The message is forwarded unmodified to DON members, demonstrating that no upper-bound timestamp validation exists.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-384)
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
	// TODO: apply allowlist and rate-limiting here
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L410-420)
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
