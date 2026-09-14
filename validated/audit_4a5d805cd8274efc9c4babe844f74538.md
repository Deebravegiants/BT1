## Analog Bug Found

### Title
Missing allowlist/rate-limiting enforcement on gateway legacy trigger messages allows unauthorized WebAPI trigger requests to reach the DON - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The `SimpleInterestTermsContract.registerRepayment` bug class is: a function receives a caller-supplied parameter that is supposed to be checked against an expected value, but the validation is missing/incomplete, so the call is silently accepted and processed as if it were valid. The direct analog in this repository is `handler.HandleLegacyUserMessage` in the gateway's capabilities handler, which processes internet-facing "web_api_trigger" requests and explicitly documents — via a `TODO` comment — that allowlist and rate-limiting checks on the caller are not applied before forwarding the request to every DON node member.

### Finding Description
`HandleLegacyUserMessage` is the entry point the gateway uses (via `gateway.ProcessRequest`) to handle unauthenticated, internet-facing legacy requests targeting a DON [1](#0-0) . It performs payload decoding, staleness checks (`payload.Timestamp`), and method-name validation, but the code explicitly states:

```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [2](#0-1) 

No allowlist check against `msg.Body.Sender` (the caller-supplied, self-reported field populated only from the request's cryptographic signature, see `Message.Validate` [3](#0-2) ) is performed before the request is forwarded. After passing the staleness/method checks, the handler unconditionally sends the message to every member of the target DON:

```go
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [4](#0-3) 

This mirrors the reported bug pattern precisely: the system has the concept of an expected/authorized caller set (an allowlist), the code path that should enforce it exists (or is intended to exist), but the enforcement is missing, so the "wrong" (unauthorized) caller is silently accepted and its request is processed identically to an authorized one — just as `registerRepayment` silently accepted the wrong token instead of rejecting it.

### Impact Explanation
Any unprivileged, internet-facing client that can reach the gateway's `ProcessRequest` endpoint [5](#0-4)  and produce a validly-signed `api.Message` (which only requires generating an ECDSA keypair — no membership in any DON or capability owner allowlist is required) can trigger a `web_api_trigger` request that is broadcast to every node in the target DON. Since the trigger is fanned out to all DON members and later matched to a saved callback by `MessageID` [6](#0-5) , this allows an unauthorized actor to invoke DON-side webhook/trigger capability processing that should be restricted to allowlisted senders/workflows, potentially triggering downstream workflow runs or capability executions without authorization.

### Likelihood Explanation
This is reachable by any unprivileged external HTTP client since `ProcessRequest` is the gateway's public entrypoint and the missing check is unconditional (not gated behind any feature flag), and the offending code path is explicitly marked with `TODO: apply allowlist and rate-limiting here`, confirming the check is known to be absent rather than intentionally omitted for a benign reason.

### Recommendation
Enforce an allowlist check on `msg.Body.Sender` (and apply rate-limiting) in `HandleLegacyUserMessage` before forwarding the request to DON members, rejecting (not silently accepting) messages from senders not present in the DON's/capability's configured allowlist — analogous to how `registerRepayment` was fixed to reject repayments in the wrong token instead of silently ignoring the mismatch.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration or allowlisting required).
2. Construct an `api.Message` with `Body.Method = "web_api_trigger"`, a valid `Body.DonID` matching a target DON, and a `TriggerRequestPayload` with a current `Timestamp`; sign it with the arbitrary key (`msg.Sign(privateKey)`), producing a `Body.Sender` derived from that key per `Message.Validate` [7](#0-6) .
3. Submit the signed legacy request to the gateway's `ProcessRequest` HTTP endpoint.
4. Observe that `HandleLegacyUserMessage` passes the payload/staleness/method checks and forwards the trigger request to every member of the target DON [8](#0-7) , despite the sender never having been checked against any allowlist.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-162)
```go
func (h *handler) handleWebAPITriggerMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.mu.Lock()
	savedCb, found := h.savedCallbacks[msg.Body.MessageID]
	delete(h.savedCallbacks, msg.Body.MessageID)
	h.mu.Unlock()

	if found {
		// Send first response from a node back to the user, ignore any other ones.
		// TODO: in practice, we should wait for at least 2F+1 nodes to respond and then return an aggregated response
		// back to the user.
		codec := api.JSONRPCCodec{}
		return savedCb.SendResponse(handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError})
	}
	return nil
}
```

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

**File:** core/services/gateway/gateway.go (L220-265)
```go
// Called by the server
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
