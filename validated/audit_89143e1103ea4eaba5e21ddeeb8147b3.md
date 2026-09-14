### Title
Legacy WebAPI Trigger gateway path lacks sender allowlisting, letting any unprivileged caller broadcast attacker-controlled trigger events to all DON nodes - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The gateway's legacy `web_api_trigger` path (`handler.HandleLegacyUserMessage`) accepts any externally-submitted, self-signed `api.Message`, checks only payload shape/timestamp freshness, and then forwards the request verbatim to *every* member of the DON — with no verification that the signer/sender is an authorized or expected source for the workflow/topic being triggered. This mirrors the TradingVault finding: a caller with no special relationship to a resource (here, a workflow/DON) can unilaterally force a state-affecting action (a trigger event delivered to all nodes) that should require the resource owner's consent or an allowlist check, without the affected party's consent.

### Finding Description
`HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` performs the following checks on an incoming `api.Message`:
1. Unmarshal `payload` into `webapicap.TriggerRequestPayload` [1](#0-0) 
2. Reject if `payload.Timestamp == 0` [2](#0-1) 
3. Reject if the message is older than `MaxAllowedMessageAgeSec` [3](#0-2) 
4. Immediately followed by an explicit acknowledgement that sender/allowlist checks are missing: `// TODO: apply allowlist and rate-limiting here` [4](#0-3) 
5. The request is then broadcast, unmodified, to **every** node in the DON: `for _, member := range h.donConfig.Members { err = errors.Join(err, don.SendToNode(ctx, member.Address, req)) }` [5](#0-4) 

The only authentication performed on the message is `msg.Validate()`, called earlier by the gateway's `ProcessRequest`, which merely verifies the ECDSA signature is well-formed and derives `Body.Sender` from whatever key signed the message: [6](#0-5)  and [7](#0-6) . Because any caller can generate an arbitrary ECDSA keypair, sign a `TriggerRequestPayload` with an arbitrary `TriggerId`/`Topics`, and satisfy `Validate()`, there is no proof that the sender is an authorized initiator for the DON, workflow, or topic being triggered — the "consent" of the workflow owner/DON operator to accept a trigger from this sender is never checked at the gateway layer.

This is functionally analogous to the reported `TradingVault.deposit()` issue: in both cases, an operation that should require the affected party's authorization (deposit accounting / trigger delivery) is instead performed purely on the say of an arbitrary, unvetted caller, with the enforcement of correctness deferred ("to allowed depositor vetting" / "to a TODO for allowlist checks") rather than actually implemented at this layer.

The handler's own test suite explicitly documents this gap as unresolved: `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated` [8](#0-7) .

By contrast, the newer v2 HTTP-trigger gateway handler path does not expose this legacy method (`HandleLegacyUserMessage` explicitly errors there) [9](#0-8) , and other gateway-routed flows such as the Vault capability enforce an explicit `AuthorizeRequest` step before any node dispatch [10](#0-9) , confirming that allowlisting/authorization at the gateway is the expected control that is simply missing in this legacy capabilities handler path.

### Impact Explanation
Any unauthenticated internet client that can reach the gateway's HTTP endpoint and knows (or guesses) a valid `DonID`/method name can:
- Forge a `TriggerRequestPayload` (arbitrary `TriggerId`, `Topics`, `Params`) and have the gateway broadcast it to every node in that DON without any check that the sender is permitted to originate that trigger.
- Cause spurious/unauthorized job runs on nodes for workflows subscribed to that trigger/topic, since the only gate at the gateway is timestamp freshness, not sender identity or workflow ownership.
- Potentially exhaust node/gateway resources (each such request creates a `savedCallback` entry and fans out to all DON members), though a bounded `pruneCallbacks`/`nodeRateLimiter` exists for other paths — this legacy trigger ingestion path itself has no rate limiting per the TODO.

This matches the "unauthorized job run" impact class called out in the validation criteria.

### Likelihood Explanation
Likelihood is high for reachability (the code path is directly reachable from an unauthenticated `ProcessRequest` call as long as a legacy DON-ID-addressed message is used), but actual exploit impact depends on:
- Whether node-side handlers additionally validate the sender/topic before acting on the trigger (this is outside the scope of the reviewed gateway code and could not be confirmed with the tools available).
- Whether this legacy `web_api_trigger` handler is still deployed/enabled in production DON configurations, versus being superseded by the v2 HTTP trigger handler (which does implement proper authorization and explicitly disables this legacy path).

Given the explicit, unresolved `TODO` comments in both the handler and its test file, this is a known, acknowledged gap rather than a subtle bug — consistent with "Acknowledged" status pattern in the original report.

### Recommendation
- Implement the sender/topic allowlist check called out in the `TODO` in `HandleLegacyUserMessage` before forwarding requests to DON members, mirroring the `AuthorizeRequest` pattern used in the Vault gateway handler (`core/capabilities/vault/gateway_vault_request_processor.go`).
- Add rate limiting on the incoming legacy trigger path per sender, similar to `nodeRateLimiter` used for outgoing node messages.
- If this legacy path is deprecated in favor of the v2 HTTP trigger handler, consider disabling/removing it entirely to eliminate the exposure, following the pattern already used in `v2/http_handler.go` where `HandleLegacyUserMessage` unconditionally errors.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no association with any legitimate workflow owner or DON member).
2. Construct a `TriggerRequestPayload` with a chosen `TriggerId`/`Topics`/current `Timestamp`, wrap it in an `api.Message` addressed to a known `DonID` with `Method = "web_api_trigger"`, and sign it with the arbitrary key (as done in the handler's own test helper `triggerRequest` in `handler_test.go`, lines 193-234).
3. Submit this as a legacy JSON-RPC request to the gateway's public HTTP endpoint, which routes through `gateway.ProcessRequest` → `handler.HandleLegacyUserMessage`.
4. Observe that the message passes `Validate()` (valid signature format) and the payload/timestamp checks, and is forwarded to every DON member via `don.SendToNode`, with no verification that the arbitrary signer is authorized to originate this trigger — exactly as exercised (without any sender allowlist assertion) in `TestHandlerReceiveHTTPMessageFromClient` in `handler_test.go`.

**Uncertainty note:** I could not verify from the indexed code whether a downstream, node-side authorization layer (outside the gateway package) independently blocks unauthorized triggers before a workflow actually executes, which would reduce real-world impact. Confirming this would require inspecting the node-side capability/trigger execution code, which was not fully available in this indexed search. A Devin session with full repository access would be needed to trace the complete node-side handling of `MethodWebAPITrigger` messages to confirm whether this gateway-level gap is mitigated elsewhere.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-357)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-370)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L416-420)
```go
	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L388-390)
```go
func (h *gatewayHandler) HandleLegacyUserMessage(context.Context, *api.Message, handlers.Callback) error {
	return errors.New("HTTP capability gateway handler does not support legacy messages")
}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-277)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}

```
