## Title
Legacy Web API Trigger messages bypass allowlist and rate-limiting, allowing free DON resource consumption - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Sherlock report describes an L1→L2 bridge that lets a caller submit `depositERC20`/`depositERC20To` with `_l2Gas = 0`, so an unprivileged actor can force the DON/relayer to spend L2 execution resources without paying for them (no minimum-resource-consumption gate before dispatching work). The same structural gap — a user-facing entry point that dispatches work to a distributed set of nodes with an explicitly missing authorization/quota check — exists in the Chainlink Gateway's legacy Web API trigger path.

### Finding Description
The internet-facing Gateway's `ProcessRequest` routes any incoming "legacy" (DON-ID-addressed) JSON-RPC request to the target `Handler.HandleLegacyUserMessage` after only generic envelope validation (`msg.Validate()`), with no method-specific authorization performed at the gateway layer [1](#0-0) .

For the capabilities Web API handler, `HandleLegacyUserMessage` only checks that the payload decodes, that the timestamp is non-zero, and that the message is not "stale" (based on `MaxAllowedMessageAgeSec`) — then it explicitly skips allowlist and rate-limit enforcement per its own TODO, and immediately fans the request out to every member node of the DON: [2](#0-1) 

The `// TODO: apply allowlist and rate-limiting here` comment on line 384 documents that this code path has no per-sender authentication, no allowlist check, and no rate limiting before triggering `don.SendToNode` for every member of the DON — unlike the sibling JSON-RPC path (`HandleJSONRPCUserMessage`/`processTrigger` in `core/capabilities/webapi/trigger/trigger.go`), which does enforce `allowedSenders` and a `rateLimiter.Allow` check before dispatching [3](#0-2) . The `NewHandler` constructor only wires up a `nodeRateLimiter` for outbound node-originated calls, not a user-facing limiter for this legacy inbound path [4](#0-3) .

This means any caller who can reach the Gateway's legacy HTTP endpoint with a validly-shaped `web_api_trigger` message and a fresh timestamp can force the message to be broadcast to every node in the DON — consuming node compute/network resources — without being on the trigger's `allowedSenders` list and without any rate limit throttling that per-sender/global limiter would otherwise provide.

### Impact Explanation
This is a resource-consumption/DoS-class issue analogous to the "gasless bridging" report: an unprivileged, unauthenticated actor can cause the DON's nodes to do real work (message dispatch/processing) for free and outside of any quota, exactly the kind of "consume the resource without paying/being authorized for it" flaw the report highlights. Severity is bounded because the eventual per-workflow authorization is expected to happen downstream at the capability layer, but the Gateway/legacy handler itself provides no defense-in-depth, and the missing rate limiter opens a spam/DoS vector against the DON.

### Likelihood Explanation
Likelihood is high for reachability: the legacy path is a supported, still-wired code path (`HandleLegacyUserMessage` is part of the `handlers.Handler` interface and is invoked directly by `gateway.ProcessRequest` for any legacy DON-ID-addressed request) [5](#0-4) , requires no special credentials, and the omission is self-documented by the TODO comment rather than being a subtle bug, indicating it is a known, currently-unaddressed gap.

### Recommendation
Enforce the same `allowedSenders`/topic authorization and `rateLimiter.Allow` checks used in `core/capabilities/webapi/trigger/trigger.go`'s `processTrigger` before calling `don.SendToNode` in `HandleLegacyUserMessage`, or reject/deprecate the legacy path entirely in favor of the already-guarded JSON-RPC path.

### Proof of Concept
1. An attacker sends a JSON-RPC-over-HTTP request to the Gateway's public endpoint addressed to a known DON ID with `Body.Method = "web_api_trigger"` and a valid `webapicap.TriggerRequestPayload` (arbitrary `Topics`) and a recent `Timestamp`.
2. `gateway.ProcessRequest` validates only the envelope (`msg.Validate()`) and routes to the capabilities `handler.HandleLegacyUserMessage` [1](#0-0) .
3. `HandleLegacyUserMessage` passes the staleness check and, per the TODO, performs no allowlist or rate-limit check, then loops over all `donConfig.Members` and calls `don.SendToNode` for each [6](#0-5) .
4. Repeating this at high volume forces every node in the DON to process attacker-controlled messages with no throttling gate at this layer, consuming node resources without the sender ever being checked against `allowedSenders` or a rate limiter.

### Citations

**File:** core/services/gateway/gateway.go (L253-265)
```go
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L80-117)
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

	metrics, err := newMetrics()
	if err != nil {
		return nil, err
	}

	return &handler{
		config:          cfg,
		don:             don,
		donConfig:       donConfig,
		lggr:            logger.Named(lggr, "WebAPIHandler."+donConfig.DonID),
		httpClient:      httpClient,
		nodeRateLimiter: nodeRateLimiter,
		savedCallbacks:  make(map[string]*savedCallback),
		stopCh:          make(services.StopChan),
		metrics:         metrics,
	}, nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-420)
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
	return err
```

**File:** core/capabilities/webapi/trigger/trigger.go (L106-119)
```go
	for _, trigger := range triggers {
		for _, topic := range topics {
			if trigger.allowedTopics[topic] {
				matchedWorkflows++
				if !trigger.allowedSenders[sender.String()] {
					err = fmt.Errorf("unauthorized Sender %s, messageID %s", sender.String(), body.MessageID)
					h.lggr.Debugw(err.Error())
					continue
				}
				if !trigger.rateLimiter.Allow(body.Sender) {
					err = fmt.Errorf("request rate-limited for sender %s, messageID %s", sender.String(), body.MessageID)
					continue
				}
				fullyMatchedWorkflows++
```

**File:** core/services/gateway/handlers/handler.go (L31-47)
```go
type Handler interface {
	job.ServiceCtx

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleJSONRPCUserMessage(ctx context.Context, jsonRequest jsonrpc.Request[json.RawMessage], callback Callback) error

	// Handlers should not make any assumptions about goroutines calling HandleNodeMessage.
	// should be non-blocking
	// should validate the message inside the response
	HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error
```
