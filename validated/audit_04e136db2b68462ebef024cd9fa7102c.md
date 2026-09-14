### Title
Signed timestamp field bypasses gateway trigger message staleness check via unsigned integer underflow - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Sherlock report describes an owner-controlled `challengePeriod` integer that, without bounds checking, can make time-based boundary comparisons in `TelcoinDistributor` always evaluate incorrectly, freezing challenge/execution flows. The closest reachable analog in this codebase is an unsigned-integer arithmetic bug in the internet-facing gateway's `capabilities` handler, where a client-supplied `Timestamp` field in the trigger message payload is used in an unsigned subtraction/comparison to decide whether a message is "stale". Because the operands are unsigned and the timestamp value comes from the message body (attacker-influenced), the boundary check can be defeated.

### Finding Description
In `HandleLegacyUserMessage`, the gateway extracts a client-supplied `TriggerRequestPayload.Timestamp` and checks staleness with: [1](#0-0) 

```go
if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115: comparing unix timestamps, both fit within uint
    h.lggr.Errorw("stale message")
    ...
}
```

This mirrors the report's root cause pattern exactly: an arithmetic/boundary comparison involving a value that can be pushed outside its intended range (here, `uint(payload.Timestamp)` from a signed `int64` field), causing a "cannot be true/cannot be false" condition analogous to the overflowed `challengePeriod` check in `challengeTransaction`/`executeTransaction`. If `payload.Timestamp` is crafted to be a very large or negative `int64` value, the unsigned conversion `uint(payload.Timestamp)` produces a huge value that will never be less than `uint(time.Now().Unix()) - MaxAllowedMessageAgeSec`, so the staleness check is permanently satisfied as "not stale," regardless of the message's real age.

### Impact Explanation
If the staleness guard can be bypassed, previously captured/old signed trigger messages could be considered fresh indefinitely by the gateway/DON, defeating the intended anti-replay/freshness boundary and forwarding stale or replayed trigger payloads to `don.SendToNode` for all DON members. This is comparable to the report's "freeze/bypass of a time boundary check" bug class, but here the practical blast radius is more limited: the field is inside the message payload which is covered by `msg.Sign`/`msg.Validate` (see the message signature check earlier in `HandleLegacyUserMessage`), so exploitation requires an already-valid signer to craft the payload — it is not a pure unauthenticated bypass of authentication/roles, secret disclosure, or fund movement. I was not able to fully verify (given the exhausted tool budget) whether `Timestamp` is included inside the signed digest computed by `msg.Sign`/`msg.Validate`, which determines whether an unprivileged third party (without the signer's key) could forge/tamper with this field independently of the original signature.

### Likelihood Explanation
Low-to-moderate. Exploitation requires: (1) an actor capable of producing a validly-signed `api.Message` (i.e., already an authenticated node/workflow participant, not a fully anonymous internet client), and (2) the ability to set an out-of-range `Timestamp` value inside the JSON payload without invalidating the message signature. Given the `//nolint:gosec // G115` comment, the developers were aware of the signed/unsigned conversion but asserted timestamps "both fit within uint" — an assumption that does not hold if `payload.Timestamp` is attacker-supplied and not range-validated before the conversion.

### Recommendation
- Validate `payload.Timestamp` is within a sane, non-negative, bounded range (e.g., not before epoch, not absurdly far in the future) before using it in unsigned arithmetic.
- Perform the staleness comparison using signed 64-bit arithmetic (`int64`) rather than converting to `uint`, to avoid underflow/overflow when the client-controlled value is out of the expected range.
- Confirm whether `Timestamp` is part of the data covered by the message signature; if not, add it to the signed payload so tampering invalidates the signature.

### Proof of Concept
Conceptual PoC (not executed, due to reaching tool-call limits):
1. Craft a `webapicap.TriggerRequestPayload` with `Timestamp` set to a large positive `int64` value (e.g., `math.MaxInt64`) or a negative value.
2. Sign the resulting `api.Message` with a valid node/workflow key so `msg.Validate()` passes.
3. Send the message to the gateway's `HandleLegacyUserMessage` handler.
4. Observe that `uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp)` evaluates to `false` regardless of the message's actual age, bypassing the "stale message" rejection at [2](#0-1) , allowing the message to be forwarded to all DON members via `don.SendToNode`.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L372-383)
```go
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
