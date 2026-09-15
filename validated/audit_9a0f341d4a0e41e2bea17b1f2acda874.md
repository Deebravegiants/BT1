Audit Report

## Title
Gateway `savedCallbacks` response routing keyed only by client-supplied `MessageID`, not bound to sender identity, enabling cross-user response misdirection - ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
In the legacy `WebAPIHandler` path used by the gateway for DON ID based (non service-routed) requests, pending user callbacks are stored in `savedCallbacks` keyed solely by the client-controlled `msg.Body.MessageID`, with no binding to the verified sender address and no check against overwriting an existing pending entry. A second request submitted with a colliding `MessageID` (from any signer) silently replaces the first caller's stored callback, so when the DON node later responds for that `MessageID`, the response is routed to whichever callback is currently registered rather than to the original submitter.

## Finding Description
`HandleLegacyUserMessage` registers the caller's callback with no existing-key check and no tie to `msg.Body.Sender`: [1](#0-0) 

`Message.Validate()` recovers the signer via ECDSA signature recovery and populates `m.Body.Sender`, but this value is never consulted when writing to or reading from `savedCallbacks`: [2](#0-1) 

On the response path, `handleWebAPITriggerMessage` looks the callback up purely by `MessageID`, delivers the DON's response to whatever `Callback` is stored, and deletes the entry: [3](#0-2) 

`ProcessRequest` only validates message structure and DON existence (`msg.Validate()`) before dispatching to `HandleLegacyUserMessage`; it performs no per-sender authorization or `MessageID` ownership check: [4](#0-3) 

The in-code `TODO: apply allowlist and rate-limiting here` confirms that no allowlisting/authorization gate exists yet on this legacy path: [5](#0-4) 

This matches the claim precisely: an unprivileged party who can sign an arbitrary well-formed message and knows/guesses a victim's in-flight `MessageID` can overwrite `savedCallbacks[MessageID]` before the DON node's response returns, causing the victim's response to be delivered to the attacker's callback instead.

## Impact Explanation
This is a genuine cross-user response confusion bug on the legacy `web_api_trigger` handler path: an attacker who wins the race receives another caller's DON-node response through the public gateway HTTP endpoint, which is an in-scope "cross-user response corruption" impact.

## Likelihood Explanation
Exploitation requires the attacker to both know/predict the victim's `MessageID` and win a timing race between the victim's submission and the DON's response — feasible but not trivial, since `MessageID` entropy depends entirely on the calling client's implementation (some clients could use low-entropy or predictable IDs). The absence of any allowlist, rate limit, or ownership check (as explicitly flagged by the `TODO`) means nothing besides ID guessing and timing stands between the attacker and a successful hijack, making this a real, currently-unmitigated weakness on this legacy path.

## Recommendation
- Key `savedCallbacks` by a composite of `(Sender, MessageID)` (or otherwise bind the callback to the verified `msg.Body.Sender`) rather than by `MessageID` alone.
- Reject registration of a `MessageID` that already has a pending callback instead of silently overwriting it.
- Implement the pending allowlist/rate-limiting check referenced by the `TODO` comment in `HandleLegacyUserMessage` before registering a callback.

## Proof of Concept
1. Legitimate user U signs and POSTs a `web_api_trigger` legacy JSON-RPC message with `MessageID = "X"` to the gateway's user-facing HTTP endpoint; the gateway calls `HandleLegacyUserMessage`, storing `savedCallbacks["X"] = U.callback` and forwarding the request to all DON members (`core/services/gateway/handlers/capabilities/handler.go:411-419`).
2. Before any DON member responds, attacker A generates an independent ECDSA key, crafts and signs a structurally valid message with the same `MessageID = "X"` and the same `DonID`, and submits it to the same public endpoint.
3. `HandleLegacyUserMessage` overwrites `savedCallbacks["X"]` with `A.callback` (no existing-key check, no sender binding — `handler.go:411-414`).
4. A DON node responds for `MessageID = "X"`; `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds A's callback, and delivers U's response payload to A (`handler.go:148-161`), demonstrating cross-user response misdirection. A Go unit/integration test simulating two `HandleLegacyUserMessage` calls with identical `MessageID` values from different signers, followed by a single `HandleNodeMessage` call for that `MessageID`, would confirm which callback receives the response.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-384)
```go
	// TODO: apply allowlist and rate-limiting here
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/api/message.go (L82-87)
```go
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
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
