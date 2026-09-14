### Title
Missing sender allowlist enforcement in Gateway legacy `web_api_trigger` message path allows unauthorized workflow triggering - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Camel advisory describes a case where a receiving component performs a superficial "allow-listed namespace" check but omits the actual authorization gate (`transferExchange`) that should have controlled trust, letting an unprivileged sender inject data that is processed as if authorized. The Chainlink Gateway's legacy capabilities-handler path exhibits the same asymmetric-trust pattern: `Message.Validate()` only verifies that a message carries *some* recoverable ECDSA signature — it never checks that the recovered signer is an allowlisted/authorized sender for the target DON — and the handler that consumes it, `HandleLegacyUserMessage`, explicitly skips authorization with a `// TODO: apply allowlist and rate-limiting here` comment, then unconditionally forwards the message to every DON node member.

### Finding Description
`Message.Validate()` in [1](#0-0)  checks structural fields (lengths, null-byte suffixes) and calls `ExtractSigner()`, which merely recovers *an* address from the ECDSA signature over the message body — it never compares that address against any registered/allowlisted sender set. Any unprivileged external actor can generate a fresh keypair, sign an arbitrary `web_api_trigger` message, and this will pass `Validate()`.

That signed message is routed by `gateway.ProcessRequest` for legacy (DON-ID-bearing) requests directly to `HandleLegacyUserMessage`: [2](#0-1) . In the capabilities handler, `HandleLegacyUserMessage` decodes the payload, checks timestamp staleness and method name, but — as the code itself documents — skips allowlist and rate-limit checks before forwarding the request to all DON members: [3](#0-2) 

This is the same trust-boundary asymmetry as the CVE: the "acceptance check" (well-formed signature / allow-listed class) is not equivalent to the "authorization check" (registered sender / `transferExchange`-style opt-in) that the code should be enforcing before trusting and propagating the payload. This gap is corroborated by the handler's own test suite, which contains a matching TODO: `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated` [4](#0-3) . By contrast, the JSON-RPC vault path in the same gateway package does enforce an `Authorizer.AuthorizeRequest` allowlist check before processing [5](#0-4) , confirming that allowlisting is an expected control that is missing specifically on this legacy path.

### Impact Explanation
An unprivileged network actor who can reach the Gateway's HTTP endpoint can submit an arbitrary self-signed `web_api_trigger` message for any configured DON. Because `HandleLegacyUserMessage` forwards the request to every DON node member without verifying the sender is an authorized/allowlisted trigger source, this permits unauthorized triggering of workflow capability requests towards DON nodes (CWE-862/863-style missing authorization, analogous to CVE-2026-43866's post-check trust bypass), and — since it also currently forwards these before any rate limiting — the same path could be used to flood every DON member with attacker-controlled trigger traffic.

### Likelihood Explanation
Reachable directly from an unauthenticated HTTP-facing client of the Gateway (`ProcessRequest` is the outward-facing entry point handling raw HTTP request bodies). The only barrier is producing a syntactically valid signature over attacker-chosen fields, which requires no privileged key — a fresh ECDSA keypair suffices, since `Validate()`/`ExtractSigner()` accept any signer.

### Recommendation
Implement the sender allowlist/authorization check explicitly called out by the `// TODO` in `HandleLegacyUserMessage` before saving the callback and forwarding the request to DON members — mirroring the `Authorizer.AuthorizeRequest` gate used on the vault JSON-RPC path — and add rate limiting per-sender to this path.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no relationship to any legitimate workflow owner or registered sender).
2. Construct an `api.Message` with `Body.Method = "web_api_trigger"`, a valid `DonID` for a target DON, and a well-formed `TriggerRequestPayload` with a current timestamp.
3. Call `msg.Sign(privateKey)` with the attacker's own key — this produces a signature that passes `Message.Validate()` because it only checks signature well-formedness/recoverability, not sender authorization.
4. Submit the JSON-RPC-wrapped message to the Gateway's HTTP endpoint.
5. Observe in `gateway.ProcessRequest` → `HandleLegacyUserMessage` (per [3](#0-2) ) that the message is forwarded to all DON node members with no allowlist check rejecting the unauthorized sender.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
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
