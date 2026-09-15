All citations check out exactly against the actual code. The vulnerability is confirmed as described:

- `HandleLegacyUserMessage` writes to `h.savedCallbacks[msg.Body.MessageID]` unconditionally with no existence check [1](#0-0) .
- `MessageID` is fully client-controlled and only validated for length/format, not uniqueness or binding to sender [2](#0-1) .
- `HandleNodeMessage` only validates that the responding node's address matches `msg.Body.Sender` (the node identity), never that the `MessageID`'s current callback still belongs to the original requester [3](#0-2) .
- `handleWebAPITriggerMessage` dispatches the response purely by `MessageID` lookup to whatever callback is currently stored [4](#0-3) .
- Sibling implementations in the same package correctly guard against this by keying on `(Sender, MessageID)` and rejecting duplicates [5](#0-4) , or explicitly rejecting reused request IDs [6](#0-5) , confirming this is a genuine gap in the legacy handler rather than an intentional design choice.

This is a concrete, reachable-by-unprivileged-client bug: any external caller of the legacy Web API trigger gateway endpoint can supply an arbitrary `MessageID`, and if it collides with another in-flight caller's ID, the second caller's callback silently overwrites the first's, causing the node's response (intended for the first caller) to be delivered to the second caller. This matches the in-scope "cross-user response corruption" impact class.

Audit Report

## Title
Unauthenticated MessageID collision in Gateway Web API handler causes cross-user response hijacking - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`HandleLegacyUserMessage` stores the caller's response callback in `h.savedCallbacks`, keyed solely by the client-supplied `msg.Body.MessageID`, and writes it unconditionally without checking for an existing in-flight entry with the same ID. Because `MessageID` is fully client-chosen and only validated for length/format (not uniqueness or sender-binding), an unprivileged client that reuses or predicts another caller's in-flight `MessageID` can overwrite that caller's saved callback, causing the eventual DON node response to be delivered to the wrong client.

## Finding Description
In `core/services/gateway/handlers/capabilities/handler.go`, `HandleLegacyUserMessage` stores the callback with `h.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}` with no existence check (lines 411-414). `MessageID` is part of the client-signed `api.MessageBody` and is validated only for length and null-byte suffix in `Message.Validate()` (`core/services/gateway/api/message.go`, lines 54-66) — there is no uniqueness or sender-binding requirement. When a DON node later responds, `HandleNodeMessage` (lines 248-255) verifies only that `msg.Body.Sender == nodeAddr`, i.e., that the responding node isn't spoofed — it does not verify that the callback currently associated with that `MessageID` still belongs to the original requester. `handleWebAPITriggerMessage` (lines 148-161) then looks up and delivers the response purely by `MessageID`, to whichever callback is currently stored. Sibling implementations in the same package (`requestcache.go`'s `NewRequest`, keyed by `(Sender, MessageID)` with explicit duplicate rejection, and `http_trigger_handler.go`'s `setupCallback`, which rejects reused `requestID`s) demonstrate that this exact class of collision is a known risk that the legacy handler fails to guard against.

## Impact Explanation
If a second caller submits a request reusing an in-flight `MessageID`, their callback silently replaces the original caller's entry. When the node responds for that `MessageID`, the response — containing data intended for the original requester — is delivered to the second caller instead, while the original caller's request times out with no response. This is a cross-user response corruption/information-disclosure bug reachable from unprivileged, external client input on the internet-facing gateway's legacy Web API trigger endpoint, falling under the in-scope "cross-user response corruption" impact category.

## Likelihood Explanation
No privilege beyond being a normal external caller of the gateway's legacy Web API trigger endpoint is required. Exploitability depends only on colliding `MessageID` values across concurrent in-flight requests, which is entirely within an unprivileged client's control since `MessageID` is client-chosen and unauthenticated with respect to uniqueness. The presence of duplicate-rejection logic in two sibling handlers in the same codebase, but not in this legacy path, indicates this is a genuine oversight.

## Recommendation
In `HandleLegacyUserMessage`, check whether `h.savedCallbacks[msg.Body.MessageID]` already exists before writing, and reject the new request if so (mirroring `requestcache.go`'s `NewRequest` and `http_trigger_handler.go`'s `setupCallback`). Additionally, key the callback map by `(Sender, MessageID)` instead of `MessageID` alone so that accidental cross-client ID collisions cannot cause response misdelivery.

## Proof of Concept
1. User A sends a legacy Web API trigger message with `MessageID = "X"`; gateway forwards to DON nodes and sets `savedCallbacks["X"] = callbackA` (`handler.go:411-414`).
2. Before the node responds, User B sends a message reusing `MessageID = "X"`; `HandleLegacyUserMessage` overwrites: `savedCallbacks["X"] = callbackB` (no existence check).
3. A DON node responds for `MessageID = "X"`. `HandleNodeMessage` validates only `msg.Body.Sender == nodeAddr` (`handler.go:253-255`), then `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `callbackB`, and delivers User A's node response to User B (`handler.go:148-161`).
4. User B receives data intended for User A; User A's request times out with no response delivered.

A Go integration test can be written against `handler_test.go` in the same package: call `HandleLegacyUserMessage` twice with the same `MessageID` but distinct callbacks/callback-tracking channels, then invoke `HandleNodeMessage` with a node response for that `MessageID`, and assert which callback channel receives the response.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-161)
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

**File:** core/services/gateway/api/message.go (L54-66)
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
```

**File:** core/services/gateway/handlers/common/requestcache.go (L57-63)
```go
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
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
