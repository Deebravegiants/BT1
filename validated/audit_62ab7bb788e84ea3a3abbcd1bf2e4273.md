### Title
Attacker-chosen `MessageID` collision overwrites another user's pending gateway callback, causing cross-user response delivery - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`HandleLegacyUserMessage` stores a user's response `callback` in a shared `savedCallbacks` map keyed solely by the attacker/client-controlled `msg.Body.MessageID`, with no check for an existing entry. Any unprivileged caller of the Gateway's user-facing HTTP endpoint can submit a signed message with a `MessageID` matching one currently in-flight from a different user, silently overwriting that user's saved callback. When a DON node later responds with that `MessageID`, `handleWebAPITriggerMessage` looks up the (now-attacker-owned) callback and delivers the victim's on-chain/workflow response to the attacker instead of the original requester.

### Finding Description
`HandleLegacyUserMessage` unconditionally assigns to the map without checking for a pre-existing key: [1](#0-0) 

`MessageID` is a plain client-supplied field in the signed message body, bounded only by length, and is not derived from the sender's address or any server-generated nonce — different senders can freely choose the same value: [2](#0-1) [3](#0-2) 

When a matching response arrives from a DON member, the handler looks up and deletes the saved callback purely by `MessageID` and delivers the response to whichever callback is currently stored there: [4](#0-3) 

The outer `gateway.ProcessRequest` flow confirms this is reachable directly from an unprivileged, unauthenticated-by-role HTTP client: it decodes the raw request, calls `HandleLegacyUserMessage`, and then blocks on `callback.Wait(ctx)` for the result: [5](#0-4) 

Exploit sequence:
1. Victim submits a legitimate `web_api_trigger` request with `MessageID = "X"`; the gateway saves `victimCallback` under key `"X"` and fans the request out to all DON members.
2. Before a DON node responds, attacker submits their own signed message reusing `MessageID = "X"` (attacker only needs their own valid signature over their own message — no knowledge of the victim's data is required, since the check is a pure map write keyed by the value they control). This overwrites `savedCallbacks["X"]` with `attackerCallback`.
3. When a DON node responds to the *victim's* original outgoing request (same `MessageID = "X"`, since the ID is carried through unchanged), `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `attackerCallback`, deletes the entry, and calls `attackerCallback.SendResponse(...)` with the victim's response payload.
4. The attacker's HTTP request (still blocked in `callback.Wait`) receives the victim's data. The victim's original HTTP request instead times out/never resolves (eventually reaped or hangs until context/HTTP timeout).

This is a direct instance of the reported bug class — one actor's action (their own request submission, analogous to funding a malicious token) corrupts shared state relied upon by another actor's in-flight "claim" (here, the response-delivery path), causing cross-user response confusion/blocking, unlike newer handlers (`vault`, `confidentialrelay`, `capabilities/v2`) which key active requests using the same pattern but where this legacy path lacks any existing-key guard.

### Impact Explanation
This allows an unprivileged client to hijack another user's response from the DON (potential disclosure of the victim's trigger response payload to the attacker) and to deny/delay the victim's response delivery — a concrete cross-user response confusion, matching the accepted bug categories for this analog scan (unauthorized cross-user response delivery). Depending on what payload data flows through `web_api_trigger` responses (e.g., data intended only for the requesting workflow/owner), this can leak response content to an unrelated party.

### Likelihood Explanation
Likelihood is high for an active attacker: `MessageID` collision requires no privilege beyond being able to sign a message with any private key (self-signed, no special role) and knowledge/guessing of an in-flight `MessageID`. Since `MessageID`s are often predictable/sequential or reused by legitimate client SDKs (and there is no server-side uniqueness enforcement or sender-scoping of the key), a race window between step 1 and step 3 is realistically exploitable, especially given the fan-out to potentially slow-to-respond DON nodes.

### Recommendation
Scope `savedCallbacks` keys by a tuple that includes the sender/signer address in addition to `MessageID` (e.g., `sender+":"+MessageID`), or reject/overwrite-guard `HandleLegacyUserMessage` when an active `MessageID` entry already exists (returning a conflict error, similar to the `activeRequests` existing-ID guard used in `confidentialrelay`/`vault` handlers). Additionally, validate that `handleWebAPITriggerMessage`'s node response actually corresponds to the same requester before dispatching the callback.

### Proof of Concept
1. Start two HTTP requests to the Gateway user port targeting the `capabilities` legacy handler:
   - Request A (victim): valid signed `api.Message` with `Body.MessageID = "collide-1"`, `Method = MethodWebAPITrigger`.
   - Request B (attacker): a different valid signed `api.Message` (attacker's own key) with `Body.MessageID = "collide-1"` too, sent shortly after A but before any DON node has replied to A.
2. Gateway processes A: `HandleLegacyUserMessage` stores `savedCallbacks["collide-1"] = victimCallback` and fans out to DON members.
3. Gateway processes B: `HandleLegacyUserMessage` overwrites `savedCallbacks["collide-1"] = attackerCallback` (no existing-key check) and fans out its own request.
4. A DON node eventually sends a `web_api_trigger` response for the original `MessageID = "collide-1"` (from processing request A's fan-out). `HandleNodeMessage` → `handleWebAPITriggerMessage` retrieves `savedCallbacks["collide-1"]`, which is now `attackerCallback`, and calls `attackerCallback.SendResponse(...)` with the victim's response data.
5. Attacker's blocked HTTP request (B) returns with the victim's data; victim's HTTP request (A) never resolves via this path and eventually times out.

This can be directly reproduced/extended from the existing test harness in `core/services/gateway/handlers/capabilities/handler_test.go` (`TestHandlerReceiveHTTPMessageFromClient`), by issuing two `HandleLegacyUserMessage` calls with distinct callbacks but identical `MessageID`s and observing which callback receives the node's response. [6](#0-5)

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/api/message.go (L42-52)
```go
type MessageBody struct {
	MessageID string `json:"message_id"`
	Method    string `json:"method"`
	DonID     string `json:"don_id"`
	Receiver  string `json:"receiver"`
	// Service-specific payload, decoded inside the Handler.
	Payload json.RawMessage `json:"payload,omitempty"`

	// Fields only used locally for convenience. Not serialized.
	Sender string `json:"-"`
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

**File:** core/services/gateway/gateway.go (L267-288)
```go
	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}

	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
	}
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L236-265)
```go
func TestHandlerReceiveHTTPMessageFromClient(t *testing.T) {
	handler, _, don, nodes := setupHandler(t)
	ctx := t.Context()
	msg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "", "")
	codec := api.JSONRPCCodec{}

	t.Run("happy case", func(t *testing.T) {
		// sends to 2 dons
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			nodeReq := nodeRequest(msg)
			require.Equal(t, nodeReq, args.Get(2))
		}).Return(nil).Once()
		don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			nodeReq := nodeRequest(msg)
			require.Equal(t, nodeReq, args.Get(2))
		}).Return(nil).Once()

		cb := hc.NewCallback()
		err := handler.HandleLegacyUserMessage(ctx, msg, cb)
		require.NoError(t, err)

		resp, err := hc.ValidatedResponseFromMessage(msg)
		require.NoError(t, err)
		err = handler.HandleNodeMessage(ctx, resp, nodes[0].Address)
		require.NoError(t, err)

		r, err := cb.Wait(t.Context())
		require.NoError(t, err)
		require.Equal(t, handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError}, r)
	})
```
