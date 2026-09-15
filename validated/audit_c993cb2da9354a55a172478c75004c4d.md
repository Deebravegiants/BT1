Audit Report

## Title
Missing Allowlist/Rate-Limit Validation on Legacy Web API Gateway Trigger Messages Allows Unrestricted Fan-out to All DON Nodes - ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
`handler.HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` is reachable from any caller able to submit a well-formed, signed JSON-RPC request to the gateway's HTTP endpoint via `gateway.ProcessRequest`. The function validates payload shape, timestamp staleness, and method name, but performs no check that the message's signer (`msg.Body.Sender`, derived purely from `ExtractSigner` over attacker-controlled signature material) is an authorized/allowlisted caller for the target DON, and applies no rate limiting, before broadcasting the request to every node in `h.donConfig.Members`.

## Finding Description
`gateway.ProcessRequest` decodes the request, calls `msg.Validate()`, and dispatches directly to `h.HandleLegacyUserMessage(ctx, msg, callback)` for any request carrying a `DonID`. [1](#0-0) 

`Message.Validate()` only checks field lengths/formats and recovers the signer address from the signature via `ExtractSigner`, assigning it to `m.Body.Sender` — it performs no allowlist/authorization lookup; any keypair holder can produce a validly-formatted, validly-signed message. [2](#0-1) 

`HandleLegacyUserMessage` then checks payload decode success, timestamp presence, staleness, and method name — but the explicit `// TODO: apply allowlist and rate-limiting here` comment sits directly before the method-name check, and no such check exists anywhere in the function. [3](#0-2) 

After these checks pass, the handler saves the callback and forwards the client-supplied request to **every** DON member node, unconditionally: [4](#0-3) 

The `nodeRateLimiter` field on the handler is applied only to the reverse/outgoing path (`handleWebAPIOutgoingMessage`, keyed by `nodeAddr`), not to inbound legacy trigger requests. [5](#0-4) 

By contrast, the newer v2 HTTP trigger handler explicitly performs `authorizeRequest` and `checkRateLimit` before dispatching to nodes, demonstrating that this is a known and expected control that the legacy path is missing. [6](#0-5) 

## Impact Explanation
Because there is no allowlist check binding the message's signer to authorization for the target DON/workflow, any actor capable of generating an ECDSA signature (i.e., any unprivileged external caller) can submit a `web_api_trigger` legacy message for an arbitrary `DonID` and have it broadcast to all member nodes of that DON. This is a concrete, in-scope "gateway request impersonation" / "unauthorized job/workflow triggering" impact, since the security assumption that only authorized senders can trigger a DON's workflow is broken at the gateway layer. The absence of rate limiting on this path additionally allows unrestricted repeated fan-out, though pure DDoS-only impact is explicitly out of scope per `SECURITY.md`; the primary, in-scope impact here is the unauthorized-trigger/impersonation gap, not the DoS aspect alone.

## Likelihood Explanation
The path is directly reachable from `gateway.ProcessRequest`, the top-level entrypoint for any external HTTP caller, requiring only a syntactically valid signature (which any keyholder can produce) — no allowlist membership, node registration, or prior authorization is required. The explicit `TODO: apply allowlist and rate-limiting here` comment in the shipped code confirms this is a known, still-open gap rather than an intentional design decision, and the parallel v2 handler's `authorizeRequest`/`checkRateLimit` calls demonstrate the expected mitigation is both understood and technically feasible.

## Recommendation
Add caller/workflow authorization (allowlist check keyed on `msg.Body.Sender` against the DON/workflow's configured allowlist) and per-sender rate limiting in `HandleLegacyUserMessage`, prior to storing the callback and calling `don.SendToNode`, mirroring the `authorizeRequest`/`checkRateLimit` pattern in `httpTriggerHandler.HandleUserTriggerRequest`. Reject unauthorized/non-allowlisted senders and enforce a quota before any fan-out to DON nodes.

## Proof of Concept
1. Generate an arbitrary ECDSA keypair (no prior registration/allowlisting needed) and craft a `Message` with `Body.Method = "web_api_trigger"`, a valid `TriggerRequestPayload` (fresh `Timestamp`), and a target `DonID` for a DON the caller has no legitimate relationship to; sign it with `Message.Sign`.
2. Submit the resulting JSON-RPC request to the gateway's HTTP endpoint, which routes through `gateway.ProcessRequest` → `handler.HandleLegacyUserMessage` (exercised similarly by `TestHandlerReceiveHTTPMessageFromClient` in `core/services/gateway/handlers/capabilities/handler_test.go`).
3. Observe the request passes `Validate()`, payload/timestamp/method checks, and is forwarded via `don.SendToNode` to every member of `h.donConfig.Members`, confirming no allowlist or rate-limit rejection occurs for an arbitrary, previously-unregistered signer.

### Citations

**File:** core/services/gateway/gateway.go (L253-272)
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

	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
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
