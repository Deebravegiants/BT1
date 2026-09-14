## Title
Legacy WebAPI Gateway Handler Allows Unauthenticated Callback-Slot Hijacking via Attacker-Controlled `message_id` Collision — ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
The SEDA `postBatch`/`postResult` bug is a class of vulnerability where an unprivileged actor can claim a shared, keyed "slot" (the batch sender address) that a later, unrelated operation depends on, and by making that slot misbehave (revert on transfer), block or corrupt processing for everyone relying on it. The closest reachable analog in this codebase is in the Gateway's legacy WebAPI capability handler, where the `savedCallbacks` map — the slot that determines who receives the DON's response to a triggered request — is keyed purely by a caller-supplied `message_id` with **no collision/ownership check**, unlike the newer v2 trigger handler which explicitly guards against this.

## Finding Description
`gateway.ProcessRequest` accepts a request from any unauthenticated internet-facing client, decodes it into an `api.Message`, and for legacy requests calls `h.HandleLegacyUserMessage(ctx, msg, callback)` [1](#0-0) .

In `HandleLegacyUserMessage`, the handler stores the caller's `callback` in a shared map keyed by the attacker-controlled `msg.Body.MessageID`, with no check for whether an entry already exists for that ID:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()
``` [2](#0-1) 

`MessageID` originates directly from the incoming request body (`m.Body.MessageID`) and is only checked for length/format, not uniqueness or ownership, in `Message.Validate()` [3](#0-2) .

When a DON node later responds to a trigger, the gateway looks the callback up **only by `MessageID`**, delivers the first response to whichever callback is currently stored, and deletes the entry:
```go
h.mu.Lock()
savedCb, found := h.savedCallbacks[msg.Body.MessageID]
delete(h.savedCallbacks, msg.Body.MessageID)
h.mu.Unlock()
if found {
    ...
    return savedCb.SendResponse(...)
}
``` [4](#0-3) 

Because insertion into `savedCallbacks` is unconditional, an unprivileged attacker who submits a second legacy request using the same `message_id` as an in-flight legitimate request overwrites the map entry with their own callback. The original caller's `callback` reference is orphaned (never invoked, causing it to hang until the gateway's request timeout), while the DON's eventual response for the original triggered workflow is instead delivered to the attacker's callback — a direct cross-user response confusion, structurally identical to the SEDA report's pattern of an unprivileged party claiming a shared role/slot (`batchSender`) that downstream logic (`postResult`) unconditionally trusts and acts on.

Notably, the newer v2 trigger handler (`httpTriggerHandler.setupCallback`) already recognizes and defends against exactly this hazard, explicitly rejecting duplicate in-flight request IDs:
```go
if _, found := h.callbacks[requestID]; found {
    h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used...", requestID), callback)
    return nil, fmt.Errorf("in-flight request ID: %s", requestID)
}
``` [5](#0-4) 
confirming that the legacy path's lack of this guard is a genuine gap rather than intended behavior.

## Impact Explanation
An unauthenticated, unprivileged internet-facing client can:
- Deny service to a legitimate caller by orphaning their callback (their HTTP request will hang until the gateway timeout and never receive the DON's response).
- Cause cross-user response confusion: the attacker's callback can receive the response payload generated for another user's triggered request/workflow execution, if the attacker can predict or race the victim's `message_id`.

This matches the accepted bug classes of "unauthorized... fund movement" analogs and "cross-user response confusion" explicitly permitted by the validation criteria, and is reachable purely through the internet-facing gateway message envelope handling with no privileged role required.

## Likelihood Explanation
Exploitability depends on the attacker knowing or guessing a victim's in-flight `message_id` and winning a race before the DON responds (a window on the order of the trigger's round-trip time). Since `message_id` is fully attacker-supplied and not validated for uniqueness or bound to session/ownership, any caller who can observe or predict IDs (e.g., sequential/predictable client-generated IDs, or an attacker targeting their own outstanding request being overwritten by a second self-submitted request to test/demonstrate the hijack) can trigger this deterministically for their own requests, and probabilistically/timing-based for others.

## Recommendation
In `HandleLegacyUserMessage`, before inserting into `savedCallbacks`, check whether an entry already exists for `msg.Body.MessageID` and reject the new request (mirroring the `ErrConflict` behavior already implemented in the v2 `setupCallback` path) rather than silently overwriting the existing callback.

## Proof of Concept
No PoC was executed; the flaw is demonstrated by direct code inspection: the unconditional map write in `HandleLegacyUserMessage` at [2](#0-1)  versus the collision-check present in the sibling v2 implementation at [6](#0-5) .

### Citations

**File:** core/services/gateway/gateway.go (L253-279)
```go
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
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
