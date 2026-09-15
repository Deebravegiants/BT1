Audit Report

## Title
Legacy gateway handler allows client-controlled MessageID collisions to overwrite another user's pending callback, causing cross-user response delivery - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` stores each incoming request's callback in `h.savedCallbacks` keyed solely by the client-supplied `msg.Body.MessageID`, with no check for an existing in-flight entry under that key and no binding of the map entry to the requester's identity. Since `MessageID` is fully attacker-controlled and only validated for length/format (not uniqueness) at the gateway ingress, a second requester who reuses a still-pending `MessageID` silently overwrites the first requester's callback, so the DON's eventual response for that ID is delivered to the second (attacker) callback while the original requester gets nothing (eventually a timeout).

## Finding Description
The gateway's HTTP entry point `ProcessRequest` in `core/services/gateway/gateway.go` decodes each incoming request, calls `msg.Validate()` (which only checks length/charset constraints on `MessageID`, not uniqueness), and then synchronously invokes `h.HandleLegacyUserMessage(ctx, msg, callback)`, blocking on `callback.Wait(ctx)` for the response. [1](#0-0) 

`Message.Validate` in `core/services/gateway/api/message.go` bounds-checks `MessageID` length and charset but performs no uniqueness or ownership check; `Sender` is derived only from the ECDSA signature over the message body (which includes the client-chosen `MessageID`), meaning two distinct, differently-keyed senders can independently and validly sign messages carrying the identical `MessageID` string. [2](#0-1) 

`HandleLegacyUserMessage` then unconditionally overwrites whatever is currently stored at that key: [3](#0-2) 

When a DON node later responds, `handleWebAPITriggerMessage` looks the callback up purely by `msg.Body.MessageID` and delivers the response to whichever callback is currently stored there — with no verification that the response actually belongs to the same requester who registered that callback: [4](#0-3) 

The only identity check performed on the response path (`HandleNodeMessage`) verifies that the *node* (`nodeAddr`) matches the message's claimed sender — it authenticates that the response genuinely came from an expected DON node, but says nothing about which original *user* request it should route back to: [5](#0-4) 

The same unguarded overwrite pattern is present in `handler.dummy.go`'s `HandleLegacyUserMessage`: [6](#0-5) 

By contrast, the newer JSON-RPC-based handlers (`vault`, `confidentialrelay`) explicitly reject a new request whose ID already exists in `activeRequests` before registering a callback, demonstrating the project's awareness of, and mitigation for, this exact class of collision in newer code paths — a mitigation absent from the legacy `capabilities` handler and `handler.dummy.go`. [7](#0-6) 

## Impact Explanation
This is a genuine logic flaw: `savedCallbacks` is keyed only by an attacker-controlled string with no collision guard and no binding to sender identity, in a code path reachable directly via unauthenticated (signature-only, not privilege-gated) HTTP requests to the gateway's user-facing port. If exploited, it causes cross-user response corruption — the original requester's in-flight request is silently dropped/overwritten and a different user's callback receives the DON's response for that `MessageID`, matching the "cross-user response corruption" impact class called out as in-scope.

## Likelihood Explanation
Exploitation requires only that an unprivileged client hold a valid ECDSA keypair (any workflow-owner-equivalent client can generate one; the check `msg.Validate()` only confirms *a* valid signature exists — it does not enforce that the signer possesses any special privilege) and that it send a competing request with the same `MessageID` while the victim's original request is still pending (the window is the round-trip time until the DON responds or the callback timeout elapses, which can be on the order of seconds). The attacker must know or guess the victim's `MessageID` — feasible if IDs are predictable, reused, or observed in transit/logs, though not guaranteed in all deployments. This makes the likelihood realistic but conditional on the specific ID-selection scheme used by legitimate clients, which was not verified in the code (the `MessageID` generation logic on the legitimate client side, e.g. `core/scripts/gateway/web_api_trigger/invoke_trigger.go`, was not fully inspected in this review, so the real-world predictability of concurrent legitimate `MessageID`s is not independently confirmed).

## Recommendation
Apply the same collision-rejection strategy used by `vault` and `confidentialrelay` handlers to the legacy path: before inserting into `savedCallbacks`, check whether an entry for that `MessageID` already exists and reject the new request, or scope the callback map key by `(Sender, MessageID)` rather than by `MessageID` alone, in `core/services/gateway/handlers/capabilities/handler.go`'s `HandleLegacyUserMessage` and in `core/services/gateway/handlers/handler.dummy.go`'s `HandleLegacyUserMessage`.

## Proof of Concept
1. User A sends a legacy `web_api_trigger` message with `Body.MessageID = "X"`, signed with key A; the gateway stores A's callback under `savedCallbacks["X"]` (`core/services/gateway/handlers/capabilities/handler.go:411-414`) and forwards the request to all DON members.
2. Before the DON responds, attacker B (using an independently-generated, unrelated key B) sends a second legacy message also using `Body.MessageID = "X"`; `msg.Validate()` passes (signature is internally consistent for B's own key), and the gateway overwrites `savedCallbacks["X"]` with B's callback.
3. A DON node responds for `MessageID = "X"` (destined for A's request); `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds B's entry, and delivers A's response payload to B (`core/services/gateway/handlers/capabilities/handler.go:148-162`).
4. User A's HTTP request blocks in `callback.Wait(ctx)` (`core/services/gateway/gateway.go:281`) until timeout, receiving a `RequestTimeoutError`, while B receives content intended for A.

A Go integration test against `core/services/gateway/handlers/capabilities/handler_test.go` (or `core/services/gateway/gateway_test.go`) can construct two signed `api.Message`s with distinct keys but identical `MessageID`, invoke `HandleLegacyUserMessage` for both in sequence before simulating the DON's `HandleNodeMessage` response, and assert that the response is delivered to the second caller's callback rather than the first.

### Citations

**File:** core/services/gateway/gateway.go (L253-279)
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
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L248-255)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	msg, err := common.ValidatedMessageFromResp(resp)
	if err != nil {
		return err
	}
	if msg.Body.Sender != nodeAddr {
		return errors.New("message sender mismatch when reading from node ")
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/handlers/handler.dummy.go (L62-66)
```go
func (d *dummyHandler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error {
	d.mu.Lock()
	d.savedCallbacks[msg.Body.MessageID] = &savedCallback{msg.Body.MessageID, callback}
	don := d.don
	d.mu.Unlock()
```

**File:** core/services/gateway/handlers/vault/handler.go (L457-463)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
```
