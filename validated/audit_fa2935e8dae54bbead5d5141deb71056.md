This confirms it: `RequestCache.NewRequest` (used elsewhere in the gateway) explicitly rejects duplicate `(sender, MessageID)` keys with `"request already exists"` [1](#0-0) , but the legacy `capabilities.handler` does not use this cache at all — it stores directly into a plain map with no collision check.

### Title
Unprivileged client can hijack another user's pending Gateway callback via colliding `MessageID` (cross-user response confusion) - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The CVE describes a use-after-free/double-free in a Linux NIC driver where a buffer's lifetime is not properly tracked, letting a stale/reused reference be delivered to the wrong consumer, causing a crash or info leak. The chainlink Gateway `capabilities` handler has an analogous **object-lifetime confusion** bug at the application layer: an attacker-controlled `MessageID` key is used, without uniqueness enforcement, to store and later retrieve a `savedCallback` object that is used to route a response back to a specific caller's HTTP connection. Colliding IDs let one caller's live callback entry be silently overwritten (freed early / "reused") by another caller, so a response meant for user A can be delivered to user B — the same class of bug as the CVE (unsynchronized reuse of a live resource across two independent consumers), but here it manifests as cross-user response leakage instead of a kernel crash.

### Finding Description
`gateway.ProcessRequest` accepts `jsonRequest.ID` directly from an unauthenticated/unprivileged HTTP client with only a length check (`<= 200` chars) [2](#0-1) , then routes it to `handler.HandleLegacyUserMessage`, which uses this attacker-supplied ID as `msg.Body.MessageID` and directly overwrites the shared `savedCallbacks` map with no existence check: [3](#0-2) 

Compare this to `handleWebAPITriggerMessage`, which retrieves and deletes whatever `savedCallback` is currently stored at that `MessageID` when a DON node later replies, and blindly sends the response to it: [4](#0-3) 

Because the map is keyed only on the caller-chosen `MessageID` (not on caller identity, connection, or sender/receiver pair), a second unprivileged client can submit a concurrent request using the exact same `MessageID` as a victim's still-pending request. This overwrites the victim's `*savedCallback` entry in `h.savedCallbacks` before the DON responds. When the DON node's response for that `MessageID` eventually arrives, `handleWebAPITriggerMessage` looks the entry up by ID only and delivers the (potentially sensitive) response payload to whichever callback currently occupies that slot — the attacker's HTTP connection — while the original victim's request is silently orphaned (never resolved, until pruned/timed out).

This is structurally the same bug class as the CVE: a shared resource (callback/buffer) keyed by an identifier that is not guaranteed unique per-consumer, freed/reused out of sequence, and delivered to the wrong owner. The codebase clearly recognizes this hazard and defends against it elsewhere — `RequestCache.NewRequest` rejects duplicate `(sender, MessageID)` pairs with `"request already exists"` [1](#0-0) , and the v2 HTTP trigger handler enforces JWT-based replay/duplicate protection ("token has already been used") [5](#0-4)  — but the legacy `capabilities.handler.HandleLegacyUserMessage` path has no equivalent check.

### Impact Explanation
An unprivileged client interacting with the gateway's legacy user-message endpoint can:
- Receive another user's response payload for a web API trigger callback (cross-user response confusion / potential information disclosure), and
- Deny the legitimate user their response (their request is silently dropped from the map and only recovers via timeout/prune, i.e., availability impact).

This matches the "cross-user response confusion" acceptance criterion in scope, reached from a fully unprivileged client via the internet-facing gateway's message envelope/handler path.

### Likelihood Explanation
Exploitation requires only sending two ordinary, unauthenticated JSON-RPC/legacy requests to the gateway with the same client-chosen request `id` while a victim's request of the same ID is still in flight (within the callback prune window, default ~120s per `defaultCallbackMaxAgeSec`, and up to `defaultMaxSavedCallbacks` = 20000 entries) [6](#0-5) . There is no authentication or per-caller namespacing of `MessageID` in this path, so likelihood is high for an attacker who can predict or guess a victim's request ID (e.g., low-entropy client-generated IDs, or race conditions where the attacker submits many requests with sequential/common IDs hoping to collide with a victim).

### Recommendation
Namespace `savedCallbacks` by a value that includes caller/session identity (not just the raw attacker-supplied `MessageID`), or reject a new `HandleLegacyUserMessage` request if an entry already exists for that `MessageID` (mirroring `RequestCache.NewRequest`'s `"request already exists"` behavior) instead of silently overwriting it. Consider migrating this legacy handler to the same protected `RequestCache` abstraction already used elsewhere in the gateway.

### Proof of Concept
1. Unprivileged client A sends a legacy `web_api_trigger` request to the gateway with `id = "X"`; the gateway stores `savedCallbacks["X"] = callbackA` [7](#0-6)  and forwards it to DON nodes.
2. Before the DON responds, unprivileged client B sends its own request with the same `id = "X"`; the gateway overwrites `savedCallbacks["X"] = callbackB` with no duplicate check.
3. A DON node responds with `MessageID = "X"`; `handleWebAPITriggerMessage` looks up and deletes `savedCallbacks["X"]`, which is now `callbackB`, and sends the response — intended for A's original request — to B's connection via `savedCb.SendResponse(...)` [8](#0-7) .
4. Client A never receives a response and times out.

Note: I could not fully trace every code path that produces `msg.Body.MessageID` for the legacy request (e.g., whether any upstream layer enforces sender-scoped uniqueness before reaching this handler); confirming the full absence of mitigating checks end-to-end would benefit from a deeper trace in a live Devin session with repo-wide search/build tooling.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L360-393)
```go
	t.Run("duplicate JWT token and request ID", func(t *testing.T) {
		handler, mockDon := createTestTriggerHandler(t)
		privateKey := createTestPrivateKey(t)
		registerWorkflow(t, handler, workflowID, privateKey)
		callback1 := hc.NewCallback()
		callback2 := hc.NewCallback()

		triggerReq := gateway_common.HTTPTriggerRequest{
			Workflow: gateway_common.WorkflowSelector{
				WorkflowID: workflowID,
			},
			Input: []byte(`{"key": "value"}`),
		}
		reqBytes, err := json.Marshal(triggerReq)
		require.NoError(t, err)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      requestID,
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}
		// First request should succeed
		req.Auth = createTestJWTToken(t, req, privateKey)
		mockDon.EXPECT().SendToNode(mock.Anything, mock.Anything, mock.Anything).Return(nil).Times(3)
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback1, time.Now())
		require.NoError(t, err)

		// Second request with same ID should fail
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback2, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "token has already been used")

```
