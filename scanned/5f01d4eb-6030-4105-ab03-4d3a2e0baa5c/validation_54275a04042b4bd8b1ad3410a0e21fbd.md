### Title
Unsafe `int64`→`uint` cast in WebAPI Gateway staleness check allows message replay bypass - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The `WebAPIHandler.HandleLegacyUserMessage` staleness check performs an unsafe cast of a client-controlled signed timestamp field to `uint` before comparing it against the current time, mirroring the reported class of bug (unsafe/unchecked numeric casting used directly in a security-relevant computation without bounds validation).

### Finding Description
`HandleLegacyUserMessage` is the entry point that processes an unprivileged user's `web_api_trigger` request arriving at the internet-facing Gateway before it is forwarded to DON nodes: [1](#0-0) 

The staleness/anti-replay check is: [2](#0-1) 

specifically:
```go
if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115: comparing unix timestamps, both fit within uint
``` [3](#0-2) 

`payload.Timestamp` comes from `webapicap.TriggerRequestPayload`, populated by unmarshalling raw, attacker-controlled JSON supplied in the message body: [4](#0-3) 

The code explicitly suppresses a `gosec G115` "unsafe integer conversion" lint warning rather than validating the value. Because the field is deserialized from client JSON, an attacker can supply a negative timestamp value. Casting a negative signed integer to `uint` wraps around to a very large positive value (two's-complement reinterpretation), which will always be greater than `uint(time.Now().Unix()) - MaxAllowedMessageAgeSec`, causing the staleness comparison to always evaluate to `false` — i.e., the message is never rejected as stale, regardless of its actual age or how many times it has been replayed.

Immediately after this check, the code notes that no allowlist/rate-limiting is yet applied at this handler stage (`// TODO: apply allowlist and rate-limiting here`) and directly forwards the request to all DON nodes: [5](#0-4) 

This is directly analogous to the reported vulnerability class: an unchecked/unsafe numeric cast of externally-supplied data is used as-is in a security-critical decision (there, `uint256`→`uint128` truncation feeding a fund-movement operation; here, a signed timestamp→`uint` wraparound feeding a replay-protection gate) — data loss/wraparound from the cast defeats the intended safety check.

### Impact Explanation
An unprivileged remote client that can reach the Gateway's user-facing HTTP endpoint can forge a `web_api_trigger` message with a negative `timestamp` field to permanently disable/bypass the anti-replay staleness check for that message type. Combined with the absence of allowlist/rate-limiting at this stage (per the adjacent TODO), this enables replaying or resubmitting old signed trigger messages against DON nodes indefinitely, an unauthorized re-triggering of workflow execution (`SendToNode`) outside the intended freshness window.

### Likelihood Explanation
The `Timestamp` field is deserialized directly from client-supplied JSON with no explicit range/sign validation prior to the cast; supplying a negative number in the JSON payload is trivial for any external caller reaching the gateway's user endpoint, making exploitation straightforward if this path is reachable in current deployments (legacy `HandleLegacyUserMessage` path).

### Recommendation
Validate `payload.Timestamp` is non-negative (and within a sane bounds) before using it, and perform the staleness comparison using signed arithmetic (`int64`) rather than casting to `uint`:
```go
now := time.Now().Unix()
if payload.Timestamp <= 0 || now-payload.Timestamp > int64(h.config.MaxAllowedMessageAgeSec) {
    // reject as invalid/stale
}
```
Remove the `//nolint:gosec // G115` suppression once the underlying unsafe conversion is fixed rather than silenced.

### Proof of Concept
1. Attacker sends a `web_api_trigger` message to the Gateway's user-facing endpoint with `TriggerRequestPayload.Timestamp` set to a negative value, e.g. `-1`.
2. In `HandleLegacyUserMessage`, `uint(payload.Timestamp)` wraps to `18446744073709551615` (on 64-bit `uint`), which is always greater than `uint(time.Now().Unix()) - MaxAllowedMessageAgeSec`.
3. The staleness check at line 372 passes (message treated as fresh) regardless of the true age of the message, and the request proceeds to be forwarded to DON nodes via `don.SendToNode`, bypassing the intended replay-protection window.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-358)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-419)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
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
```
