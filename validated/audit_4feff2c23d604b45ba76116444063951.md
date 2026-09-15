Audit Report

## Title
Cross-user response hijacking via attacker-controlled MessageID collision in the WebAPI capabilities gateway handler - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
The gateway's `handler.savedCallbacks` map, keyed solely by the caller-supplied JSON-RPC `ID` (propagated to `msg.Body.MessageID`), is written without any duplicate-key check in `HandleLegacyUserMessage`, and read/deleted purely by that same key in `handleWebAPITriggerMessage`. Any unprivileged external caller reaching the user-facing gateway endpoint can choose an `ID` that collides with another concurrent caller's in-flight `ID`, silently overwriting that caller's `Callback` entry so that the DON's eventual response to the *original* request is delivered to the *second* caller instead.

## Finding Description
`gateway.ProcessRequest` decodes the request and, for legacy DON-addressed requests, calls `msg.Validate()` and sets `msg.Body.MessageID = req.ID` via `ValidatedMessageFromReq`, then invokes `h.HandleLegacyUserMessage(ctx, msg, callback)` with a fresh per-request `callback` object. [1](#0-0) [2](#0-1) 

`HandleLegacyUserMessage` then stores that callback in the shared `h.savedCallbacks` map keyed purely by `msg.Body.MessageID`, with no check for an existing entry under the same key: [3](#0-2) 

When a DON node later responds with `MessageID = "X"`, `handleWebAPITriggerMessage` looks the callback up purely by that ID, delivers the response to whichever `Callback` currently occupies the slot, and deletes it: [4](#0-3) 

`Message.Validate()` and `ExtractSigner()` verify the message signature only to authenticate the *sender* (populating `m.Body.Sender`) — they do not enforce uniqueness or ownership of `MessageID`, and `MessageID` is not part of any per-connection scoping: [5](#0-4) 

The only length/format constraints on `MessageID` are the 128/200-char limits and the null-suffix check; nothing prevents two unrelated, differently-signed messages from sharing the same `MessageID`: [6](#0-5) [7](#0-6) 

By contrast, the outgoing-connector code path explicitly guards against duplicate IDs via `c.responses.new(messageID)`, confirming the maintainers are aware of this bug class elsewhere in the codebase, but no equivalent guard exists on the `savedCallbacks` map in the WebAPI capabilities handler (or its `handler.dummy.go` sibling, which grep confirms uses the identical unguarded pattern). [8](#0-7) 

Exploit flow: (1) Attacker A sends a `web_api_trigger` request with `ID = "X"`, gateway stores `savedCallbacks["X"] = CallbackA` and forwards to all DON members; (2) before the DON responds, User B sends another `web_api_trigger` with the same `ID = "X"`, overwriting `savedCallbacks["X"] = CallbackB`; (3) the DON's response to A's original message (still tagged `MessageID = "X"`) is looked up, found as `CallbackB`, and delivered to B instead of A — a cross-user response confusion requiring no node compromise, no signature forgery, and no privileged access.

## Impact Explanation
This maps to the in-scope "cross-user response corruption" impact category: an unprivileged external caller can cause another caller's DON-produced trigger-response payload to be delivered to itself, and can cause a victim's own request to silently vanish (its callback slot reassigned, so no response ever reaches it before the 120s callback TTL expires). The impact is real and directly caused by the reviewed code path — there is no reliance on a malicious node, peer, or dependency; it is purely a consequence of the shared, unpartitioned `savedCallbacks` map keyed by attacker-controlled data.

## Likelihood Explanation
Exploitation requires only: (1) guessing or choosing a `MessageID` that collides with another in-flight request (trivial if an attacker picks a short/common value like `"1"` and races a low-traffic gateway, since no server-side entropy is injected into the key), and (2) sending two overlapping `web_api_trigger` requests to the same gateway instance within the 120-second default callback TTL. No authentication bypass, no node compromise, and no cryptographic break are needed. This is reachable from the internet-facing user-server endpoint by any unprivileged caller.

## Recommendation
- Reject the request if `MessageID` already exists in `savedCallbacks` (mirroring the `responses.new(messageID)` duplicate-detection pattern in `OutgoingConnectorHandler`), or scope the map key to include a server-generated nonce / per-connection identifier in addition to the caller-supplied `MessageID`.
- Apply the identical fix to `core/services/gateway/handlers/handler.dummy.go`'s `HandleLegacyUserMessage`, which has the same unguarded pattern.
- Avoid using the raw client-supplied JSON-RPC `ID` as the sole cross-goroutine response-routing key; derive it server-side or combine it with sender identity/connection state.

## Proof of Concept
1. Start a gateway with the `web-api-capabilities` handler configured for a DON.
2. Client A sends `{"jsonrpc":"2.0","id":"X","method":"web_api_trigger","params":{...donID, signature, payloadA...}}` to the user-server endpoint; gateway stores `savedCallbacks["X"] = CallbackA` per `HandleLegacyUserMessage` (handler.go:411-420) and forwards to all DON members.
3. Before the DON responds, Client B sends `{"jsonrpc":"2.0","id":"X","method":"web_api_trigger","params":{...different signer, payloadB...}}`, causing `savedCallbacks["X"]` to be overwritten with `CallbackB`.
4. When the DON node responds to A's original forwarded message (still carrying `MessageID = "X"`), `handleWebAPITriggerMessage` (handler.go:148-162) looks up `savedCallbacks["X"]`, finds `CallbackB`, deletes the entry, and delivers A's DON-originated response data to B — verifiable via a Go unit test asserting `CallbackB.SendResponse` is invoked with A's response payload while `CallbackA.Wait` times out.

### Citations

**File:** core/services/gateway/gateway.go (L231-234)
```go
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
```

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

**File:** core/services/gateway/handlers/common/message_util.go (L34-58)
```go
// ValidatedMessageFromReq validated and extracts a legacy Gateway Message
// from params field of JSON-RPC request
func ValidatedMessageFromReq(req *jsonrpc.Request[json.RawMessage]) (*api.Message, error) {
	if req.Version != "2.0" {
		return nil, errors.New("incorrect jsonrpc version")
	}
	if req.Method == "" {
		return nil, errors.New("empty method field")
	}
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
	var m api.Message
	err := json.Unmarshal(*req.Params, &m)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal request params: %w", err)
	}
	m.Body.Method = req.Method
	m.Body.MessageID = req.ID
	err = m.Validate()
	if err != nil {
		return nil, err
	}
	return &m, nil
}
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

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L136-140)
```go
	ch, err := c.responses.new(messageID)
	if err != nil {
		return nil, fmt.Errorf("duplicate message received for ID: %s", messageID)
	}
	defer c.responses.cleanup(messageID)
```
