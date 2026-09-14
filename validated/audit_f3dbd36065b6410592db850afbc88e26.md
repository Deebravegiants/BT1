### Title
Gateway WebAPI trigger handler forwards unauthenticated/unallowlisted user requests to all DON nodes - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The gateway's legacy WebAPI handler accepts any cryptographically well-formed `web_api_trigger` message from an unprivileged HTTP client and broadcasts it to every node in the DON without ever checking that the sender/workflow is allowlisted, mirroring the IP-in-IP CVE's core defect: a forwarding component that relays arbitrary externally supplied traffic to internal destinations without validating that the source is authorized to reach that destination.

### Finding Description
`gateway.ProcessRequest` in [1](#0-0)  decodes an inbound JSON-RPC request from the public `/user` HTTP endpoint and dispatches it to the DON-specific `Handler` based only on service name / DON ID — there is no authorization gate at the gateway layer for legacy messages.

For the capabilities WebAPI handler, `HandleLegacyUserMessage` performs only structural checks (payload decoding, `Timestamp != 0`, message staleness) and explicitly skips authorization: [2](#0-1) 

Right after that skipped check, the request is converted via `common.ValidatedRequestFromMessage` and forwarded to **every** node in the DON: [3](#0-2) 

The only gate on the message is `api.Message.Validate()`, which merely checks field-length constraints and recovers *a* valid ECDSA signer from the signature — it does not verify the recovered signer is an allowlisted or otherwise authorized entity: [4](#0-3) 

Any client can generate a fresh keypair, sign a `web_api_trigger` message with it, and the message will pass `Validate()` (since it only checks *a* valid signature exists, not that the signer is permitted) and be relayed to all DON nodes. This is analogous to the IP-in-IP flaw: the gateway "routes" (forwards) inbound traffic to an internal destination (the DON nodes) purely based on structural validity, not based on an explicit source→destination authorization relationship — the exact "TODO: apply allowlist and rate-limiting here" comment confirms this is a known, unimplemented gap in this specific code path, unlike the sibling vault (`core/capabilities/vault/gw_handler.go`) and confidential-relay handlers, which do enforce `AuthorizeRequest`/allowlist checks before forwarding.

### Impact Explanation
An unauthenticated/unprivileged actor can inject arbitrary `web_api_trigger` messages that are broadcast to all nodes of a DON, triggering node-side workflow processing (`handleWebAPITriggerMessage`/downstream capability execution) without being on the workflow registry allowlist. This can be used to flood DON nodes with attacker-controlled triggers (resource exhaustion / reflective load amplification onto the DON, paralleling the reflective-DDoS impact of the CVE), or to invoke trigger processing for workflows the attacker does not own, bypassing the intended access-control model that other gateway handlers (vault, confidential relay) enforce.

### Likelihood Explanation
High: the code path requires no prior authentication beyond generating a throwaway ECDSA keypair to produce a technically-valid signature, and the missing authorization is explicitly flagged in-code (`// TODO: apply allowlist and rate-limiting here`), indicating it is currently reachable in production builds that route legacy `web_api_trigger` messages through this handler.

### Recommendation
Implement the allowlist/rate-limit check called out by the TODO before forwarding legacy WebAPI trigger messages to DON nodes — mirror the pattern already used in the vault (`Authorizer.AuthorizeRequest`) and confidential-relay handlers, verifying the extracted `msg.Body.Sender` against the workflow registry's allowlisted senders/workflow owners, and apply per-sender rate limiting, before any `don.SendToNode` calls in `HandleLegacyUserMessage`.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no prior registration or allowlisting needed).
2. Construct an `api.Message` with `Body.Method = "web_api_trigger"`, a fresh `MessageID`, valid `DonID`, and a current `Timestamp` in the trigger payload; sign it with the throwaway key via `Message.Sign`.
3. Submit the JSON-RPC-wrapped message to the gateway's public `/user` endpoint targeting the WebAPI service/DON.
4. Observe `gateway.ProcessRequest` → `handler.HandleLegacyUserMessage` accepts the message (passes `Validate()`, timestamp check) and calls `don.SendToNode` for every DON member, without any allowlist lookup, as shown in [5](#0-4) .

### Citations

**File:** core/services/gateway/gateway.go (L221-265)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L397-420)
```go
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
