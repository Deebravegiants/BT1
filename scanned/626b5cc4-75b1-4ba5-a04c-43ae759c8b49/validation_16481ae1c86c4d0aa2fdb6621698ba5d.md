Based on my investigation, `Message.Validate()` in `core/services/gateway/api/message.go` only verifies signature format and extracts a signer address via `ExtractSigner` — it does **not** check that the signer/sender is an authorized node or user, nor does it apply any allowlist. That check is explicitly deferred: in `core/services/gateway/handlers/capabilities/handler.go`, the `HandleLegacyUserMessage` function contains a `// TODO: apply allowlist and rate-limiting here` comment immediately before dispatching the (weakly-validated) request to every DON member.

### Title
Missing Allowlist/Authorization Check on Legacy WebAPI Trigger Gateway Path - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The legacy gateway user-message path for the WebAPI capability (`web_api_trigger` method) forwards attacker-controlled requests to all DON nodes without any allowlist, per-user authorization, or user-identity check, despite the code explicitly acknowledging this gap.

### Finding Description
`gateway.ProcessRequest` in [1](#0-0)  routes any request carrying a `don_id` to the legacy handler after only calling `msg.Validate()`. `Message.Validate()` in [2](#0-1)  checks field lengths/signature format and extracts a signer address from the signature, but it never verifies that signer against any allowlist, node registry, or user permission table — it just accepts whatever key signed the payload.

That signer/message is then handed to `HandleLegacyUserMessage` in [3](#0-2) , which decodes the `TriggerRequestPayload`, checks timestamp freshness, and checks the method name — but the code explicitly states `// TODO: apply allowlist and rate-limiting here` at [4](#0-3)  right before broadcasting the request to every DON member via `don.SendToNode`.

This contrasts with the newer/parallel gateway handlers in the same codebase that do enforce authorization before dispatching to nodes: the vault handler requires `AllowListBasedAuth`/JWT authorization via `requestProcessor.ProcessRequest` in [5](#0-4) , and the v2 HTTP trigger handler requires JWT-based authentication as documented in [6](#0-5) . The legacy WebAPI handler lacks this equivalent control.

### Impact Explanation
Any unprivileged client capable of reaching the gateway's public HTTP endpoint and producing a validly-*formatted* (not validly-*authorized*) signed message can trigger a `web_api_trigger` job run broadcast to all nodes of a DON, since there is no allowlist gate comparable to the vault/v2 http trigger handlers. This maps to the CVE's "unauthorized action via unauthenticated/unauthorized endpoint" bug class — request impersonation / unauthorized job trigger on an internet-facing gateway component.

### Likelihood Explanation
The gateway HTTP endpoint (`ProcessRequest`) is explicitly internet-facing and designed to accept external client requests; reaching this legacy code path only requires supplying a `don_id` in the request body and any valid-format ECDSA signature (the signer need not be a known/authorized identity). This makes the code path directly reachable without needing insider access, though it is limited to DONs still configured to use the legacy WebAPI capability handler rather than the newer v2/vault path.

### Recommendation
Add an authorization/allowlist check (mirroring `AllowListBasedAuth`/`Authorizer` used in the vault and v2 HTTP trigger handlers) inside `HandleLegacyUserMessage` before forwarding requests to DON nodes, replacing the outstanding TODO with an actual allowlist and rate-limiting enforcement tied to the message's extracted signer (`msg.Body.Sender`).

### Proof of Concept
1. Craft a `MessageBody` with `Method: "web_api_trigger"`, a valid `don_id` matching a configured legacy WebAPI DON, and a `TriggerRequestPayload` with `Timestamp` set to current time.
2. Sign the message with any arbitrary ECDSA private key (not registered/authorized anywhere) using `Message.Sign`.
3. POST the raw JSON to the gateway's public HTTP endpoint.
4. `gateway.ProcessRequest` → `msg.Validate()` succeeds (only checks format/signature well-formedness) → `HandleLegacyUserMessage` executes and calls `don.SendToNode` for every DON member, without ever checking whether the signer is allowlisted — confirming the missing authorization gate noted by the `// TODO` at line 384.

**Caveat:** I could not fully confirm whether this legacy handler path is still wired up in production DON configurations or is deprecated/unreachable in favor of the v2 HTTP trigger handler; the index does not show a definitive routing/config table confirming which DONs still use this legacy handler. If a Devin session investigates this further, verifying handler registration in production job specs/configs would strengthen or refute reachability.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-420)
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L422-434)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L79-82)
```markdown
1. **Request Validation**: Validates JSON-RPC format, method, and parameters
2. **Workflow Resolution**: Resolves workflow ID from selector (ID, owner, name, tag)
3. **Authentication**: Verifies JWT token (ECDSA signature) and checks authorized keys
4. **Rate Limiting**: Enforces per-workflow-owner rate limits
```
