Based on the code I was able to examine, here is my analysis.

### Title
Unauthenticated, unscoped `MessageID` allows cross-user response hijacking in gateway `savedCallbacks` map - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The `handler.HandleLegacyUserMessage` function stores each inbound user request's callback in a shared map keyed only by the client-supplied `msg.Body.MessageID`, with no verification that the ID is unique, unpredictable, or bound to the requesting client's identity/session: [1](#0-0) 
When a DON node later responds, `handleWebAPITriggerMessage` looks up and deletes the callback purely by `msg.Body.MessageID` and forwards the node's raw response payload to whatever callback is currently registered under that key: [2](#0-1) 

### Finding Description
This is structurally analogous to the Matrix advisory's root cause: an untrusted/externally-influenced identifier (there, `origin_server_ts`; here, `MessageID`) is trusted as the sole basis for a security-relevant decision — in this case, *which client receives which response*. There is no cryptographic binding between the `MessageID` and the specific caller/session; the field is chosen by the requester in `TriggerRequestPayload`/`api.MessageBody` and is only covered by that requester's own signature, which proves who sent *their own* message but does nothing to prevent a second, different unprivileged caller from independently choosing (or guessing) the same `MessageID` while a first caller's request is still pending. If two different requests share a `MessageID`, the second `HandleLegacyUserMessage` call overwrites the first entry in `h.savedCallbacks`, so when the DON node eventually replies to the first (legitimate) request, the response is delivered to the second (attacker-controlled) callback via `codec.EncodeLegacyResponse(msg)` — leaking the first caller's response content to an unauthorized party.

### Impact Explanation
If exploitable, this allows an unprivileged external client of the gateway's legacy user-facing endpoint to receive workflow-trigger responses intended for a different caller, i.e., cross-user response confusion — one of the explicitly in-scope impact categories. Response payloads for web API triggers can contain sensitive downstream data returned from workflow execution.

### Likelihood Explanation
Exploitability depends on factors I could not fully verify given tool/read limitations in this session: (1) whether the gateway's user-facing endpoint enforces any additional per-session/per-connection scoping on top of `MessageID` before invoking `HandleLegacyUserMessage`, (2) how difficult it is in practice for an attacker to predict or race a victim's in-flight `MessageID` (this needs confirmation from `core/services/gateway/api/message.go` and the user-facing HTTP/WS server code, which I was unable to open due to a tool-call setup error before running out of iterations), and (3) whether newer non-legacy paths (e.g., the v2 handlers) have replaced this mechanism with per-workflow/session scoped keys. Given these open questions, likelihood should be treated as unconfirmed rather than established.

### Recommendation
- Derive `savedCallbacks` keys from a value that is either server-generated or bound to the requester's authenticated identity/connection (e.g., combine `MessageID` with sender address/session ID, or generate the correlation ID server-side and never accept a client-supplied one for callback routing).
- On registration, reject/collision-check duplicate `MessageID`s within the outstanding-request window instead of silently overwriting (`delete` + reassign) the existing entry.
- Audit `core/services/gateway/api/message.go` and the v1/legacy user-facing gateway server code (not fully reviewed here) to confirm whether any additional binding already exists, and extend the same protection to any other maps keyed solely by client-supplied identifiers.

### Proof of Concept
Not independently verified end-to-end in this session due to incomplete access to `core/services/gateway/api/message.go` and the HTTP/WS ingress code before the session ended. Conceptually:
1. Victim sends a signed `web_api_trigger` request with `MessageID = "X"` to the gateway's legacy user endpoint; `HandleLegacyUserMessage` stores `h.savedCallbacks["X"] = victimCallback`.
2. Before the DON responds, attacker sends their own signed request also using `MessageID = "X"`; `HandleLegacyUserMessage` overwrites `h.savedCallbacks["X"] = attackerCallback`.
3. The DON node responds to the victim's original (still-pending) request; `HandleNodeMessage` → `handleWebAPITriggerMessage` looks up `h.savedCallbacks["X"]`, finds `attackerCallback`, and delivers the victim's response to the attacker.

Given the uncertainty flagged above, I recommend this be validated with a live reproduction (e.g., a Devin session with codebase/terminal access) against `core/services/gateway/api/message.go` and the ingress server to confirm whether `MessageID` collisions across independent, unrelated callers are actually reachable and unguarded before treating this as a confirmed vulnerability.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```
