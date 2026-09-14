### Title
Missing MessageID uniqueness check allows callback-registration collision and cross-user response confusion in the legacy Web API trigger handler - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`handler.HandleLegacyUserMessage` registers a pending user callback keyed only by the attacker/client-supplied `msg.Body.MessageID`, without checking whether an entry for that ID already exists. Every other request-tracking path in the gateway (HTTP trigger handler, confidentialrelay handler, vault handler, and the sender-scoped `requestcache`) explicitly rejects a duplicate/in-flight request ID before registering a new callback. This handler does not, so a second (possibly unrelated) request using the same `MessageID` silently overwrites the first request's saved callback.

### Finding Description
`HandleLegacyUserMessage` stores the callback unconditionally: [1](#0-0) 

Compare this with the equivalent registration code paths elsewhere in the same package/gateway, all of which reject a colliding ID before insertion: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

When a DON node later answers with the trigger response, the response is matched solely on `MessageID` (the map key), and the entry is deleted and its `SendResponse` invoked for whoever currently occupies the map slot: [6](#0-5) 

Because insertion is not guarded by a "does this ID already exist" check, two logically distinct incoming legacy requests that happen to carry the same `MessageID` (attacker-chosen, since `MessageID` is a client-supplied field of the message body rather than something derived from an authenticated, unique per-request source) can race:
1. Victim submits a legacy trigger request with `MessageID = X`; a `savedCallback` for X is stored, and the request is broadcast to DON nodes.
2. Before the DON responds, an unprivileged caller submits their own legacy request with the same `MessageID = X`. This overwrites the map entry, replacing the victim's callback with the attacker's.
3. When the DON node responds for `MessageID = X` (satisfying the victim's original request), `handleWebAPITriggerMessage` looks up the (now attacker-owned) entry and delivers the victim's response payload to the attacker's callback.
4. The victim's original callback is orphaned — it is never invoked and only reclaimed later by the age/size-based `pruneCallbacks` sweep: [7](#0-6) 

This is the direct structural analog of CVE-2023-4575: the report describes multiple identical callbacks created under the same identity that get resolved/destroyed together, so one requester's completion can improperly affect another's outstanding callback. Here Go's garbage collector prevents literal memory unsafety, but the same "no uniqueness guard on callback registration" root cause produces the security-relevant consequence permitted by the rules: cross-user response confusion (the wrong caller receives another party's response) plus a callback-starvation/DoS window for the victim.

### Impact Explanation
An unprivileged external client interacting with the gateway's legacy Web API trigger endpoint can, by choosing a colliding `MessageID`, cause another in-flight requester's trigger response to be delivered to itself instead of to the rightful caller, and cause the rightful caller's request to silently hang until the periodic pruner expires it (up to `CallbackMaxAgeSec`, default 120s). This is a concrete cross-user response confusion issue affecting the unprivileged gateway client entry point.

### Likelihood Explanation
Likelihood depends on how `MessageID` is generated/validated for legacy Web API trigger requests and whether it is scoped per-sender elsewhere in the pipeline before reaching this handler. I was not able to fully confirm from the indexed code whether an upstream layer already enforces per-sender/global `MessageID` uniqueness before calling `HandleLegacyUserMessage` (my search for the message/ID validation logic that feeds this handler and its callers across `core/services/gateway/gateway.go` / `multihandler.go` did not return the actual body of that validation). If `MessageID` is fully client-chosen and not otherwise deduplicated by sender, the collision is trivially triggerable by any unprivileged caller sending two overlapping requests with an identical ID; if an upstream layer already scopes/validates IDs per-sender or enforces global uniqueness independent of this handler, exploitability would be reduced. This uncertainty should be resolved by inspecting the callers of `HandleLegacyUserMessage` and the message-validation code in `core/services/gateway/gateway.go`/`multihandler.go`/`core/services/gateway/api/message.go`, which the current search could not fully surface.

### Recommendation
In `HandleLegacyUserMessage`, before inserting into `h.savedCallbacks`, check for an existing entry under the same key (and ideally scope the key by sender, mirroring `requestcache.go`'s `globalID{sender, id}` pattern) and reject the request with a conflict/duplicate error, consistent with `httpTriggerHandler.setupCallback`, the confidentialrelay handler's `newActiveRequest`, and the vault handler's `newActiveRequest`.

### Proof of Concept
1. Attacker/legitimate victim submits legacy request A with `msg.Body.MessageID = "X"` to the gateway; `HandleLegacyUserMessage` stores `savedCallbacks["X"] = victimCallback` and forwards to all DON members.
2. Before any node responds, attacker submits legacy request B with `msg.Body.MessageID = "X"`; `HandleLegacyUserMessage` overwrites `savedCallbacks["X"] = attackerCallback` (no existing-key check at `handler.go:411-412`).
3. A DON node responds for `MessageID = "X"` (satisfying request A). `handleWebAPITriggerMessage` (`handler.go:148-161`) looks up `savedCallbacks["X"]`, finds `attackerCallback`, deletes the entry, and calls `attackerCallback.SendResponse(...)` with the victim's response data.
4. `victimCallback` never receives a response and remains pending until `pruneCallbacks` evicts it after `CallbackMaxAgeSec`.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-312)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-420)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
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
