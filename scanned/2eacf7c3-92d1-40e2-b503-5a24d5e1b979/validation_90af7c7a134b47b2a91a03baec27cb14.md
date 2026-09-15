### Title
Cross-user response hijacking via unvalidated MessageID reuse in gateway legacy web-api-trigger handler - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy web-api-trigger handler (`core/services/gateway/handlers/capabilities/handler.go`) stores an in-flight user callback keyed only by the client-supplied `MessageID`, without checking whether that key is already in use by another (possibly different) requester's in-flight request. `MessageID` is entirely attacker-controlled (any string up to 128 bytes, only checked for length/null-suffix), so any unprivileged client can pick the exact same `MessageID` as a concurrently pending request from a different user and overwrite the stored callback, causing the DON's eventual response to the original request to be delivered to the attacker instead of the legitimate caller.

### Finding Description
The gateway HTTP entrypoint `gateway.ProcessRequest` accepts a JSON-RPC-wrapped legacy `api.Message` from any unauthenticated internet-facing client, validates only structural/signature properties via `Message.Validate()` [1](#0-0) , then dispatches to `HandleLegacyUserMessage` [2](#0-1) .

`Message.Validate()` enforces only that `MessageID` is non-empty, ≤128 bytes, and doesn't end in a null byte — there is no uniqueness or ownership binding between `MessageID` and `Sender` [3](#0-2) .

In the capabilities handler, `HandleLegacyUserMessage` unconditionally overwrites the `savedCallbacks` map at the client-supplied key with no existence check:
```
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()
``` [4](#0-3) 

When a DON node later responds, `handleWebAPITriggerMessage` looks up and deletes the callback purely by `msg.Body.MessageID`, then delivers the response to whichever callback is currently stored there — regardless of which sender originally submitted the request that the DON is now responding to:
```
h.mu.Lock()
savedCb, found := h.savedCallbacks[msg.Body.MessageID]
delete(h.savedCallbacks, msg.Body.MessageID)
h.mu.Unlock()
if found {
    // Send first response from a node back to the user, ignore any other ones.
    ...
    return savedCb.SendResponse(...)
}
``` [5](#0-4) 

The identical unguarded-overwrite pattern also exists in the dummy handler used for other services: `d.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}` [6](#0-5) .

Exploit flow (unprivileged actor, no special role required):
1. Victim submits a legitimate web-api-trigger request with `MessageID = "X"`; the handler stores victim's callback at `savedCallbacks["X"]`.
2. Before the DON responds, attacker submits their own signed message reusing `MessageID = "X"` (trivial since MessageID is fully client-chosen and there is no per-sender namespacing).
3. `HandleLegacyUserMessage` overwrites `savedCallbacks["X"]` with the attacker's callback.
4. The DON eventually responds to the request keyed by `MessageID = "X"` (originating from the victim's request forwarded to the DON). `handleWebAPITriggerMessage` looks the entry up by `MessageID` only, finds the attacker's callback, and delivers the (potentially sensitive) response payload to the attacker's HTTP connection instead of the victim's.

This constitutes cross-user response confusion: an unprivileged, unauthenticated actor can hijack another user's in-flight gateway response by racing a colliding `MessageID`.

### Impact Explanation
An attacker on the public gateway endpoint can intercept response payloads intended for another user's workflow trigger request, potentially exposing whatever data/results the DON returns for that execution (which may include workflow-computed results tied to another user/workflow owner). This is a confidentiality/integrity violation of the request/response channel between an unprivileged client and the gateway, matching the "cross-user response confusion" class explicitly in scope.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to guess or predict a victim's `MessageID` and win a race window between the victim's request submission and the DON's response. If clients use low-entropy or externally observable MessageIDs (e.g., sequential IDs, or IDs echoed/logged elsewhere), or if an attacker can flood many colliding IDs while requests are in flight, exploitation becomes practical. No authentication or special privilege is required to attempt this — only network access to the gateway's public HTTP endpoint.

### Recommendation
- Scope `savedCallbacks` (and the equivalent map in `handler.dummy.go`) by `(Sender, MessageID)` rather than `MessageID` alone, so that responses can only be routed back to the callback registered by the same authenticated sender.
- In `HandleLegacyUserMessage`, reject the request (return an error) if an entry already exists for the given key instead of silently overwriting it, mirroring the existing `setupCallback` conflict check used in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go` (`ErrConflict` on duplicate `requestID`) [7](#0-6) .
- Verify in `handleWebAPITriggerMessage`/dummy handler's node-response path that the node response's sender/context matches the sender that originally created the saved callback before delivering the payload.

### Proof of Concept
Not independently executed against a running instance; the following describes the reproduction steps supported by the cited code paths:
1. Send request A: `POST /` with a valid signed `api.Message` (`MessageID: "collide-1"`, valid signature from key A, targeting a web-api-trigger DON) — handler stores callback A under `savedCallbacks["collide-1"]`.
2. Immediately send request B: another valid signed `api.Message` with `MessageID: "collide-1"` but signed by attacker key B — handler overwrites `savedCallbacks["collide-1"]` with callback B (`core/services/gateway/handlers/capabilities/handler.go:411-414`).
3. When the DON responds to the original request (still carrying `MessageID: "collide-1"`), `handleWebAPITriggerMessage` (`handler.go:148-162`) delivers that response to callback B, i.e., to the attacker's connection, not the original caller's.

Note: I did not have access to run the code or a live gateway instance to confirm timing feasibility; this analysis is based on static review of the cited source. A background engineering session with code execution/testing capability would be needed to build a concrete timing-based PoC and confirm the exploit window in practice.

### Citations

**File:** core/services/gateway/api/message.go (L54-88)
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
	if len(m.Body.Method) == 0 || len(m.Body.Method) > MessageMethodMaxLen {
		return errors.New("invalid method name length")
	}
	if strings.HasSuffix(m.Body.Method, NullChar) {
		return errors.New("method name ending with null bytes")
	}
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
}
```

**File:** core/services/gateway/gateway.go (L253-276)
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

**File:** core/services/gateway/handlers/handler.dummy.go (L62-66)
```go
func (d *dummyHandler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error {
	d.mu.Lock()
	d.savedCallbacks[msg.Body.MessageID] = &savedCallback{msg.Body.MessageID, callback}
	don := d.don
	d.mu.Unlock()
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
