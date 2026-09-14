Confirmed: `MessageID` is a fully user-controlled, arbitrary string field validated only for length/format (`core/services/gateway/api/message.go` `Message.Validate()`), not for uniqueness or ownership binding, and the legacy user-message path stores callbacks keyed solely by this attacker-chosen ID.

### Title
Unscoped, user-controlled MessageID in gateway legacy handler allows cross-user callback hijack / response confusion - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy capabilities handler (`handler.HandleLegacyUserMessage`) saves each pending user request's callback in a shared map keyed only by the client-supplied `msg.Body.MessageID`, with no binding to the requesting client/session. Because the ID is fully attacker-controlled and only length/format-validated, an unprivileged client can submit a request using the same `MessageID` as another user's in-flight request. This mirrors the reported bug class ("execution reaches an attacker-controlled address because identity/allowlist checks are missing mid-flow") — here, the missing check is that saved callbacks are not scoped to the request's origin, so a colliding ID lets one client's response routing be overwritten by another's.

### Finding Description
`Message.Validate()` only checks that `MessageID` is non-empty, ≤128 bytes, and doesn't end in a null char [1](#0-0) . It is not derived from any per-session/per-user secret or nonce tied to the caller.

In `HandleLegacyUserMessage`, the handler stores the callback for the *current* request directly into the shared `savedCallbacks` map using this attacker-chosen key, unconditionally overwriting whatever was previously stored under that key: [2](#0-1) 

When a DON node later responds with `MethodWebAPITrigger` and that same `MessageID`, the handler looks the ID up, deletes it, and delivers the stored response to whichever callback is currently registered under that key: [3](#0-2) 

There is no check that the callback being resolved actually belongs to the caller who is being served, nor is there a check that a `MessageID` isn't already in use by another party before insertion. If an attacker submits a request with the same `MessageID` a victim already used (or is about to use) for a pending trigger, the attacker's callback becomes registered under that key. Any node response destined for the victim's original request that arrives after the overwrite is delivered to the attacker instead of the victim (cross-user response confusion), or vice versa depending on timing.

### Impact Explanation
An unprivileged client could intercept another client's workflow-trigger response by colliding `MessageID` values, since the callback map provides no per-caller isolation. This is a concrete cross-user response confusion primitive reachable directly from the internet-facing gateway endpoint via ordinary unauthenticated/unprivileged user requests (`gateway.ProcessRequest` → `HandleLegacyUserMessage`), matching the acceptance criteria for cross-user response confusion.

### Likelihood Explanation
Likelihood is moderate: the attacker needs to guess or observe another client's `MessageID` (which is often predictable/sequential/request-supplied rather than a cryptographically random per-session secret) and race the timing window before pruning/response delivery occurs. This is analogous to the original report's "Low likelihood, requires execution to reach a malicious address" — here it requires only ID prediction/collision plus timing, which is generally easier than requiring a hook-triggered reentrancy path.

### Recommendation
Scope `savedCallbacks` entries by a combination of `MessageID` and an unforgeable caller identity (e.g., the request's signer/session, or a server-generated nonce unrelated to client input), and reject insertion if an active callback already exists for a given key rather than silently overwriting it. Consider deriving/validating `MessageID` uniqueness against a signature-bound value instead of accepting arbitrary client-controlled strings.

### Proof of Concept
1. Client A sends a legacy user message via the gateway with `MessageID = "X"`, which is validated and stored: `savedCallbacks["X"] = A's callback` (`handler.go:411-414`).
2. Before A's request completes, Client B sends its own legacy user message reusing `MessageID = "X"` (Validate() has no uniqueness check, `message.go:54-66`), overwriting the map entry: `savedCallbacks["X"] = B's callback`.
3. A DON node responds for the original request/ID `"X"`; `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds B's callback, deletes the entry, and delivers A's response data to B (`handler.go:148-161`).

Note: I could not fully trace whether an upstream layer (e.g. session/connector auth) additionally binds `MessageID` per-connection before reaching this handler — this could not be verified with the available index and would need direct code review in a full Devin session to confirm exploitability end-to-end.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```
