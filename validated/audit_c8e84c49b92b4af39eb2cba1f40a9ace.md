Based on my review of the code, this claim is well-supported by the actual source. Key verification points:

1. `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` performs an unconditional map write `h.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}` with no existence check, confirmed at [1](#0-0) .

2. `MessageID` is not server-generated — it originates from the caller-supplied JSON-RPC `id` field via `DecodeJSONRequest`, [2](#0-1)  and is passed straight through `gateway.ProcessRequest` [3](#0-2) .

3. Critically, `Message.Validate()` requires a valid ECDSA signature over the message body (including `MessageID`), [4](#0-3) , but this signature only proves the message came from whichever key signed it — it does **not** bind `MessageID` uniqueness to a specific signer. Any unprivileged actor can generate their own keypair, sign a message with an arbitrary `MessageID` matching a victim's in-flight request, and pass `Validate()`. The code even has an explicit `// TODO: apply allowlist and rate-limiting here` comment confirming no caller-authorization gate exists at this layer [5](#0-4) .

4. `handleWebAPITriggerMessage` resolves whichever callback is currently present under that `MessageID` and silently drops any duplicate/late response with no error surfaced, [6](#0-5) .

5. The asymmetry with the newer v2 handler is real — `setupCallback` explicitly rejects reused in-flight `requestID`s, [7](#0-6) , confirming the legacy path was not hardened the same way.

This gives an unprivileged, unauthenticated-relative-to-victim actor (any external caller who can sign their own arbitrary message) a concrete way to collide with another in-flight request's ID, causing either DoS (victim's `callback.Wait` times out per `core/services/gateway/gateway.go:281-288`) or cross-user response delivery, with no existing check preventing it.

Audit Report

## Title
Client-controlled `MessageID` collision in legacy WebAPI trigger gateway handler causes cross-user response hijack/DoS - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
`HandleLegacyUserMessage` keys the gateway's pending-request table `savedCallbacks` by the caller-supplied `MessageID` and overwrites any existing entry with no uniqueness or ownership check. Because message signature validation only authenticates the sender of a message, not the uniqueness of the `MessageID` value across senders, any unprivileged caller can choose a `MessageID` colliding with another party's in-flight request, causing that victim's request to time out and potentially causing the victim's DON response to be delivered to the attacker's callback instead.

## Finding Description
The public gateway endpoint decodes the JSON-RPC `id` field verbatim into `Message.Body.MessageID` (`core/services/gateway/api/jsonrpccodec.go:26-35`) and forwards it unmodified through `gateway.ProcessRequest` (`core/services/gateway/gateway.go:270-272`) into `handler.HandleLegacyUserMessage`. That function unconditionally stores `h.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}` (`core/services/gateway/handlers/capabilities/handler.go:411-414`) — silently overwriting any prior in-flight entry at that key. `Message.Validate()` requires a valid signature over the message body, but the signature proves only which key signed a given payload; it places no constraint tying `MessageID` to a specific, non-colliding signer, and the handler explicitly still has a `// TODO: apply allowlist and rate-limiting here` marker showing no caller-authorization/uniqueness gate exists (`core/services/gateway/handlers/capabilities/handler.go:384`). When a DON node later replies, `handleWebAPITriggerMessage` looks up and deletes whatever is currently stored under that `MessageID` and resolves it with the incoming payload, with no way to verify the response is addressed to its rightful requester (`core/services/gateway/handlers/capabilities/handler.go:148-162`). The identical unauthenticated-overwrite pattern exists in `handler.dummy.go`'s `HandleLegacyUserMessage`. By contrast, the newer v2 HTTP trigger handler's `setupCallback` explicitly rejects a request whose `requestID` is already in-flight (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:419-426`), confirming this is a real, unaddressed gap in the legacy code path rather than intentional design.

## Impact Explanation
An unprivileged external caller who chooses (or races to guess) a `MessageID` matching another legitimate in-flight request's ID can overwrite that victim's `savedCallbacks` entry. This causes either: (a) the victim's original request to never resolve, so `callback.Wait(ctx)` in `gateway.ProcessRequest` (`core/services/gateway/gateway.go:281-288`) times out — a denial of service for that specific request — or (b) the DON node's response intended for the victim being delivered to the attacker's callback instead, since `handleWebAPITriggerMessage` resolves whichever callback currently occupies the `MessageID` slot. This maps to the in-scope "gateway request impersonation / cross-user response corruption" impact class.

## Likelihood Explanation
The gateway's WebAPI-trigger endpoint is internet-facing and accepts requests from unprivileged callers who supply their own signing key and arbitrary `MessageID` value; nothing in `Message.Validate()` or `HandleLegacyUserMessage` prevents two independently-signed messages from different keys from sharing the same `MessageID`. Exploitation requires only observing or predicting another in-flight request's ID (e.g., via timing, sequential IDs, or logs) and is repeatable without any privilege escalation.

## Recommendation
- In `handler.go`'s `HandleLegacyUserMessage` (and `handler.dummy.go`'s equivalent), check for an existing entry in `savedCallbacks` before inserting, and reject the new request with a conflict error if the key is already in use — mirroring the guard in `http_trigger_handler.go`'s `setupCallback`.
- Namespace/derive the internal map key using something not fully controlled by an arbitrary external caller (e.g., combine the verified `Sender` address with the caller-supplied ID, or use a server-generated UUID for the internal callback key) so no unauthenticated identifier can collide with another party's in-flight request.

## Proof of Concept
1. Legitimate User A signs and sends a WebAPI trigger JSON-RPC request to the gateway's public HTTP endpoint with `id = "X"`. `HandleLegacyUserMessage` stores `savedCallbacks["X"] = callbackA` and forwards the message to all DON members.
2. Before User A's response returns, an unprivileged Attacker (using their own independent signing key) sends their own request to the same endpoint with the same `id = "X"`. `HandleLegacyUserMessage` unconditionally overwrites `savedCallbacks["X"] = callbackB` (no existing-key check, `handler.go:411-414`), and forwards the attacker's message to the DON.
3. A DON node responds to User A's original trigger with `MessageID = "X"`. `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `callbackB` (the attacker's), deletes the entry, and delivers User A's response payload to the Attacker.
4. User A's `callback.Wait(ctx)` in `gateway.ProcessRequest` never resolves and times out with `RequestTimeoutError`, while the Attacker receives a response payload not addressed to them. This can be reproduced as a Go unit test invoking `handler.HandleLegacyUserMessage` twice with the same `MessageID` from two different signers, then calling `handler.HandleNodeMessage`/`handleWebAPITriggerMessage` once and observing which callback resolves.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-384)
```go
	// TODO: apply allowlist and rate-limiting here
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/api/jsonrpccodec.go (L26-35)
```go
func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)
	if err != nil {
		return nil, err
	}
	msg.Body.MessageID = request.ID
	msg.Body.Method = request.Method
	return &msg, nil
}
```

**File:** core/services/gateway/gateway.go (L270-272)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-426)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
```
