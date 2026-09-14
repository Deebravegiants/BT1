### Title
Unprivileged gateway users can overwrite another in-flight request's callback via MessageID collision, causing DoS and cross-user response confusion - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The external report describes a "push" pattern where an external interaction is inlined into a critical state update, letting an unprivileged actor trigger failures/overwrites that block or corrupt processing for other users. The internet-facing Chainlink Gateway has an analogous pattern: `HandleLegacyUserMessage` stores a pending request's response callback in a shared map keyed only by an attacker-controlled `MessageID`, with no check for an existing/in-flight entry before overwriting it.

### Finding Description
`HandleLegacyUserMessage` unconditionally writes into the shared `savedCallbacks` map keyed by `msg.Body.MessageID`, without checking whether an entry for that ID is already in-flight: [1](#0-0) 

`MessageID` is a client-supplied field of `api.Message.Body`, validated only for length/format (non-empty, ≤128 bytes, no trailing null byte) — it is never required to be unique across different senders, nor namespaced to the sender's identity: [2](#0-1) 

When a node eventually replies, the handler looks up the saved callback purely by `MessageID` and delivers the response to whatever callback currently occupies that map slot, then deletes it: [3](#0-2) 

Because two different signed messages (from two different, unrelated users) can carry the same `MessageID` string (only the signature differs), an attacker can submit a request choosing the same `MessageID` as an in-flight legitimate request. This overwrites the legitimate caller's saved callback with the attacker's own, so:
- The legitimate user's request is silently orphaned (their callback is dropped from the map and never invoked, sitting until an external timeout) — a Denial of Service.
- The attacker's callback instead receives the DON's response intended for the other user's request — cross-user response confusion.

This is exactly analogous to the report's core theme: an unprivileged party can interfere with a shared, mutable per-request resource maintained by a "push"-style handler and used by the platform's most exposed (internet-facing) surface, causing blocking/DoS of another party's flow.

Notably, the codebase's own newer gateway handlers recognize and mitigate this exact class of bug: the v2 HTTP trigger handler explicitly checks for a duplicate/in-flight `requestID` before saving a callback and rejects the collision with `ErrConflict`: [4](#0-3) 

and the Vault gateway handler namespaces the ID with the requester's `owner` address specifically to avoid ID collisions across users (`owner + RequestIDSeparator + requestID`), as seen in its tests. The legacy `HandleLegacyUserMessage` path in `core/services/gateway/handlers/capabilities/handler.go` lacks both protections, indicating this is a real gap rather than an accepted design tradeoff.

### Impact Explanation
An unauthenticated/unprivileged client interacting with the gateway's legacy web API trigger path can:
1. Deny service to another concurrent requester by hijacking their `MessageID` slot (their request never completes, timing out from their perspective).
2. Receive a response payload that was destined for a different user's request (cross-user response confusion / potential information disclosure depending on payload sensitivity).

This directly matches the accepted categories: "cross-user response confusion" and unauthorized interference reachable from an unprivileged client via the gateway (message envelopes / handlers / caches).

### Likelihood Explanation
Likelihood is high for any deployment where multiple concurrent legacy trigger requests can be in flight and `MessageID` is fully client-controlled (as confirmed by `Validate()` only checking length/format, not uniqueness or binding to sender). No special privileges are required — merely valid signing capability to produce a well-formed signed `Message`, which is the same requirement as any legitimate caller of this endpoint. The race window is bounded by DON round-trip time, which is realistic to win with automated flooding.

### Recommendation
- Key `savedCallbacks` by a composite value that binds the `MessageID` to the sender's identity (e.g., `sender + separator + MessageID`), mirroring the Vault handler's `owner + RequestIDSeparator + requestID` pattern.
- Before inserting into `savedCallbacks` in `HandleLegacyUserMessage`, check for an existing (non-expired) entry for that key and reject the request with a conflict error, mirroring `httpTriggerHandler.setupCallback`'s duplicate-ID check.
- Consider enforcing `MessageID` uniqueness/idempotency at the transport layer before it reaches per-handler state.

### Proof of Concept
1. Legitimate user A submits a signed `api.Message` with `Body.MessageID = "X"` to a webhook/web-api-trigger endpoint served by `HandleLegacyUserMessage`; the handler stores A's callback under key `"X"` and forwards the request to DON members (handler.go:411-419).
2. Before the DON responds, attacker B — using their own valid signing key — submits a different signed message also with `Body.MessageID = "X"` (allowed because `Validate()` never checks for uniqueness across senders). The handler overwrites `savedCallbacks["X"]` with B's callback (handler.go:412).
3. When the DON responds with `resp.ID == "X"` (matching A's original forwarded request), `HandleNodeMessage`/`handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds B's callback, and delivers the response meant for A to B (handler.go:148-162).
4. A's original callback is now orphaned; A never receives a response (DoS), while B has received a response for a request they did not originate (cross-user response confusion).

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

**File:** core/services/gateway/api/message.go (L42-66)
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
