Confirmed: in `core/services/gateway/gateway.go` `ProcessRequest`, the `jsonRequest.ID` (attacker-controlled, only bounded to 200 chars) becomes `msg.Body.MessageID` via `ValidatedMessageFromReq` (`core/services/gateway/handlers/common/message_util.go:36-58`), and `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go:411-414` unconditionally overwrites `h.savedCallbacks[msg.Body.MessageID]` with no existence/duplicate check, unlike the analogous `activeRequests`/`callbacks` maps in the vault and v2 HTTP-trigger handlers which explicitly reject duplicate/in-flight request IDs (`core/services/gateway/handlers/vault/handler.go:457-463`, `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:419-426`).

### Title
Message-ID Collision in `HandleLegacyUserMessage` Allows Unprivileged Sender to Hijack Another User's Pending Callback - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The legacy WebAPI-Trigger gateway `handler` stores pending user callbacks keyed only by the caller-supplied `MessageID`, without checking whether that ID is already in use by another in-flight request. This mirrors the `updateTrust()` DOS class: a shared, capacity-bounded resource (the `savedCallbacks` map / `maxVouchees` slots) can be filled or clobbered by cheap, repeated unprivileged actions, denying service to or corrupting state for legitimate other actors.

### Finding Description
`gateway.ProcessRequest` (`core/services/gateway/gateway.go:221-296`) accepts any HTTP-facing client request, decodes it, and only bounds `jsonRequest.ID` length to 200 characters (`core/services/gateway/gateway.go:231-234`) before calling `h.HandleLegacyUserMessage(ctx, msg, callback)`. The message ID is copied directly from the untrusted request ID in `ValidatedMessageFromReq` (`core/services/gateway/handlers/common/message_util.go:46-52`).

In `HandleLegacyUserMessage` (`core/services/gateway/handlers/capabilities/handler.go:341-421`), after minimal payload/timestamp/method checks, the handler does:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()
``` [1](#0-0) 

There is no `if _, exists := h.savedCallbacks[id]; exists { return err }` guard, unlike every other request-tracking map in the gateway handlers package (vault's `activeRequests`, v2 HTTP trigger's `callbacks`, and the confidential-relay handler all explicitly reject duplicate/in-flight IDs): [2](#0-1) [3](#0-2) 

When a node later responds, `handleWebAPITriggerMessage` looks up and deletes the entry solely by `MessageID` and forwards the *first* matching response to whichever `Callback` currently occupies that slot: [4](#0-3) 

Because two different unprivileged HTTP clients can pick the same `MessageID` string, an attacker who submits a request with a colliding ID after a victim's request is in flight will overwrite the victim's saved callback. The victim's original callback is orphaned (silently dropped, effectively a per-request DOS that only resolves via the eventual gateway-side timeout), while the attacker's callback receives whatever node response arrives for that ID — a cross-user response confusion, since the attacker can now potentially receive a response intended for someone else's trigger request.

Additionally, `pruneCallbacks()` bounds `savedCallbacks` by `MaxSavedCallbacks`, evicting the oldest entries once exceeded (`core/services/gateway/handlers/capabilities/handler.go:299-339`), so a burst of cheap collided/garbage `MessageID`s from a single unprivileged sender can also evict legitimate in-flight callbacks from other users before their nodes respond — directly analogous to the `maxVouchees` exhaustion DOS in the reported bug, since there is no per-sender allowlisting or minimum-cost gating (`// TODO: apply allowlist and rate-limiting here` is explicitly left unimplemented at `core/services/gateway/handlers/capabilities/handler.go:384`).

### Impact Explanation
- Denial of service: a legitimate user's WebAPI-trigger request silently never resolves (until gateway timeout) if another concurrent request reuses/collides on the same `MessageID`.
- Cross-user response confusion: the attacker's callback can receive the response payload originally destined for the victim's request, because routing is keyed purely on the untrusted, attacker-chosen `MessageID`.
- The explicit `// TODO: apply allowlist and rate-limiting here` comment confirms no sender-based mitigation currently exists on this legacy path.

### Likelihood Explanation
Any unauthenticated client hitting the gateway's public `/…` request endpoint can trigger `HandleLegacyUserMessage` with an arbitrary `ID` (bounded only to ≤200 chars, no uniqueness requirement) as long as it is well-formed enough to pass `ValidatedMessageFromReq`/`msg.Validate()` and targets a legacy DON-routed handler. Colliding with a victim's `MessageID` requires either predicting/observing it or brute-forcing short IDs, which is plausible given the format is caller-chosen and not namespaced per sender.

### Recommendation
In `HandleLegacyUserMessage`, check for an existing `savedCallbacks[msg.Body.MessageID]` entry before inserting, and reject the request (e.g., with a JSON-RPC conflict error, mirroring the vault and v2 HTTP-trigger handlers' `"request ID already exists"` / `"in-flight request ID"` behavior) instead of silently overwriting it. Also implement the still-pending allowlist/rate-limiting for this legacy path per the existing TODO to prevent cheap resource-slot exhaustion of `savedCallbacks`.

### Proof of Concept
1. Victim submits a valid legacy WebAPI-trigger request via `gateway.ProcessRequest` with `ID = "X"`; `HandleLegacyUserMessage` stores `savedCallbacks["X"] = victimCallback` and forwards to DON members.
2. Before the DON responds, an unprivileged attacker submits another well-formed legacy request with the same `ID = "X"`; `HandleLegacyUserMessage` overwrites `savedCallbacks["X"] = attackerCallback` (no duplicate check exists, see `core/services/gateway/handlers/capabilities/handler.go:411-414`).
3. When a DON node responds with `MessageID = "X"`, `handleWebAPITriggerMessage` delivers the response to `attackerCallback` (whichever callback is currently stored) and deletes the entry.
4. The victim's original callback never receives a response and eventually times out at the gateway level (`core/services/gateway/gateway.go:281-288`), demonstrating both the DOS on the victim and the response misdelivery to the attacker.

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
