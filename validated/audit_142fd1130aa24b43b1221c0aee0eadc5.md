This confirms the analog: `ProcessRequest` in `gateway.go` accepts a fully client-supplied JSON-RPC `ID` (bounded only to 200 chars) directly from an unauthenticated internet-facing user request and forwards it unchanged as `msg.Body.MessageID` into `HandleLegacyUserMessage` [1](#0-0) , which is signature-validated but not bound to the sender in the saved-callback map, and is stored keyed only by that attacker-controlled ID [2](#0-1) . The `handleWebAPITriggerMessage` function that later delivers the DON node's response looks the callback up purely by `MessageID`, with no check that the response's originating request came from the same sender that is expected to receive it [3](#0-2) . Additionally, the code explicitly documents that per-request allowlist and rate-limiting are not yet applied at this layer (`// TODO: apply allowlist and rate-limiting here`) [4](#0-3) .

### Title
Cross-user response hijacking via attacker-controlled MessageID collision in Gateway WebAPI trigger handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Gateway's legacy WebAPI trigger flow keys pending user callbacks solely by a client-supplied `MessageID`/JSON-RPC `ID` with no binding to the requester's identity. An unprivileged internet-facing user can submit a `web_api_trigger` request using the same `MessageID` as another in-flight legitimate request, silently overwriting that user's saved callback. When the DON node later replies with that `MessageID`, the response is delivered to whichever callback is currently stored in the map — potentially the attacker's — leading to cross-user response confusion/hijacking and denial of the legitimate response, analogous to the Vault `setHooks` issue where an unvalidated, attacker-influenced hook/callback path let one party intercept effects intended for another and disrupt the intended response flow.

### Finding Description
`ProcessRequest` decodes the raw JSON-RPC request and takes the `ID` field directly from the untrusted HTTP body, only capping its length at 200 characters, with no uniqueness or ownership check [1](#0-0) . This value becomes `msg.Body.MessageID` and is passed into `HandleLegacyUserMessage`, which stores the caller's `Callback` in the shared `h.savedCallbacks` map keyed only by this ID: `h.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}` [2](#0-1) . The signature check in `Message.Validate()` only proves the message was signed by *some* valid key belonging to the sender of that particular message — it does not prevent two different senders from independently choosing an identical `MessageID` value, since `MessageID` is arbitrary attacker-chosen data that is itself part of what gets signed [5](#0-4) .

When a DON node later responds to a `web_api_trigger` request, `handleWebAPITriggerMessage` looks the callback up strictly by `msg.Body.MessageID` (no re-validation that the response corresponds to the same original sender who is expected to receive it) and immediately delivers it: `savedCb, found := h.savedCallbacks[msg.Body.MessageID]` then `savedCb.SendResponse(...)` [3](#0-2) . If an attacker submits a colliding-ID request after a victim's request has been dispatched to the DON but before the node's reply arrives (window bounded by `CallbackMaxAgeSec`, defaulting to 120 seconds) [6](#0-5) , the attacker's callback silently replaces the victim's entry in the map. The eventual node response — intended for the victim — is then delivered to the attacker instead, and the victim's HTTP request hangs until `RequestTimeoutError` in `gateway.go`'s `callback.Wait(ctx)` [7](#0-6) . The code itself flags that allowlist/rate-limit enforcement for this exact handler path is not implemented (`// TODO: apply allowlist and rate-limiting here`) [4](#0-3) , so there is no mitigating control preventing a malicious client from freely submitting many colliding-ID requests.

### Impact Explanation
This enables an unprivileged, unauthenticated internet client to hijack another user's WebAPI trigger response — potentially disclosing the victim's workflow execution result to the attacker (cross-user response confusion / information exposure) — and simultaneously causes a denial-of-service against the legitimate caller, whose request will time out. Since `web_api_trigger` results can carry workflow-specific data intended only for the triggering caller, this is a concrete authentication/authorization confusion at the response-routing layer, not merely a resource-exhaustion nuisance.

### Likelihood Explanation
Exploitability depends on the attacker either predicting/guessing a victim's `MessageID` or on the calling convention producing low-entropy or attacker-observable IDs (e.g., if a client or integration reuses fixed/sequential/short IDs, this is trivial). Given the ID is fully client-supplied with no server-side randomness/nonce enforcement and the collision window is up to 120 seconds by default, an attacker who can predict or replay a known ID pattern used by a target integration has a straightforward, low-cost path to trigger the collision. I could not verify from the indexed code how MessageIDs are generated on the calling client side (e.g., whether callers use cryptographically random IDs), which affects how easily a real-world ID collision could be engineered; if callers reliably use high-entropy random IDs, practical exploitation is significantly harder.

### Recommendation
Bind the saved-callback map to both `MessageID` and the authenticated sender identity (derived from the verified signature), rejecting or namespacing a new registration if a callback for that `(MessageID)` already exists and belongs to a different sender. Additionally, implement the still-outstanding TODO for allowlist and rate-limiting enforcement in `HandleLegacyUserMessage`, and consider generating/mixing in a server-side nonce or requiring a minimum entropy for `MessageID`.

### Proof of Concept
1. Victim submits a valid, signed `web_api_trigger` JSON-RPC request to the Gateway's user-facing HTTP endpoint with `ID = "shared-id"`; `ProcessRequest` → `HandleLegacyUserMessage` stores the victim's callback in `h.savedCallbacks["shared-id"]` and forwards the request to DON nodes [8](#0-7) .
2. Before the DON node replies, an attacker (no special privileges, just internet access to the Gateway) submits their own valid, self-signed `web_api_trigger` request also using `ID = "shared-id"`. Because `Message.Validate()` only checks that the signature matches the message contents (which the attacker controls entirely for their own message), this passes validation and `h.savedCallbacks["shared-id"]` is overwritten with the attacker's callback [2](#0-1) , [5](#0-4) .
3. When the DON node responds with `MessageID = "shared-id"`, `handleWebAPITriggerMessage` looks up `h.savedCallbacks["shared-id"]`, finds the attacker's callback, and delivers the victim's workflow response to the attacker [3](#0-2) .
4. The victim's original HTTP request never receives a response and eventually times out via `callback.Wait(ctx)` in `gateway.go` [7](#0-6) .

### Citations

**File:** core/services/gateway/gateway.go (L221-234)
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
```

**File:** core/services/gateway/gateway.go (L281-288)
```go
	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
```

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-385)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
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
