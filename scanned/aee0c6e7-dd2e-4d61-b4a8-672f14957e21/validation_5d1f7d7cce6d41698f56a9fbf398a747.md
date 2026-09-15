## Title
Legacy WebAPI trigger message staleness check only rejects timestamps that are too old, allowing arbitrary future timestamps to bypass the intended freshness window - ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
`handler.HandleLegacyUserMessage` validates an unprivileged, external-initiator-supplied `payload.Timestamp` field against a "max allowed message age" using a one-sided comparison, mirroring the reported bug class: a time/slot-like value supplied by an untrusted caller is checked in only one direction (not too far in the past / not too far in the future), letting the caller pick a value on the unchecked side to skip the intended progression/aging logic entirely.

## Finding Description
`HandleLegacyUserMessage` decodes a caller-supplied JSON payload (`webapicap.TriggerRequestPayload`) that includes a `Timestamp` field, and checks staleness with: [1](#0-0) 

```go
if payload.Timestamp == 0 { ... reject ... }
...
if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) {
    // "stale message" rejected
}
```

This is analogous to the `start_slot` bug: the validation is one-directional. It only rejects a timestamp that is *too old* (`now - MaxAllowedMessageAgeSec > timestamp`). It never rejects a timestamp that is arbitrarily far in the *future*. A caller reaching this handler through the gateway's legacy user-message path (this is the internet-facing gateway ingress for `HandleLegacyUserMessage`, invoked for unauthenticated/legacy webhook-style requests) fully controls `payload.Timestamp` in the JSON body, and can set it to any large value (e.g., far in the future) to guarantee the staleness check always passes, regardless of how the message is subsequently processed, queued, or aged out by other logic in the pipeline (e.g., callback pruning by `createdAt`, which uses server-side time, not the attacker-controlled `payload.Timestamp` — but any other downstream logic that treats `payload.Timestamp` as a trusted freshness signal would be bypassable this way).

This mirrors the report's root cause exactly: a single-sided bound (`start_slot <= clock.slot`) that was supposed to keep a caller-supplied "start" reference near the current time, but instead only prevents it from being in the future, letting the value drift arbitrarily in the disallowed direction (there: past; here: future).

## Impact Explanation
Where `payload.Timestamp` is used purely for a staleness gate, an attacker can force `HandleLegacyUserMessage` to always treat a message as fresh by setting the timestamp far in the future, defeating the freshness/anti-replay-staleness intent of the check. Impact is bounded by what depends on this specific field being correctly bounded — it does not itself grant authentication bypass or fund movement, so its practical impact here is a broken invariant (freshness guarantee) rather than direct compromise. This is why it is rated Medium, consistent with the source report's Medium severity for an analogous one-sided range check that breaks an intended monotonic progression rather than granting unauthorized access outright.

## Likelihood Explanation
Likelihood is Medium: any unprivileged caller able to reach the gateway's `HandleLegacyUserMessage` path with a webhook-style trigger request can trivially set an arbitrary `Timestamp` value in the JSON payload; no special access or timing is required.

## Recommendation
Validate `payload.Timestamp` on both sides of "now" using the same tolerance windows applied elsewhere in this codebase for auth timestamps (see `network.ErrAuthInvalidTimestamp` bounds and `AuthTimestampToleranceSec` pattern used in `core/services/gateway/connector/connector.go` and `core/services/gateway/network/handshake.go`, which check `ts < now-tolerance || now+tolerance < ts`). Apply an equivalent two-sided check to `payload.Timestamp` in `HandleLegacyUserMessage` instead of only rejecting timestamps below the lower bound.

## Proof of Concept
1. Send a legacy webhook trigger message to the gateway with `payload.Timestamp` set to, e.g., `time.Now().Unix() + 10_000_000` (far future).
2. `uint(time.Now().Unix()) - h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp)` evaluates to `false` regardless of how stale the message actually becomes by the time it is processed, since the right-hand side is inflated arbitrarily.
3. The message passes the staleness check unconditionally, confirming the one-sided validation gap analogous to the reported `start_slot <= clock.slot` bug. [1](#0-0) 

**Caveat/uncertainty:** I could not fully trace every downstream consumer of `payload.Timestamp` beyond the staleness check within the index's available context (the `webapicap.TriggerRequestPayload` struct and `trigger.go` consumers were only partially inspected), so I cannot confirm additional concrete impact (e.g., fund movement or cross-user confusion) beyond the freshness-check bypass itself. If a full trace is needed, a Devin session with full repo access should follow `payload.Timestamp` through `webapicap` and `capabilities/webapi/trigger/trigger.go` to check for any other assumptions on timestamp boundedness.

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
