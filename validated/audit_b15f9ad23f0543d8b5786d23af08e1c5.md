### Title
Unsafe int64→uint Cast Allows Bypass of Stale-Message / Replay-Window Check in Gateway WebAPI Trigger Handler - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`HandleLegacyUserMessage` in the gateway's capabilities handler validates the freshness of a user-supplied `web_api_trigger` message by comparing an unsigned-cast `Timestamp` field against the current time. The comparison casts an attacker-controlled `int64` (`payload.Timestamp`) directly to `uint` without validating that the value is non-negative, mirroring the class of unsafe-cast bug described in the report (raw type coercion on unsanitized numeric input silently producing a wrong, security-relevant result).

### Finding Description
The freshness/anti-replay check is: [1](#0-0) 

Specifically:
```go
if payload.Timestamp == 0 { ... reject ... }

if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115
    // "stale message" — reject
}
```
`payload.Timestamp` is defined as `int64` and is fully attacker-controlled JSON input [2](#0-1) . The only guard applied before the cast is `Timestamp == 0` [3](#0-2) ; negative values are never rejected.

In Go, converting a negative `int64` to `uint` performs a two's-complement reinterpretation, producing a value close to `math.MaxUint64` (on 64-bit platforms). Consequently, if `payload.Timestamp` is negative, `uint(payload.Timestamp)` evaluates to an enormous number, making `uint(now) - maxAge > uint(payload.Timestamp)` false for essentially any current time — the "stale message" branch can never trigger for such a payload, regardless of how old (or how far in the future) the intended timestamp actually is. This nullifies the freshness/replay-window check that is meant to bound how long a signed trigger message can be reused.

This directly mirrors the reported bug class: an unvalidated numeric field crosses a narrower/differently-signed integer boundary via a raw cast (`uint96()` in the Solidity report vs. `int64`→`uint` here), and the resulting silent truncation/wraparound defeats a security-relevant comparison (debited-amount check in the report; stale-message/anti-replay check here) rather than raising an error.

The signature scheme covers `Payload` as raw bytes [4](#0-3) , so a legitimate signer of a `web_api_trigger` message can freely choose `Timestamp` (including negative values) before signing, and the check can never flag that message as stale thereafter, effectively creating an unlimited replay window for that self-crafted message. Note also that this legacy code path explicitly has no allowlist/rate-limit enforcement yet ("TODO: apply allowlist and rate-limiting here" [5](#0-4) ), which increases the practical exposure of any bypassed freshness control on this path, though that missing-control issue is a separate gap from the unsafe cast itself.

### Impact Explanation
The freshness check exists to bound the reuse window of a signed `web_api_trigger` gateway message forwarded to all DON members. A crafted negative timestamp defeats that bound entirely, letting a message be classified as "fresh" indefinitely. Combined with the DON's own trigger-side handling (topic/sender allowlist enforcement occurs later in a different code path, not in this legacy handler), this weakens a defense-in-depth control against message replay/reuse at the internet-facing gateway ingress. Impact is bounded by whatever additional freshness/uniqueness enforcement (e.g. per-trigger-event-id dedup) exists further down the pipeline, which was not verified in this pass.

### Likelihood Explanation
Exploiting this requires nothing more than an actor able to submit a `web_api_trigger` JSON-RPC/legacy message to the gateway with a self-chosen `Timestamp` value in the payload (e.g., `-1`), then signing it with any key. Given `Timestamp` is a plain JSON integer field with only an `== 0` guard, crafting a negative value is trivial for any client capable of reaching this endpoint.

### Recommendation
Reject non-positive (`<= 0`) timestamps explicitly, or use a signed-safe comparison entirely in `int64`/`time.Time` space instead of casting to `uint`:
```go
now := time.Now().Unix()
if payload.Timestamp <= 0 || now-int64(h.config.MaxAllowedMessageAgeSec) > payload.Timestamp {
    // stale/invalid
}
```
Avoid `//nolint:gosec` suppressions on conversions from attacker-controlled signed fields to unsigned types without an explicit range check beforehand, consistent with the reported recommendation to use safe/guarded casts instead of raw type coercions.

### Proof of Concept
1. Construct a `TriggerRequestPayload` with `Timestamp: -1` (any negative int64), valid `trigger_id`, `topics`, and `params`.
2. Sign the resulting `api.Message` with any ECDSA private key via `Message.Sign` (signature covers `Payload` bytes, so any timestamp value is signable).
3. Submit via `HandleLegacyUserMessage` (or the corresponding legacy HTTP endpoint that routes into it).
4. Observe: `payload.Timestamp == 0` check passes (value is `-1`, not `0`); `uint(payload.Timestamp)` wraps to `~2^64-1`; the staleness comparison `uint(now)-maxAge > uint(payload.Timestamp)` is false, so the message is treated as fresh and forwarded to all DON members, regardless of the true age/validity intended by the freshness control.

Note: I was unable to fully trace whether downstream DON-side or trigger-registration logic independently rejects negative/implausible timestamps or enforces its own replay protection (e.g., via `trigger_event_id` uniqueness) — that would need to be confirmed to bound the real-world exploitability of this specific bypass.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-384)
```go
	// TODO: apply allowlist and rate-limiting here
```

**File:** core/capabilities/webapi/webapicap/event_trigger_generated.go (L101-117)
```go
type TriggerRequestPayload struct {
	// Key-value pairs for the workflow engine, untranslated.
	Params TriggerRequestPayloadParams `json:"params" yaml:"params" mapstructure:"params"`

	// Timestamp of the event (unix time), needs to be within certain freshness to be
	// processed.
	Timestamp int64 `json:"timestamp" yaml:"timestamp" mapstructure:"timestamp"`

	// Topics corresponds to the JSON schema field "topics".
	Topics []string `json:"topics" yaml:"topics" mapstructure:"topics"`

	// Uniquely identifies generated event (scoped to trigger_id and sender).
	TriggerEventId string `json:"trigger_event_id" yaml:"trigger_event_id" mapstructure:"trigger_event_id"`

	// ID of the trigger corresponding to the capability ID.
	TriggerId string `json:"trigger_id" yaml:"trigger_id" mapstructure:"trigger_id"`
}
```

**File:** core/services/gateway/api/message.go (L90-108)
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
}
```
