Confirmed: `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` only rejects messages that are too *old* — there is no check rejecting messages with a `Timestamp` in the *future*. This is the direct structural analog of the reported bug (an incomplete two-sided timestamp bound check, missing one side).

### Title
Missing upper-bound (future) timestamp check in gateway `HandleLegacyUserMessage` allows attacker-controlled `payload.Timestamp` to bypass staleness/replay protections - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`HandleLegacyUserMessage` validates a client-supplied `webapicap.TriggerRequestPayload.Timestamp` against a single lower-bound freshness check (`now - MaxAllowedMessageAgeSec > payload.Timestamp` ⇒ reject as "stale message"). There is no corresponding upper-bound check that the timestamp is not in the future relative to the gateway's clock. This is the same class of defect as the reported `ZkEvmV2._finalizeBlocks` bug: a two-sided bound is expected on a timestamp field, but only one side of the check is implemented.

### Finding Description
The handler code is: [1](#0-0) 

`payload.Timestamp` originates from the signed but attacker-controlled `TriggerRequestPayload` sent by an unprivileged client through the internet-facing gateway user endpoint (`HandleLegacyUserMessage`, invoked for web-api-trigger messages). The only validation performed is:
1. `payload.Timestamp != 0` (non-zero check)
2. `now - MaxAllowedMessageAgeSec > payload.Timestamp` → rejected as stale

There is no check of the form `payload.Timestamp > now` (or `now + tolerance`). As a result, a client can set an arbitrarily large future timestamp (e.g., `year 9999`) and the message will never be considered stale for the lifetime of the process, since the "stale" comparison will never trip for a future-dated value.

By contrast, other timestamp-bearing authentication paths in the same codebase — e.g. the gateway connector handshake (`core/services/gateway/network/handshake.go`) and node auth config (`AuthTimestampToleranceSec`, `core/services/gateway/connector/config.go`) — enforce both directions of a timestamp tolerance window. The `HandleLegacyUserMessage` path is missing the symmetric check.

### Impact Explanation
The `MaxAllowedMessageAgeSec` mechanism exists specifically to bound the message's validity window and mitigate replay of stored/cached triggers to DON nodes (`savedCallbacks` keyed by `msg.Body.MessageID`, with the request fanned out to all DON members via `don.SendToNode`). Because the upper bound is not enforced, a malicious/unprivileged client can craft `web_api_trigger` messages with a timestamp far in the future, defeating the intended purpose of the staleness check as a defense-in-depth control over message age/ordering. Downstream capability nodes and workflow trigger logic may implicitly trust that `Timestamp` reflects the current wall-clock; an unbounded future timestamp could distort trigger ordering, cause request/response correlation issues, or interact unexpectedly with downstream consumers that rely on this field for freshness/ordering assumptions.

### Likelihood Explanation
Likelihood is high for triggering the missing check itself: any client able to reach the gateway's user-facing endpoint and construct a valid signed `web_api_trigger` message (which is the intended, unprivileged entry point for this handler) can set `Timestamp` to any value without violating the existing check. The exploitability of downstream effects depends on how consuming capability nodes/workflows use the timestamp, which is outside this file, but the validation gap itself is unconditionally reachable at the boundary shown.

### Recommendation
Add a symmetric upper-bound check in `HandleLegacyUserMessage`, mirroring the existing lower-bound stale-message check, e.g.:
```go
if uint(payload.Timestamp) > uint(time.Now().Unix())+h.config.MaxAllowedMessageAgeSec {
    // reject as "message timestamp too far in the future"
}
```
placed alongside the existing check at [2](#0-1) .

### Proof of Concept
1. Construct a `TriggerRequestPayload` (as in `triggerRequest` test helper, `core/services/gateway/handlers/capabilities/handler_test.go:193-234`) with `Timestamp` set to, e.g., `time.Now().Unix() + 1e9` (far future).
2. Sign and submit via `HandleLegacyUserMessage`.
3. Observe that the existing check `uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp)` evaluates false (since `payload.Timestamp` is huge), so the "stale message" branch is skipped and the message is processed/forwarded normally — despite having a manifestly invalid (future) timestamp. [3](#0-2)

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-383)
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
```
