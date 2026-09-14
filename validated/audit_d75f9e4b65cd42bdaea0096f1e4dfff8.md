I found a concrete unprivileged-actor analog: in the gateway's legacy WebAPI handler, the `MessageID` used as the key for tracking a pending user callback is fully attacker-controlled and is never checked against a signature-bound identity or uniqueness constraint, so an unprivileged caller can pre-empt/overwrite another user's in-flight callback slot, causing the legitimate caller's response to be lost/blocked — the same "front-run a state-setting call with an unprivileged, attacker-chosen key to block a legitimate operation" bug class as the DKIM report.

### Title
Attacker-controlled MessageID lets an unprivileged caller overwrite/block another user's pending gateway callback - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`handler.HandleLegacyUserMessage` stores the caller's response callback in a map keyed purely by `msg.Body.MessageID`, a value taken directly from the untrusted JSON-RPC request ID with no ownership/ uniqueness check. Any unprivileged user can submit a request whose `MessageID` collides with (or is guessed/observed for) another in-flight legitimate request, silently replacing the stored callback and preventing the original caller from ever receiving the DON's response — analogous to the DKIM report's pattern of a public/unguarded method call letting an attacker set state that blocks someone else's pending, time-bound operation.

### Finding Description
`ProcessRequest` in `core/services/gateway/gateway.go` (lines 220-295) takes the request `ID` straight from the incoming JSON-RPC payload (only bounding its length to 200 chars) and passes the resulting `api.Message` to `h.HandleLegacyUserMessage`. [1](#0-0) 

Inside `HandleLegacyUserMessage`, after light validation of payload/timestamp/method, the handler unconditionally does:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
```
with no check for whether `msg.Body.MessageID` already exists in `savedCallbacks`. [2](#0-1) 

Later, when a DON node responds, `handleWebAPITriggerMessage` looks up and deletes the callback by that same `MessageID` and delivers the response to whichever callback is currently stored under that key: [3](#0-2) 

Because the `MessageID` is attacker-supplied and there is no per-user/per-signature binding on this map key (unlike the DON-side signature checks that exist elsewhere in the same file, e.g. `msg.Body.Sender != nodeAddr`), a second unprivileged request using the same `MessageID` (sent while the first is still in flight, within the request timeout window) silently replaces the map entry. The original caller's callback reference is dropped from `savedCallbacks`; when the legitimate DON response eventually arrives, it is delivered to the attacker's callback rather than the legitimate one, and the legitimate caller's request stalls until the gateway's request timeout fires (`callback.Wait(ctx)` in `gateway.go`) and returns a generic "handler timeout" error. This mirrors the audited bug class: an unauthenticated/unprivileged actor can front-run a legitimate call to occupy/overwrite a bookkeeping slot (there: the DKIM timelock; here: the callback map) and thereby block the victim's genuine operation from completing correctly.

The same pattern also exists verbatim in the simpler `dummyHandler.HandleLegacyUserMessage` (`core/services/gateway/handlers/handler.dummy.go`, lines 62-66), which likewise keys `savedCallbacks` solely by the untrusted `msg.Body.MessageID`. [4](#0-3) 

### Impact Explanation
Impact is availability/response-integrity, not fund loss: a legitimate user's gateway request can be silently hijacked or blocked so they receive a timeout instead of the real DON/workflow response, and (depending on downstream handling) the attacker may instead receive the legitimate response meant for the other requester — a cross-user response confusion. This is high-severity for correctness/availability of the gateway request path but does not directly move funds or leak node secrets.

### Likelihood Explanation
Likelihood is high in principle: the request ID/`MessageID` is entirely client-controlled and passed through with only a length check (`gateway.go` line 231-234). An attacker only needs to guess or observe another user's chosen `MessageID` and submit a colliding request during the (up to `defaultCallbackMaxAgeSec` = 120s) window it remains pending. In practice this requires the attacker to know or predict another user's exact `MessageID`, which reduces but does not eliminate exploitability if IDs are predictable, reused, or observable (e.g., via logs, shared client conventions, or short/deterministic ID schemes used by some integrators).

### Recommendation
Do not let an unprivileged request silently overwrite an existing `savedCallbacks` entry. Before inserting, check whether `msg.Body.MessageID` is already present and, if so, reject the new request (e.g., return a "duplicate/conflict" error) instead of overwriting the map entry — mirroring the recommended fix pattern of restricting the state-mutating write path so only the legitimate first caller's registration can occupy the slot until it naturally expires or completes. Apply the same guard to `dummyHandler.HandleLegacyUserMessage`.

### Proof of Concept
1. User A sends a legacy gateway request with `MessageID = "X"` for `MethodWebAPITrigger`; the gateway calls `HandleLegacyUserMessage`, which stores User A's callback under key `"X"` in `savedCallbacks` and forwards the request to all DON members. [5](#0-4) 
2. Before the DON responds, Attacker B sends another legacy request also with `MessageID = "X"` (possible because `ProcessRequest` only checks `len(jsonRequest.ID) > 200`, not uniqueness). [6](#0-5) 
3. `HandleLegacyUserMessage` overwrites `savedCallbacks["X"]` with Attacker B's callback. [2](#0-1) 
4. When the DON node responds with `MessageID = "X"`, `handleWebAPITriggerMessage` looks up `"X"` and finds only Attacker B's callback, delivering the response there and leaving User A's original request to hit the gateway's `callback.Wait(ctx)` timeout. [3](#0-2) 

Note: I was not able to fully trace how `MessageID`/request `ID` values are generated or whether any client-side convention (e.g., signed/derived IDs) makes collisions harder in practice for real integrators — that would require reviewing the client SDKs generating these gateway requests, which are outside what I could confirm from the indexed server-side code.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-419)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
```

**File:** core/services/gateway/handlers/handler.dummy.go (L62-66)
```go
func (d *dummyHandler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error {
	d.mu.Lock()
	d.savedCallbacks[msg.Body.MessageID] = &savedCallback{msg.Body.MessageID, callback}
	don := d.don
	d.mu.Unlock()
```
