Confirmed: `nodeRateLimiter` only gates outgoing DON→gateway HTTP relaying (`handleWebAPIOutgoingMessage`, line 166), not the inbound `HandleLegacyUserMessage` path at all. The claim's core technical assertion holds up.

Key facts from investigation:
- `gateway.ProcessRequest` calls `msg.Validate()` before dispatch [1](#0-0) , which requires a well-formed ECDSA signature and recovers a signer address [2](#0-1) . However, this only proves the request was signed by *some* keypair — any attacker can generate a fresh key and sign arbitrary messages, so this is not an authorization/allowlist check, just a format/signature-recovery check.
- `HandleLegacyUserMessage` itself performs no sender allowlist or rate-limit check, matching the `// TODO: apply allowlist and rate-limiting here` comment [3](#0-2) , and unconditionally fans out to every DON member [4](#0-3) .
- The handler does have a `nodeRateLimiter` field [5](#0-4) , but it's only invoked in `handleWebAPIOutgoingMessage` (DON→gateway HTTP-relay direction, keyed by `nodeAddr`) [6](#0-5) , not on the inbound legacy trigger path — so the outbound rate limiter does not mitigate this inbound fan-out issue.
- A test file explicitly documents this as a known open gap: `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated` [7](#0-6) .
- The v2 HTTP trigger path does enforce JWT auth, workflow resolution, authorization, and rate-limiting in sequence [8](#0-7) , confirming the legacy path lacks equivalent protection.
- This legacy handler is still actively wired up: `NewHandlerFactory` maps `WebAPICapabilitiesType` to this handler [9](#0-8) , and deployment tooling (`deployment/cre/jobs/pkg/gateway_job.go`) still creates `GatewayHandlerTypeWebAPICapabilities` handlers for production gateway configs [10](#0-9) , and gateway job tests configure a `NodeRateLimiter` on this handler's config [11](#0-10)  — but as shown above, that config only rate-limits outbound DON messages, not this inbound fan-out.

This confirms the reachability concern the report flagged as unconfirmed: the legacy handler is indeed still registered in production gateway configs, not superseded/removed.

Audit Report

## Title
Missing allowlist and rate-limiting on gateway legacy `web_api_trigger` user messages allows unauthenticated fan-out DoS - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
The gateway's legacy WebAPI capability handler's `HandleLegacyUserMessage` dispatches every incoming `web_api_trigger` message to all DON members without any sender allowlist or rate-limit check, as explicitly marked by an unaddressed `// TODO: apply allowlist and rate-limiting here` comment. Any caller able to produce a validly-formatted, self-signed message (which requires no privileged credential — any freshly generated ECDSA key works) can trigger unbounded fan-out amplification against the DON.

## Finding Description
`gateway.ProcessRequest` validates message format and signature well-formedness via `msg.Validate()` before dispatch, but `Validate()`/`ExtractSigner()` only confirm the message is signed by *some* keypair — it does not check the signer against any allowlist of authorized senders. `handler.HandleLegacyUserMessage` then performs only payload-decode, non-zero-timestamp, and staleness checks before unconditionally registering a `savedCallback` and calling `don.SendToNode` once per DON member. The handler's only rate limiter (`nodeRateLimiter`) is wired solely into `handleWebAPIOutgoingMessage`, which governs DON→gateway HTTP-relay traffic keyed by `nodeAddr`, not this inbound user-message path — so it provides no protection here. This gap is corroborated by an explicit TODO left in the corresponding test file. The v2 HTTP trigger handler, by contrast, chains JWT auth, workflow-owner authorization, and rate-limiting before DON dispatch, showing the legacy path is a known-incomplete predecessor still left active.

## Impact Explanation
This maps to the DoS/resource-exhaustion impact class: an attacker who can reach the gateway's public endpoint can generate one-to-many amplification, with each attacker request producing one `SendToNode` call per DON member and one `savedCallbacks` registration, with no per-sender or global throttle gating that fan-out. The legacy handler type (`WebAPICapabilitiesType`) is still actively instantiated by `handler_factory.go` and by production job-deployment tooling (`gateway_job.go`), so this is not dead/removed code — it is a currently reachable path in the codebase as indexed.

## Likelihood Explanation
Likelihood is high: producing a validly-formatted, self-signed message requires only generating an ECDSA keypair locally — no credential, allowlist membership, or prior authorization is needed, since the format-level `Validate()` check that gates dispatch does not enforce authorization. The attack is fully repeatable at whatever rate the attacker's network connection to the gateway allows.

## Recommendation
Implement the allowlist and rate-limiting referenced in the TODO comment (`core/services/gateway/handlers/capabilities/handler.go:384`) before any `savedCallbacks` registration or DON dispatch in `HandleLegacyUserMessage`, mirroring the per-sender/global rate-limiting pattern already used in `OutgoingConnectorHandler.HandleGatewayMessage` and the v2 `httpTriggerHandler.checkRateLimit`/authorization chain. If this legacy handler type is intended to be deprecated, it should be removed from `handler_factory.go` and `gateway_job.go` to eliminate the exposure.

## Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration/allowlisting required).
2. Construct a `web_api_trigger` legacy `api.Message` with a valid JSON `TriggerRequestPayload` (non-zero, non-stale `Timestamp`), sign it with the generated key, and submit it to the gateway's user-facing endpoint (mirrors `triggerRequest`/`HandleLegacyUserMessage` flow used in `handler_test.go`).
3. Observe that the message passes `Validate()` and all in-handler checks, is registered in `savedCallbacks`, and triggers one `don.SendToNode` call per DON member (`core/services/gateway/handlers/capabilities/handler.go:417-419`).
4. Repeat at volume from the same or different self-generated keys — the request is never rejected for lack of allowlist membership or rate, only if malformed/stale/wrong-method, confirming unauthenticated fan-out amplification is unmitigated in this code path.

### Citations

**File:** core/services/gateway/gateway.go (L253-264)
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
```

**File:** core/services/gateway/api/message.go (L54-88)
```go
func (m *Message) Validate() error {
	if m == nil {
		return errors.New("nil message")
	}
	if len(m.Signature) != MessageSignatureHexEncodedLen {
		return errors.New("invalid hex-encoded signature length")
	}
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
	if len(m.Body.Method) == 0 || len(m.Body.Method) > MessageMethodMaxLen {
		return errors.New("invalid method name length")
	}
	if strings.HasSuffix(m.Body.Method, NullChar) {
		return errors.New("method name ending with null bytes")
	}
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L50-57)
```go
	config          HandlerConfig
	don             handlers.DON
	donConfig       *config.DONConfig
	savedCallbacks  map[string]*savedCallback
	mu              sync.Mutex
	lggr            logger.Logger
	httpClient      network.HTTPClient
	nodeRateLimiter *ratelimit.RateLimiter
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-396)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```

**File:** core/services/gateway/handler_factory.go (L84-85)
```go
	case WebAPICapabilitiesType:
		return capabilities.NewHandler(handlerConfig, donConfig, don, hf.httpClient, hf.lggr)
```

**File:** deployment/cre/jobs/pkg/gateway_job.go (L255-256)
```go
			case GatewayHandlerTypeWebAPICapabilities:
				hs = append(hs, newDefaultWebAPICapabilitiesHandler())
```

**File:** deployment/cre/jobs/pkg/gateway_job_test.go (L246-250)
```go
[gatewayConfig.Services.Handlers.Config.NodeRateLimiter]
globalBurst = 10
globalRPS = 50
perSenderBurst = 10
perSenderRPS = 10
```
