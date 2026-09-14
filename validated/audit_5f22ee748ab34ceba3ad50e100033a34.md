### Title
Missing Upper-Bound Timestamp Check in Gateway Legacy User Message Handler Enables Unbounded Replay of Signed Trigger Requests - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`HandleLegacyUserMessage` in the gateway's capabilities handler validates message freshness using only a one-sided (lower-bound) staleness check on `payload.Timestamp`. There is no upper-bound check to reject timestamps set in the future, so a request signed with a future timestamp can never be classified as "stale" and remains perpetually "fresh," enabling indefinite replay of an unprivileged user's HTTP trigger request.

### Finding Description
The handler decodes an unprivileged client's `webapicap.TriggerRequestPayload` and enforces freshness with: [1](#0-0) 

This check only rejects messages that are *too old* (`now - MaxAllowedMessageAgeSec > payload.Timestamp`). It never validates that `payload.Timestamp <= now` (or within some small future tolerance). Since the payload (including `Timestamp`) is fully controlled and signed by the requesting client itself, a client can set `Timestamp` to a large future value, causing the staleness check to never trigger — the message is treated as fresh forever.

Once past this check, the handler stores a callback keyed by `msg.Body.MessageID` and fans the request out to all DON members: [2](#0-1) 

There is no replay-detection/dedup mechanism analogous to `RequestReplayGuard` used elsewhere in the codebase (e.g., the vault handlers) — `savedCallbacks` is only used to pair a later node response back to the caller and is pruned purely by wall-clock age via `pruneCallbacks`/`CallbackMaxAgeSec`, not by the message's own claimed timestamp: [3](#0-2) 

The code even has an explicit TODO acknowledging that allowlist and rate-limiting enforcement is not yet applied on this path: [4](#0-3) 

By contrast, comparable Chainlink internet-facing flows (vault, confidential relay, JWT-based auth) explicitly implement bidirectional expiry and replay protection, e.g. `RequestReplayGuard.CheckAndRecord`: [5](#0-4) 
and JWT `exp`/`iat` bounding with a max-lifetime check: [6](#0-5) 
This shows the pattern is known and applied elsewhere but is missing on the `HandleLegacyUserMessage` path.

### Impact Explanation
An unprivileged client that has legitimately authored and signed one valid `web_api_trigger` message can capture and indefinitely replay that exact same signed message against the gateway. Each replay causes the gateway to re-forward the (identical) trigger request to every DON member node: [7](#0-6) 

This results in repeated, unauthorized re-triggering of the associated workflow beyond the single intended invocation the client's signed request was meant to authorize — an unbounded replay / duplicate job-execution issue, directly analogous to the reported "lack of effective deadline check" leading to unexpected execution of stale/pending transactions.

### Likelihood Explanation
Likelihood is moderate-to-high for any client capable of reaching this internet-facing gateway endpoint with a `web_api_trigger` message: the attacker only needs to sign one payload with a future `Timestamp` value (fully under their control since they construct and sign it) and can then resend that identical message any number of times without ever failing the freshness check. No special privilege beyond normal API access is required.

### Recommendation
Add a symmetric upper-bound check rejecting payloads whose `Timestamp` is in the future beyond a small clock-skew tolerance, e.g.:
```go
now := time.Now().Unix()
if uint(payload.Timestamp) > uint(now)+clockSkewToleranceSec {
    // reject: timestamp too far in the future
}
```
Additionally, introduce replay protection for `MessageID`/digest similar to `RequestReplayGuard` used in the vault handlers, so that a previously-processed message (or one already forwarded to nodes) cannot be reprocessed even within the allowed freshness window.

### Proof of Concept
1. Client builds a `webapicap.TriggerRequestPayload` with `Timestamp` set to `time.Now().Unix() + 10_000_000` (far future) and signs the enclosing `api.Message`.
2. Client sends this message to the gateway's `HandleLegacyUserMessage` entry point repeatedly (e.g., every second, or every hour).
3. On every call, `uint(time.Now().Unix()) - h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp)` evaluates to `false` because `payload.Timestamp` is always greater than `now`, so the "stale message" branch never triggers: [1](#0-0) 
4. Each call passes validation and reaches `don.SendToNode` for every DON member, re-triggering the workflow with no bound on how many times this can be repeated.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-312)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}
```

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-384)
```go
	// TODO: apply allowlist and rate-limiting here
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-420)
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

**File:** core/capabilities/vault/request_replay_guard.go (L35-47)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}
```

**File:** core/utils/jwt.go (L290-298)
```go
	now := time.Now()
	issuedAt := verifiedClaims.IssuedAt
	if issuedAt.After(now.Add(issuedAtTolerance)) {
		return nil, gethcommon.Address{}, fmt.Errorf("issuedAt (iat) is too far in the future (beyond tolerance of %.0f seconds)", issuedAtTolerance.Seconds())
	}
	duration := verifiedClaims.ExpiresAt.Sub(verifiedClaims.IssuedAt.Time)
	if duration > maxExpiryDuration {
		return nil, gethcommon.Address{}, fmt.Errorf("token lifetime %.0f sec exceeds the maximum allowed %.0f sec. Reduce the gap between 'iat' and 'exp'", duration.Seconds(), maxExpiryDuration.Seconds())
	}
```
