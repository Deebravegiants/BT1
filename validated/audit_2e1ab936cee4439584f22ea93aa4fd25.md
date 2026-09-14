Found a valid analog. In `core/services/gateway/handlers/capabilities/handler.go`, `HandlerConfig.MaxAllowedMessageAgeSec` is never given a default (unlike `CallbackMaxAgeSec`, `MaxSavedCallbacks`, `CallbackPruneIntervalSec`, which are all zero-checked in `NewHandler`), and the staleness check in `HandleLegacyUserMessage` performs arithmetic directly on this uninitialized value, matching the "uninitialized duration bypasses a time-based gate" bug class from the report.

### Title
Uninitialized `MaxAllowedMessageAgeSec` Nullifies Stale-Message Replay Protection in WebAPI Gateway Handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`HandlerConfig.MaxAllowedMessageAgeSec` is a `uint` loaded from JSON config in `NewHandler` but, unlike every other numeric field in the same config struct, has no zero-value fallback applied before use. [1](#0-0) 

### Finding Description
`NewHandler` unmarshals `HandlerConfig` and explicitly defaults `CallbackMaxAgeSec`, `MaxSavedCallbacks`, and `CallbackPruneIntervalSec` when they are zero, but `MaxAllowedMessageAgeSec` receives no such treatment. [2](#0-1) 

This value is later used directly in the staleness check inside `HandleLegacyUserMessage`, which is the entry point for handling a user-supplied `api.Message` on the internet-facing gateway before it is forwarded to DON nodes:
```go
if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) {
    ...
    return callback.SendResponse(...) // rejected as stale
}
``` [3](#0-2) 

If `MaxAllowedMessageAgeSec` is left at its zero value (e.g., the operator's config for this handler omits the field, mirroring exactly how the `Fishing.stakeDuration` was left unset in the referenced report), the expression collapses to `time.Now().Unix() > payload.Timestamp`, i.e., any message with a timestamp less than or equal to the current time passes the staleness check — including arbitrarily old timestamps. This defeats the intended anti-replay/staleness protection for unprivileged, internet-facing user requests (`HandleLegacyUserMessage` processes messages arriving through the gateway's user-facing message envelope path, not privileged operator/node input). The check `payload.Timestamp == 0` guards only the exact zero-timestamp case, not old-but-nonzero timestamps. [4](#0-3) 

### Impact Explanation
With the staleness guard silently disabled, an attacker who has captured or replayed an old signed `api.Message`/request envelope (or who crafts a request with an arbitrarily old but validly-signed timestamp) can have it accepted and dispatched to all DON members via `don.SendToNode`, bypassing the intended anti-replay time window. This is a request-impersonation/replay class issue on the gateway's internet-facing message-handling path, comparable in nature to the referenced report's core issue of a zero-valued duration parameter silently neutering a time-based access/validity check. [5](#0-4) 

### Likelihood Explanation
Likelihood depends entirely on whether an operator deploys this handler with `maxAllowedMessageAgeSec` unset/omitted in the JSON handler config — there is no compile-time or startup-time enforcement requiring it to be set, unlike the three sibling fields that are defaulted. This is analogous to the original finding, where exploitability hinges on a deployment/configuration gap rather than a universally-triggerable code defect, so I rate confidence in "reachability from an unprivileged request" as solid, but likelihood of the vulnerable zero-config state actually existing in a given deployment as uncertain without access to the actual operator config files used for this specific handler.

### Recommendation
Add a default (e.g., `defaultCallbackMaxAgeSec`-style constant) for `MaxAllowedMessageAgeSec` in `NewHandler` when it is zero, consistent with the other three fields, e.g.:
```go
if cfg.MaxAllowedMessageAgeSec == 0 {
    cfg.MaxAllowedMessageAgeSec = defaultMaxAllowedMessageAgeSec
}
```
This should be added immediately after the existing defaulting block at [6](#0-5) .

### Proof of Concept
1. Configure the `WebAPIHandler` (`handlers/capabilities`) without setting `maxAllowedMessageAgeSec` in its JSON config (or explicitly set it to `0`).
2. Construct a signed `api.Message` with `Method = MethodWebAPITrigger` and `payload.Timestamp` set to a very old (but nonzero) unix timestamp.
3. Submit the message through the gateway's user-facing legacy message path so it reaches `HandleLegacyUserMessage`.
4. Because `h.config.MaxAllowedMessageAgeSec == 0`, the check `uint(time.Now().Unix()) - 0 > uint(payload.Timestamp)` reduces to `now > timestamp`, which is true for any past timestamp, so the "stale message" rejection never triggers, and the old message is forwarded to all DON members via `don.SendToNode`. [7](#0-6)

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L63-94)
```go
type HandlerConfig struct {
	NodeRateLimiter         ratelimit.RateLimiterConfig `json:"nodeRateLimiter"`
	MaxAllowedMessageAgeSec uint                        `json:"maxAllowedMessageAgeSec"`

	CallbackMaxAgeSec        int `json:"callbackMaxAgeSec"`
	MaxSavedCallbacks        int `json:"maxSavedCallbacks"`
	CallbackPruneIntervalSec int `json:"callbackPruneIntervalSec"`
}

type savedCallback struct {
	id        string
	createdAt time.Time
	handlers.Callback
}

var _ handlers.Handler = (*handler)(nil)

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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-419)
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
