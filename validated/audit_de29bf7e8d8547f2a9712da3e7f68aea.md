Based on my investigation, the claim is technically accurate about the code behavior.

Confirmed facts:
- `msg.Body.MessageID` is set directly from the client-supplied JSON-RPC request `ID` field with no server-side generation or uniqueness enforcement: `m.Body.MessageID = req.ID` [1](#0-0)  and in `gateway.go`'s `ProcessRequest`, the only constraint on the ID is a length cap of 200 characters, with no uniqueness/ownership check tied to session identity: [2](#0-1) 
- `HandleLegacyUserMessage` unconditionally overwrites `h.savedCallbacks[msg.Body.MessageID]` without checking whether an entry already exists for that key: [3](#0-2) 
- `handleWebAPITriggerMessage` looks up and deletes the callback purely by `MessageID`, delivering the response to whatever callback currently occupies that slot: [4](#0-3) 
- No signature, session-token, or per-caller binding is checked against the `savedCallbacks` map key anywhere in this path; `ProcessRequest` passes an `auth` string into `jsonrpc2.DecodeRequest`, but that value is not used to scope or verify uniqueness of `MessageID` for this legacy handler.

This matches the described root cause: an unauthenticated HTTP client to the gateway's user-facing port fully controls the `MessageID` used as the sole key of a shared, mutable map, and there is no ownership/session binding preventing a second, unrelated client from colliding with and silently overwriting another party's still-pending callback entry within the callback lifetime window (up to 120s by default, per `defaultCallbackMaxAgeSec`). The exploit path is directly reachable by any unprivileged caller of the public gateway HTTP endpoint (`ProcessRequest` → `HandleLegacyUserMessage`), requires no operator/admin access, and the resulting impact — response misdelivery/denial to the victim and potential leakage of a response object to an unrelated caller — maps to the "cross-user response corruption" impact class named in the rules as in-scope.

Audit Report

## Title
Legacy Web API trigger handler lets any unauthenticated user hijack another user's pending callback via `MessageID` collision - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
`HandleLegacyUserMessage` stores a pending callback in the shared `savedCallbacks` map keyed solely by the client-supplied `msg.Body.MessageID`, with no uniqueness or ownership check before insertion. Since `MessageID` is copied verbatim from the untrusted JSON-RPC request ID (`ValidatedMessageFromReq`), any unauthenticated caller of the gateway's `web_api_trigger` endpoint can supply an ID colliding with another party's in-flight request, silently overwriting that party's saved callback and causing the eventual DON response to be delivered to the wrong caller.

## Finding Description
`gateway.go`'s `ProcessRequest` accepts a raw JSON-RPC request from any unauthenticated HTTP client, decodes it, and — for legacy DON-ID-bearing requests — calls `h.HandleLegacyUserMessage(ctx, msg, callback)` with `msg.Body.MessageID` set directly to the client-controlled `jsonRequest.ID` (only length-capped at 200 chars, no uniqueness check). `HandleLegacyUserMessage` then unconditionally executes:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()
```
with no check for an existing entry under that key. On the response path, `handleWebAPITriggerMessage` retrieves and deletes the callback purely by `msg.Body.MessageID`, delivering the response to whatever callback object currently occupies that map slot. There is no session token, signature, or per-caller identity binding tied to `savedCallbacks` entries anywhere in this path, so nothing prevents a second unrelated caller from reusing a still-pending `MessageID` and displacing the original entry.

## Impact Explanation
An unprivileged attacker who submits a `web_api_trigger` request with a `MessageID` colliding with a victim's currently in-flight request overwrites the victim's callback entry. When the DON later responds with that shared `MessageID`, the response is delivered to whichever callback is currently registered — potentially the attacker's — causing the victim's HTTP call to hang until `RequestTimeoutError`, and potentially delivering a response tied to the victim's workflow trigger to the attacker. This is a concrete cross-user response corruption issue reachable by unauthenticated gateway clients.

## Likelihood Explanation
Exploitability requires the attacker to guess or otherwise obtain another party's chosen `MessageID` within the callback's lifetime window (up to `defaultCallbackMaxAgeSec` = 120s), since IDs are fully attacker/client-supplied with no server-enforced entropy or uniqueness requirement. If clients use low-entropy or predictable ID generation (e.g., sequential/timestamp-based IDs), this is trivially exploitable by any unauthenticated caller of the gateway's public HTTP endpoint, with no privileged access required.

## Recommendation
Bind `savedCallbacks` entries to request ownership rather than relying solely on the attacker-controlled `MessageID`:
- Reject registration (return an error instead of silently overwriting) when a `MessageID` already exists in `savedCallbacks`.
- Alternatively, derive a server-side-unique composite key (e.g., prefixed with a connection/session identifier not controllable by the client) for the map, so collisions across different callers cannot occur.

## Proof of Concept
1. Victim sends a `web_api_trigger` legacy gateway request with `MessageID = "X"`; `HandleLegacyUserMessage` stores the victim's callback under key `"X"` and forwards the request to DON members.
2. Before the DON responds, an attacker sends their own unauthenticated `web_api_trigger` request also using `MessageID = "X"`; `HandleLegacyUserMessage` overwrites `savedCallbacks["X"]` with the attacker's callback.
3. When a DON node responds with `MessageID = "X"`, `handleWebAPITriggerMessage` looks up and deletes `savedCallbacks["X"]`, finding the attacker's callback, and delivers the response there — the victim's original HTTP call times out while the attacker potentially receives a response correlated with the victim's original request.

A Go integration test can drive this directly against `handler.HandleLegacyUserMessage`/`HandleNodeMessage` by registering two callbacks with the same `MessageID` and asserting which callback receives the eventual `handleWebAPITriggerMessage` response.

### Citations

**File:** core/services/gateway/handlers/common/message_util.go (L51-52)
```go
	m.Body.Method = req.Method
	m.Body.MessageID = req.ID
```

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
