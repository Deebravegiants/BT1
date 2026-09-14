## Analysis

The Ledger incident centers on a trust-boundary failure that let a party access data/requests belonging to someone else. The closest analog reachable from an unprivileged Chainlink client is in the legacy Web API Gateway handler: request/response correlation is keyed purely by a client-supplied `MessageID`, and the entry is written unconditionally, without checking whether that ID is already in-flight for a different (possibly unrelated) caller.

### Title
Unauthenticated MessageID collision in Gateway Web API handler causes cross-user response hijacking - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`HandleLegacyUserMessage` stores the caller's response callback in a shared map keyed solely by `msg.Body.MessageID`, a value fully controlled by the requesting client (it is part of the client-signed message body, not server-generated). The write is unconditional — it silently overwrites any existing entry for the same ID instead of rejecting duplicates. An unprivileged client can therefore pick a `MessageID` that collides with another in-flight request and hijack the eventual node response meant for that other caller.

### Finding Description
In `core/services/gateway/handlers/capabilities/handler.go`, `HandleLegacyUserMessage` does: [1](#0-0) 
which stores `callback` in `h.savedCallbacks` keyed by `msg.Body.MessageID` with no check for an existing entry.

`MessageID` is part of the client-signed `api.MessageBody`, chosen by the requester and only constrained by length/character rules in `Message.Validate()`: [2](#0-1) 
There is no requirement that it be unique to the caller, unpredictable, or bound to the caller's identity/sender key.

When a DON node later responds, `HandleNodeMessage` verifies only that the responding node address matches the message's sender field (i.e., that the *node* isn't spoofed), not that the response's `MessageID` still belongs to the caller who originally submitted it: [3](#0-2) 

The response is then dispatched purely by `MessageID` lookup and delivered to whichever callback is currently stored for that ID: [4](#0-3) 

Contrast this with the sibling implementations in the same codebase that explicitly guard against this exact class of bug by rejecting duplicate/in-flight IDs instead of overwriting: [5](#0-4) [6](#0-5) 

The legacy `handler.go` path lacks this protection, so it is the outlier.

### Impact Explanation
If User B submits a request with the same `MessageID` as User A's still-pending request (either by guessing/reusing a short-lived ID, or intentionally racing a known/predictable ID), User B's callback silently replaces User A's in `savedCallbacks`. When the DON node eventually responds to that `MessageID`, `handleWebAPITriggerMessage` delivers the response to whichever callback is currently stored — now User B's — sending User A's (the legitimate requester's) trigger response data to User B. This is a cross-user response confusion / information-disclosure bug reachable purely from unprivileged, external client input over the internet-facing gateway, structurally analogous to the Ledger case where one party's data became accessible to another party due to a broken access/identity boundary. User A additionally receives no response and eventually times out, a secondary availability impact.

### Likelihood Explanation
Exploitability depends on message-ID predictability/reuse across concurrent requests. `MessageID` values are entirely client-chosen, so any client that can predict or intentionally reuse another party's identifier under normal or automated (bot/script) traffic patterns can trigger the collision; no special privilege beyond being a normal external caller of the gateway's legacy Web API trigger endpoint is required. The bug is a straightforward missing existence-check compared to two other handlers in the same package that already implement the fix, indicating the gap is a genuine oversight rather than a deliberate design choice.

### Recommendation
In `HandleLegacyUserMessage`, before storing a new callback, check whether `h.savedCallbacks[msg.Body.MessageID]` already exists and reject the new request (mirroring the pattern used in `requestcache.go`'s `NewRequest` and `http_trigger_handler.go`'s `setupCallback`). Additionally consider binding the callback key to `(Sender, MessageID)` rather than `MessageID` alone, so that even accidental cross-client ID collisions cannot cause response misdelivery.

### Proof of Concept
1. User A signs and sends a legacy Web API trigger message with `MessageID = "X"`; the gateway forwards it to DON nodes and stores `savedCallbacks["X"] = callbackA`.
2. Before the node responds, User B signs and sends a message reusing `MessageID = "X"`; `HandleLegacyUserMessage` overwrites the map entry: `savedCallbacks["X"] = callbackB` (see `core/services/gateway/handlers/capabilities/handler.go:411-414`, no existence check).
3. A DON node responds for `MessageID = "X"` (bound to User A's original request). `HandleNodeMessage` validates only `msg.Body.Sender == nodeAddr` (`handler.go:253-255`), then `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `callbackB`, and sends User A's node response back to User B (`handler.go:148-161`).
4. User B receives data intended for User A; User A's request times out with no response delivered.

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
