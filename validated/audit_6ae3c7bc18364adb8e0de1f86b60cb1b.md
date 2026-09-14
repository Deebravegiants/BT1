### Title
Missing allowlist/rate-limit enforcement before forwarding unprivileged web-API trigger requests to the DON - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The external report describes an Auction contract that omits a state-gating modifier (`whenNotPaused`) on user-facing bid functions, letting unprivileged callers act when the protocol should be blocked. The closest analog in this codebase is `HandleLegacyUserMessage` in the gateway's `web_api_trigger` capability handler, which is reachable directly from an unprivileged, internet-facing client and forwards the request to every DON node without ever performing the sender allowlist / rate-limit check that the code explicitly documents as required but not yet implemented.

### Finding Description
`(h *handler) HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` is the entry point the gateway (`core/services/gateway/gateway.go` `ProcessRequest`) calls for legacy user messages, i.e. requests coming straight from an HTTP client through `g.httpServer` with no membership in the DON — this is the "unprivileged client request" surface.

The function performs payload decoding, timestamp/staleness checks, and a method-name check, then explicitly acknowledges the missing control:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [1](#0-0) 

Immediately after this, with no sender allowlist check and no per-sender rate limiting applied, the handler broadcasts the caller-supplied trigger request to every member of the DON:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()

// Send original request to all nodes
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [2](#0-1) 

Note that a `nodeRateLimiter` field exists on the `handler` struct [3](#0-2)  and is constructed in `NewHandler` [4](#0-3) , but it is never referenced or enforced inside `HandleLegacyUserMessage`. This mirrors the audit-report pattern precisely: the gating primitive (like `whenNotPaused`) exists and is used elsewhere in the codebase (e.g. sibling handlers `core/services/gateway/handlers/vault/handler.go` and `core/services/gateway/handlers/confidentialrelay` enforce request validators/authorizers/rate limiters before forwarding — see `requestValidator`/`authorizer`/`nodeRateLimiter` usage in `newHandlerWithAuthorizer`) [5](#0-4) , but this specific handler forwards unauthenticated/unallowlisted requests unconditionally.

### Impact Explanation
Any unprivileged internet-facing client can send arbitrary `web_api_trigger` requests through the gateway HTTP endpoint, and they will be relayed to every node in the target DON with no allowlist or rate-limit gate. This enables:
- Triggering workflow executions on behalf of arbitrary/unauthenticated senders (request impersonation / unauthorized job run), since the sender identity encoded in the payload is not cross-checked against an allowlist at this layer.
- Denial-of-service against the DON nodes and their downstream WASM/workflow engines, since a caller can flood `SendToNode` calls to all members without a rate limit being applied (the configured `nodeRateLimiter` is dead code for this path).

This matches the "allowlist or quota bypass" and "unauthorized job run" categories called out as acceptable analog impacts.

### Likelihood Explanation
High. The gateway's HTTP endpoint is explicitly designed to accept unauthenticated client traffic (`gateway.ProcessRequest` → `HandleLegacyUserMessage`), and the only checks performed prior to fan-out are payload well-formedness, a staleness timestamp check, and a method-name equality check — all attacker-controlled or trivially satisfied. No secret, session, or role is required to reach this code path.

### Recommendation
Enforce the sender allowlist and per-sender/global rate limiting inside `HandleLegacyUserMessage` before the loop that calls `don.SendToNode`, consistent with the pattern used by the vault and confidential-relay handlers (`requestValidator`, `authorizer`, `nodeRateLimiter.Allow(...)`). Reject or drop requests from senders that are not allowlisted or that exceed the configured rate before propagating them to DON nodes.

### Proof of Concept
1. Deploy a gateway configured with the `capabilities` (`web-api-capabilities`) handler and a target DON.
2. From an unauthenticated HTTP client, POST a legacy JSON-RPC message with `Body.Method == "web_api_trigger"`, a valid (non-stale) `Timestamp`, and an arbitrary `Sender`.
3. Observe that `HandleLegacyUserMessage` accepts the message and calls `don.SendToNode` for every DON member without any allowlist lookup or rate-limit check, because the "TODO: apply allowlist and rate-limiting here" gate has never been implemented — confirmed by direct reading of the function body [6](#0-5) .
4. Repeating the request rapidly from the same unauthenticated source demonstrates unrestrained fan-out to the DON with no throttling, since `h.nodeRateLimiter` is never invoked in this path.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L48-61)
```go
type handler struct {
	services.StateMachine
	config          HandlerConfig
	don             handlers.DON
	donConfig       *config.DONConfig
	savedCallbacks  map[string]*savedCallback
	mu              sync.Mutex
	lggr            logger.Logger
	httpClient      network.HTTPClient
	nodeRateLimiter *ratelimit.RateLimiter
	wg              sync.WaitGroup
	stopCh          services.StopChan
	metrics         *metrics
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L96-99)
```go
	nodeRateLimiter, err := ratelimit.NewRateLimiter(cfg.NodeRateLimiter)
	if err != nil {
		return nil, err
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-421)
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
	return err
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L211-244)
```go
func newHandlerWithAuthorizer(methodConfig json.RawMessage, donConfig *config.DONConfig, don gwhandlers.DON, capabilitiesRegistry capabilitiesRegistry, authorizer vaultcap.Authorizer, jwtAuth services.Service, lggr logger.Logger, clock clockwork.Clock, limitsFactory limits.Factory) (*handler, error) {
	var cfg Config
	if err := json.Unmarshal(methodConfig, &cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal method config: %w", err)
	}

	if cfg.RequestTimeoutSec == 0 {
		cfg.RequestTimeoutSec = 30
	}

	nodeRateLimiter, err := ratelimit.NewRateLimiter(cfg.NodeRateLimiter)
	if err != nil {
		return nil, fmt.Errorf("failed to create node rate limiter: %w", err)
	}

	metrics, err := newMetrics()
	if err != nil {
		return nil, fmt.Errorf("failed to create metrics: %w", err)
	}

	requestValidator, err := vaultcap.NewRequestValidatorFromLimitsFactory(limitsFactory)
	if err != nil {
		return nil, err
	}

	writeMethodsEnabled, err := limits.MakeGateLimiter(limitsFactory, cresettings.Default.GatewayVaultManagementEnabled)
	if err != nil {
		return nil, fmt.Errorf("could not create vault mgmt limiter: %w", err)
	}

	requestProcessor, err := vaultcap.NewGatewayVaultRequestProcessor(requestValidator, authorizer, false, lggr)
	if err != nil {
		return nil, fmt.Errorf("failed to create gateway vault request processor: %w", err)
	}
```
