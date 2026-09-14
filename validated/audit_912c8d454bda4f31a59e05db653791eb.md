### Title
Signed unix timestamp field is converted to `uint` without bounds checking, allowing bypass of the gateway's stale-message check - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The Chainlink Gateway's `HandleLegacyUserMessage` handler validates that an incoming `web_api_trigger` message is not stale by comparing the current time against an attacker-supplied `TriggerRequestPayload.Timestamp` field. The comparison mixes signed and unsigned integer types without validating that the timestamp is a sane, non-negative, bounded value, mirroring the externally-reported Chainlink oracle bug class of "unchecked oracle response timestamp and integer over/underflow" (unvalidated timestamp values feeding downstream comparisons that can wrap/underflow).

### Finding Description
`HandleLegacyUserMessage` parses the JSON body into `webapicap.TriggerRequestPayload`, whose `Timestamp` field is a signed `int64` fully controlled by the calling client (any unprivileged user submitting a web API trigger message to the gateway). The freshness check is: [1](#0-0) 

```go
if payload.Timestamp == 0 { ... return error }
if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115
    ... return "stale message" error
}
```

`payload.Timestamp` is only checked for being exactly `0`; there is no check that it is positive, within a reasonable range of "now," or not absurdly large/small. Because the comparison converts the signed `int64` timestamp directly to `uint` (`uint(payload.Timestamp)`), any negative value supplied by the client wraps to a very large unsigned integer (near `2^64`). In that case `uint(time.Now().Unix()) - h.config.MaxAllowedMessageAgeSec` (a comparatively small number) will never be greater than the wrapped value, so the "stale message" branch is never taken — the staleness check is unconditionally bypassed for any negative timestamp. This is the same root-cause pattern flagged in the external report: an externally supplied/oracle-style timestamp is not validated for sane bounds before being used in unchecked arithmetic, defeating the intended timeliness/replay guard.

The `HandlerConfig.MaxAllowedMessageAgeSec` and this staleness gate are the primary defense against replay of old, previously valid signed `web_api_trigger` messages reaching the gateway's internet-facing message-envelope handler: [2](#0-1) 

The rest of the pipeline (`common.ValidatedRequestFromMessage`, DON dispatch) does not re-derive or re-validate the timestamp bound independently: [3](#0-2) 

### Impact Explanation
An unprivileged client that can reach the gateway's public/internet-facing endpoint for `web_api_trigger` messages can craft a message with a negative `Timestamp` value. This bypasses the "stale message" rejection entirely, allowing the message to be forwarded to all DON members regardless of its actual age. If message age/staleness is relied upon elsewhere (e.g., to bound replay windows for signed messages, since the JSON-RPC/message signature covers the payload including the timestamp but not the current wall-clock time), this weakens the freshness guarantee the gateway is supposed to enforce for this handler, allowing acceptance of messages that should have been rejected as too old (or with nonsensical timestamps), which can affect downstream trigger/consensus processing on the DON side.

### Likelihood Explanation
The `Timestamp` field is fully attacker-controlled JSON input, and the check is a single unguarded arithmetic comparison — no additional validation is required to trigger the bypass. Any client capable of sending a `web_api_trigger` message to the gateway (an intentionally externally-reachable capability) can supply a negative timestamp with no other precondition, making this trivially reachable from an unprivileged sender.

### Recommendation
- Validate `payload.Timestamp` is non-negative and within a sane bounded range (not too far in the future, not absurdly old) before using it, rather than only checking `== 0`.
- Perform the staleness comparison entirely in signed 64-bit arithmetic (`int64`), avoiding the `uint` conversions that allow underflow/wraparound, e.g. compute `age := time.Now().Unix() - payload.Timestamp` and reject if `age < 0` or `age > int64(h.config.MaxAllowedMessageAgeSec)`.
- Remove the `//nolint:gosec // G115` suppression once the conversion is fixed safely, since it currently masks the exact class of bug being suppressed.

### Proof of Concept
1. An unprivileged client crafts a `web_api_trigger` message with `webapicap.TriggerRequestPayload{Timestamp: -1, ...}` (or any negative value), signs it as required by `msg.Sign`/`msg.Validate`, and sends it to the gateway.
2. In `HandleLegacyUserMessage`, `payload.Timestamp == 0` is false (it's `-1`), so execution proceeds to the staleness check.
3. `uint(payload.Timestamp)` evaluates to `18446744073709551615` (max `uint64`) due to the negative-to-unsigned conversion.
4. `uint(time.Now().Unix()) - h.config.MaxAllowedMessageAgeSec` is a small positive number (current unix time minus configured max age), which is never greater than `18446744073709551615`.
5. The "stale message" branch at [4](#0-3)  is skipped, and the message — despite having an invalid/attacker-chosen timestamp — is forwarded to all DON members via `don.SendToNode`.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L63-70)
```go
type HandlerConfig struct {
	NodeRateLimiter         ratelimit.RateLimiterConfig `json:"nodeRateLimiter"`
	MaxAllowedMessageAgeSec uint                        `json:"maxAllowedMessageAgeSec"`

	CallbackMaxAgeSec        int `json:"callbackMaxAgeSec"`
	MaxSavedCallbacks        int `json:"maxSavedCallbacks"`
	CallbackPruneIntervalSec int `json:"callbackPruneIntervalSec"`
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
