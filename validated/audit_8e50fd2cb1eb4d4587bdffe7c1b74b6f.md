Audit Report

## Title
Global `savedCallbacks` map in the legacy WebAPI gateway handler is keyed only by client-supplied `MessageID` with no per-sender scoping or duplicate-ID rejection, allowing cross-user callback overwrite/response misdelivery - ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
`handler.HandleLegacyUserMessage` stores each pending user callback in a single, DON-wide map `savedCallbacks map[string]*savedCallback` keyed solely by the caller-supplied `MessageID`, with no check for an existing in-flight entry and no binding of the key to the sender's identity [1](#0-0) . Because `api.Message.Validate()` only restricts `MessageID` length and forbids a trailing null byte, and never enforces per-sender uniqueness [2](#0-1) , a second message that collides on `MessageID` silently overwrites the previously stored callback, and the subsequent node response is delivered only to whichever callback currently occupies that map slot [3](#0-2) .

## Finding Description
`HandleLegacyUserMessage` unconditionally assigns `h.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}` after basic payload/method/timestamp validation, without ever checking `if _, exists := h.savedCallbacks[msg.Body.MessageID]; exists` [1](#0-0) . The map is process/DON-wide (`handler` struct field, not per-sender) and guarded only by a plain `sync.Mutex`, giving no ownership semantics beyond the raw string key [4](#0-3) . When a node later responds for that `MessageID`, `handleWebAPITriggerMessage` looks up and deletes `h.savedCallbacks[msg.Body.MessageID]` and forwards the response to whatever `savedCallback` is currently stored there — there is no sender/receiver match performed at this stage [3](#0-2) . This is materially different from the sibling handlers in the same package tree, which explicitly detect and reject a duplicate/in-flight request ID: the v2 HTTP trigger handler test asserts an `"in-flight request"` / `ErrConflict` rejection [5](#0-4) , the vault handler rejects with `"request was already authorized previously"` [6](#0-5) , and the confidential relay handler rejects with `"request ID already exists"` [7](#0-6) . The legacy capabilities handler has no equivalent check, and the existing test suite for it explicitly notes this gap is unresolved: `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated` [8](#0-7) .

## Impact Explanation
An unprivileged client able to submit legacy gateway messages (`web_api_trigger`) can cause another in-flight request's callback entry to be silently overwritten and later deleted before the real response arrives, orphaning the original caller's request (denial of service on a per-request basis), or — under a race where the attacker's colliding message is registered after the victim's but before the node responds — receive the victim's DON response delivered to the attacker's callback instead (cross-user response corruption/impersonation) via `savedCb.SendResponse(...)` [9](#0-8) . This does not leak secrets directly, but it is a legitimate cross-user response corruption / gateway request impersonation issue reachable from the unprivileged legacy WebAPI trigger path.

## Likelihood Explanation
Exploitation requires only two legacy gateway messages that collide on `MessageID` while the first is still pending (within the default 120-second `CallbackMaxAgeSec` window) [10](#0-9) . Since `MessageID` is entirely attacker-chosen and unbounded by sender identity, an attacker who can predict, observe, or race a victim's `MessageID` (e.g., deterministic/sequential IDs, or simply retrying with a guessed ID) can trigger the overwrite deterministically; likelihood is moderate for targeted attacks and higher for accidental self-inflicted collisions from poorly randomized client ID schemes.

## Recommendation
Scope `savedCallbacks` keys by sender identity in addition to `MessageID` (e.g., `sender + "/" + MessageID`), and/or reject `HandleLegacyUserMessage` calls whose `MessageID` already has a live, unexpired entry — mirroring the duplicate-ID rejection already implemented in the v2 HTTP trigger handler, vault handler, and confidential relay handler. At minimum, add a `if _, exists := h.savedCallbacks[msg.Body.MessageID]; exists { return conflict }` guard before the unconditional store at [1](#0-0) .

## Proof of Concept
1. Send a legacy `web_api_trigger` message signed by user A with `MessageID = "X"`; `HandleLegacyUserMessage` stores `savedCallbacks["X"] = callback_A` [1](#0-0) .
2. Before the DON responds, send a second legacy `web_api_trigger` message signed by user B (or replayed/predicted) with the same `MessageID = "X"`; this silently overwrites `savedCallbacks["X"]` with `callback_B`.
3. When the DON node responds for `MessageID = "X"`, `handleWebAPITriggerMessage` delivers the response only to `callback_B`, leaving user A's request permanently unresolved [3](#0-2) . This can be encoded as a Go unit test extending `TestHandlerReceiveHTTPMessageFromClient` in `handler_test.go` that calls `HandleLegacyUserMessage` twice with the same `MessageID` from different signers and asserts the first callback never resolves while the second one does.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L48-61)
```go
type handler struct {
	services.StateMachine
	config          HandlerConfig
	don             handlers.DON
	donConfig       *config.DONConfig
	savedCallbacks  map[string]*savedCallback
	mu              sync.Mutex
	lggr            logger.Logger
	httpClient      network.HTTPClient
	nodeRateLimiter *ratelimit.RateLimiter
	wg              sync.WaitGroup
	stopCh          services.StopChan
	metrics         *metrics
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/api/message.go (L61-66)
```go
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L349-357)
```go
		// Second request with same ID should fail
		req.Auth = createTestJWTToken(t, req, privateKey)
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback2, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "in-flight request")

		r, err := callback2.Wait(t.Context())
		require.NoError(t, err)
		requireUserErrorSent(t, r, jsonrpc.ErrConflict)
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L748-750)
```go
		// send duplicate request
		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.ErrorContains(t, err, "request was already authorized previously")
```

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L878-880)
```go
	cb2 := common.NewCallback()
	err = h.HandleJSONRPCUserMessage(t.Context(), req, cb2)
	require.ErrorContains(t, err, "request ID already exists")
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-365)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
```
