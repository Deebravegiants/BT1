### Title
Legacy Web API trigger handler lets any unauthenticated user hijack another user's pending callback via `MessageID` collision - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
`HandleLegacyUserMessage` stores a pending callback in the shared `savedCallbacks` map keyed solely by the client-supplied `msg.Body.MessageID`, with no check for whether that ID is already in use by another in-flight request. Any unprivileged caller of the gateway's legacy `web_api_trigger` endpoint can supply a `MessageID` that collides with a still-pending request from a different user, silently overwriting that user's saved callback. When the DON node later responds with the same `MessageID`, `handleWebAPITriggerMessage` looks the callback up purely by that ID and delivers the result to whichever callback is currently registered — potentially the attacker's — producing lost or misdirected responses.

### Finding Description
The gateway is an internet-facing entry point that unauthenticated/unprivileged clients call directly (`gateway.go`'s `ProcessRequest` → `h.HandleLegacyUserMessage`). In `core/services/gateway/handlers/capabilities/handler.go`: [1](#0-0) 

the handler unconditionally does:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()
```
`msg.Body.MessageID` comes directly from the untrusted request body (`ValidatedMessageFromReq` simply copies `req.ID` into `m.Body.MessageID`), and there is no uniqueness/collision check before insertion, unlike other handlers in the same codebase (e.g. the vault handler explicitly rejects a "duplicate requestId" — see `core/services/gateway/handlers/vault/handler_test.go` lines 707-750, which validates that duplicate IDs are rejected with `"request was already authorized previously"`).

On the response side, `handleWebAPITriggerMessage` retrieves and deletes the callback purely by `msg.Body.MessageID`: [2](#0-1) 

Because the map entry is keyed only by an attacker-controlled string with no ownership binding (no session/user identity check tied to the callback), a second, unprivileged request using the same `MessageID` as an already-pending legitimate request silently replaces the first request's callback reference in the map. This is directly analogous to the referenced report's bug class: a public/permissionless call path mutates shared state that another party's earlier operation depends on for correct attribution, causing the original party's outcome (their response, i.e., their "reward") to become stuck/lost or delivered to the wrong party.

### Impact Explanation
If an unprivileged attacker submits a `web_api_trigger` request with a `MessageID` matching a victim's currently in-flight request (predictable, guessed, or otherwise obtained), the victim's callback entry is overwritten. When the DON node subsequently returns the result associated with that shared `MessageID`, `handleWebAPITriggerMessage` delivers it to whichever callback object currently occupies that map slot — the attacker's newly-registered one. This causes:
- The legitimate requester's HTTP call to gateway to hang until timeout (`RequestTimeoutError`), i.e., denial of correct response delivery.
- Potential cross-user response confusion where the attacker receives a response payload correlated with the victim's original workflow trigger request via the same `MessageID`.

This satisfies "cross-user response confusion" from an unprivileged client request against the internet-facing gateway message envelope/handler path.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or race for the same `MessageID` as a target victim request within the callback's lifetime window (up to `defaultCallbackMaxAgeSec` = 120s). Since `MessageID` is fully attacker-supplied and unauthenticated, and there is no per-caller/session binding enforced on the `savedCallbacks` map, any caller that learns or guesses another party's chosen ID (e.g., low-entropy client-side ID generation, or observing IDs echoed elsewhere) can perform the overwrite. The comparison to the vault handler in the same codebase, which explicitly guards against duplicate/overlapping request IDs, indicates this specific legacy handler lacks equivalent protection.

### Recommendation
Bind `savedCallbacks` entries to request ownership, not solely the client-chosen `MessageID`:
- Reject registration (return an error rather than overwrite) if a `MessageID` already exists in `savedCallbacks`, mirroring the duplicate-ID rejection already implemented in the vault handler (`core/services/gateway/handlers/vault/handler_test.go`).
- Alternatively, derive/prefix the map key server-side with a value unique to the connection/session (not attacker-controlled) so collisions across different callers are impossible.

### Proof of Concept
1. Victim sends a legitimate `web_api_trigger` legacy gateway request with `MessageID = "X"`; `HandleLegacyUserMessage` stores victim's callback under key `"X"` in `savedCallbacks` and forwards the request to DON members.
2. Before the DON responds, attacker (unauthenticated, unprivileged) sends their own `web_api_trigger` request also using `MessageID = "X"`. `HandleLegacyUserMessage` overwrites `savedCallbacks["X"]` with the attacker's callback and forwards attacker's own request to DON members using the same ID.
3. When a DON node responds with `MessageID = "X"` (whichever request it processes first), `handleWebAPITriggerMessage` looks up and deletes `savedCallbacks["X"]`, finding the attacker's callback, and delivers the response there — the victim's original HTTP call receives no response and eventually times out, while the attacker may receive a response tied to work triggered under the colliding ID.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```
