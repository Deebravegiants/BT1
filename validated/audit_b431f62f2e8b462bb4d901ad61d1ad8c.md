Audit Report

## Title
Client-controlled `MessageID` overwrite causes cross-user response confusion in legacy WebAPI trigger handler - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`HandleLegacyUserMessage` stores each user's callback keyed solely by the caller-supplied `msg.Body.MessageID`, without checking for an existing/in-flight entry under the same key before overwriting it. `Message.Validate` only checks `MessageID` length and trailing-null-byte formatting, not uniqueness, so a second request reusing an ID from a still-pending first request will silently clobber that first request's saved callback.

## Finding Description
`HandleLegacyUserMessage` unconditionally writes `h.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}` under a mutex, with no existence check: [1](#0-0) . Later, when a node responds, `handleWebAPITriggerMessage` looks up and dispatches strictly by that `MessageID` string, delivering the response to whatever callback currently occupies that map slot: [2](#0-1) . `Message.Validate` only bounds-checks and format-checks `MessageID`, never enforcing uniqueness across in-flight requests: [3](#0-2) . The signature check in `Validate` binds the signature to the message content (including `MessageID`) and derives `Sender`, but does not prevent two different signed messages — from the same or different senders — from carrying an identical `MessageID` value, since nothing in the codebase enforces ID uniqueness before insertion into `savedCallbacks`.

This contrasts with the newer v2 HTTP trigger handler, which explicitly checks for an in-flight `requestID` and rejects the duplicate with `jsonrpc.ErrConflict` before storing a callback: [4](#0-3) , and with the vault/confidentialrelay handlers, which use a `RequestReplayGuard` or an explicit `activeRequests[req.ID] != nil` check: [5](#0-4) [6](#0-5) .

The `HandleLegacyUserMessage` is part of the `Handler` interface invoked per unprivileged user request (`HandleUserMessage`/`HandleLegacyUserMessage` is documented as processing "each user request" via a "separate goroutine"): [7](#0-6) . This confirms the code path is reachable from ordinary user-facing gateway traffic, not an operator-only or internal-only path.

## Impact Explanation
If two concurrent legacy WebAPI trigger requests use the same `MessageID` (whether from the same requester retrying, or from unrelated requesters/workflows), the second overwrites the first's saved callback. The subsequent node response for that `MessageID` is delivered to whichever callback remains in the map, meaning requester A's response can be delivered to requester B's connection (cross-user response confusion) or requester A's response can be silently dropped. This matches the "cross-user response corruption" impact category referenced in the validation criteria.

## Likelihood Explanation
Exploitability requires only that an unprivileged/ordinary gateway client choose (or accidentally reuse) a `MessageID` string that collides with another in-flight request's `MessageID` — there is no authentication or role escalation needed, only that two requests are concurrently in-flight (bounded by `CallbackMaxAgeSec`, default 120s) with the same ID. Whether this is trivially exploitable in production depends on how the actual upstream ingress (the component that constructs `api.Message` from an inbound end-user/HTTP request) generates or accepts `MessageID` — if it is always attacker-supplied end-to-end, likelihood is high; if the gateway or an upstream proxy always generates a fresh random ID server-side, exploitability by an external unprivileged attacker is much lower. I was unable to locate the exact HTTP/JSON-RPC ingress handler that constructs the `api.Message.Body.MessageID` from an inbound external request within the available tool budget, so end-to-end attacker control of this field is not fully confirmed. Given `MessageID` is validated by `Message.Validate` as a free-form string only bounded by length, and `HandleLegacyUserMessage` is explicitly documented as processing per-user requests, it is reasonable to conclude `MessageID` is client-controlled at least at the message-construction layer that calls `HandleLegacyUserMessage`.

## Recommendation
Add a duplicate-ID guard in `HandleLegacyUserMessage`, mirroring the pattern in `http_trigger_handler.go`'s `setupCallback`: under `h.mu`, check `h.savedCallbacks[msg.Body.MessageID]` for an existing entry and reject the new request (returning a conflict-style error to the caller) instead of overwriting it.

## Proof of Concept
Minimal Go unit test plan against `core/services/gateway/handlers/capabilities/handler_test.go`:
1. Construct two valid `api.Message` values with `Body.Method = MethodWebAPITrigger`, a valid `TriggerRequestPayload` with a fresh `Timestamp`, and identical `Body.MessageID` (e.g., `"dup-id"`), each signed with distinct keys (simulating two different callers).
2. Call `handler.HandleLegacyUserMessage(ctx, msg1, callback1)` then `handler.HandleLegacyUserMessage(ctx, msg2, callback2)` before either receives a node response.
3. Assert that `h.savedCallbacks["dup-id"]` now points to `callback2`'s saved callback, i.e., `callback1` was silently discarded.
4. Simulate a node response for `MessageID = "dup-id"` via `HandleNodeMessage`/`handleWebAPITriggerMessage` and assert it is delivered to `callback2` (or to whichever callback remains), confirming `callback1` never receives a response — demonstrating cross-user response loss/misdelivery.

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

**File:** core/capabilities/vault/request_replay_guard.go (L35-47)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
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

**File:** core/services/gateway/handlers/handler.go (L23-42)
```go
// Handler implements service-specific logic for managing messages from users and nodes.
// There is one Handler object created for each DON.
//
// The lifecycle of a Handler object is as follows:
//   - Start() call
//   - a series of HandleUserMessage/HandleNodeMessage calls, executed in parallel
//     (Handler needs to guarantee thread safety)
//   - Close() call
type Handler interface {
	job.ServiceCtx

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleJSONRPCUserMessage(ctx context.Context, jsonRequest jsonrpc.Request[json.RawMessage], callback Callback) error
```
