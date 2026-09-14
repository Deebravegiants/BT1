Confirmed root cause: unlike `CallbackMaxAgeSec`, `MaxSavedCallbacks`, and `CallbackPruneIntervalSec`, the `MaxAllowedMessageAgeSec` field in `HandlerConfig` (`core/services/gateway/handlers/capabilities/handler.go:65`) has **no default-value fallback** applied in `NewHandler` (lines 86-94 only backfill the other three fields). This is the direct code-level analog to the external report's "maxDelayTime not initialized" bug class.

### Title
Unbounded Stale Message Acceptance in `HandleLegacyUserMessage` Due to Unset `MaxAllowedMessageAgeSec` - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The gateway's legacy WebAPI trigger message handler validates message freshness using `h.config.MaxAllowedMessageAgeSec`, but this field is never defaulted like its sibling config fields, so it defaults to Go's zero value (`0`) whenever the operator's handler config omits it.

### Finding Description
`HandleLegacyUserMessage` performs a staleness check on unprivileged, internet-facing trigger messages: [1](#0-0) 

```go
if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) {
    // reject as stale
}
```

`MaxAllowedMessageAgeSec` is declared as a plain `uint` with no explicit initialization guarantee: [2](#0-1) 

In `NewHandler`, only three sibling fields (`CallbackMaxAgeSec`, `MaxSavedCallbacks`, `CallbackPruneIntervalSec`) are defaulted when zero; `MaxAllowedMessageAgeSec` is conspicuously omitted from this defaulting block: [3](#0-2) 

If the handler is deployed with `MaxAllowedMessageAgeSec` unset/zero (the exact same failure mode as the reported oracle `maxDelayTime`), the comparison degrades to `now() > payload.Timestamp`, which is true for essentially any timestamp in the past — meaning the "staleness" check no longer bounds message age at all. Any externally-supplied `payload.Timestamp` from an unprivileged client that is merely less than the current time passes the check, regardless of how old it is.

### Impact Explanation
This handler processes unauthenticated/unprivileged, internet-facing trigger messages forwarded to DON nodes. With the staleness guard silently disabled, an external actor can replay or resubmit an arbitrarily old, previously captured signed `web_api_trigger` message and have it accepted and forwarded to all DON members as if fresh, defeating the intended anti-replay/freshness protection — directly mirroring the reported oracle bug class (a security-critical staleness bound silently becoming a no-op due to a zero default).

### Likelihood Explanation
Likelihood depends on operator configuration: only deployments that omit `maxAllowedMessageAgeSec` from the JSON handler config are affected, since Go zero-values integer fields by default and this specific field has no code-level fallback (unlike its siblings which do). Because the surrounding code pattern explicitly defaults similar fields but skips this one, this looks like an unintentional omission rather than a deliberate "0 = disabled" design, increasing the chance of an operator unknowingly deploying with this check effectively disabled.

### Recommendation
Add a default (e.g., `defaultMaxAllowedMessageAgeSec`) and backfill `cfg.MaxAllowedMessageAgeSec` when zero in `NewHandler`, consistent with the treatment of `CallbackMaxAgeSec`, `MaxSavedCallbacks`, and `CallbackPruneIntervalSec`. Alternatively, explicitly reject configs with `MaxAllowedMessageAgeSec == 0` at startup rather than silently disabling the staleness check.

### Proof of Concept
1. Deploy a gateway `WebAPIHandler` with a `handlerConfig` JSON that omits `maxAllowedMessageAgeSec` (or explicitly sets it to `0`).
2. Capture (or construct) a `web_api_trigger` legacy message with an old, but valid-looking, `payload.Timestamp` (e.g., from days ago) and a valid signature/method.
3. Submit this message to the gateway as an unprivileged external client.
4. Observe in `HandleLegacyUserMessage` that the check `uint(time.Now().Unix())-0 > uint(payload.Timestamp)` evaluates true for the old timestamp, so the "stale message" rejection path at lines 372-383 is never hit, and the message is forwarded to all DON members via `don.SendToNode` (lines 416-419) as if it were fresh.

**Note:** I was not able to fully verify from the indexed code whether any additional upstream validation (e.g., signature-timestamp binding or replay-cache) exists elsewhere in the request pipeline for `MethodWebAPITrigger` messages that might mitigate this at another layer; a full audit of the message ingestion path leading into `HandleLegacyUserMessage` would require deeper inspection than the current index provides.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L80-99)
```go
func NewHandler(handlerConfig json.RawMessage, donConfig *config.DONConfig, don handlers.DON, httpClient network.HTTPClient, lggr logger.Logger) (*handler, error) {
	var cfg HandlerConfig
	err := json.Unmarshal(handlerConfig, &cfg)
	if err != nil {
		return nil, err
	}
	if cfg.CallbackMaxAgeSec == 0 {
		cfg.CallbackMaxAgeSec = defaultCallbackMaxAgeSec
	}
	if cfg.MaxSavedCallbacks == 0 {
		cfg.MaxSavedCallbacks = defaultMaxSavedCallbacks
	}
	if cfg.CallbackPruneIntervalSec == 0 {
		cfg.CallbackPruneIntervalSec = defaultCallbackPruneIntervalSec
	}

	nodeRateLimiter, err := ratelimit.NewRateLimiter(cfg.NodeRateLimiter)
	if err != nil {
		return nil, err
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
