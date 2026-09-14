### Title
Cross-user response confusion via unauthenticated `MessageID` collision in gateway legacy callback map - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The gateway's legacy WebAPI trigger flow stores per-request response callbacks in a shared map keyed only by the caller-supplied `MessageID`, with no ownership check before insertion and no uniqueness enforcement at the gateway ingress. Any unprivileged client that can reach the gateway's `ProcessRequest` entrypoint can submit a request with a `MessageID` that collides with another in-flight request, silently overwriting that request's saved callback. When a DON node later responds, the response is delivered to whichever callback currently occupies that `MessageID` slot — potentially the attacker's — resulting in cross-user response confusion, directly analogous to CVE-2021-46701's "receive/emit events from a socket that interferes with another party's session" over a shared multiplexed transport.

### Finding Description
The public-facing gateway entrypoint decodes a client request and, for the legacy path, calls into the DON handler with a caller-supplied callback: [1](#0-0) 

`HandleLegacyUserMessage` then stores the callback in a shared map keyed solely by the message body's `MessageID`, without checking whether an entry already exists for that ID: [2](#0-1) 

Compare this to the equivalent node-side `responses` map used for outgoing gateway requests, which explicitly rejects a duplicate ID to avoid exactly this class of bug: [3](#0-2) 

No such duplicate-detection exists in `HandleLegacyUserMessage`. When any DON node later sends a `MethodWebAPITrigger` response, the handler looks the callback up purely by `MessageID`, delivers the response to it, and deletes the entry — first node response for that ID wins, and it is delivered to whatever caller's callback is currently registered under that ID: [4](#0-3) 

Because `MessageID` is part of the client-controlled message body and the callback map has no per-caller/session scoping, two different unprivileged callers hitting the same DON with the same `MessageID` will race for the same callback slot. There is no cryptographic or session binding between the `MessageID` and the identity of the caller that owns the callback — only the eventual node response's signature is checked against the node, not against which client's callback should receive it.

### Impact Explanation
An unprivileged client can cause response data destined for another client's WebAPI trigger request to be delivered to itself instead (information disclosure of another workflow's trigger payload), or can cause a victim's request to silently receive a stale/attacker-influenced response, or to never resolve properly (denial of the victim's request). This mirrors the CVE's core defect class: a shared, unauthenticated multiplexing key (`MessageID`, analogous to the websocket event channel in PreMiD) allows one party to intercept or inject into another party's in-flight interaction.

### Likelihood Explanation
Exploitability depends on `MessageID` collision, which requires either predictable/guessable IDs or unlucky/attacker-influenced ID reuse (e.g., a caller replaying or brute-forcing IDs against a busy handler with up to `defaultMaxSavedCallbacks = 20000` concurrent entries). If upstream SDK/workflow code always generates cryptographically random UUIDs for `MessageID`, practical likelihood is reduced, but this is not enforced or validated at the gateway layer itself — the root-cause gap (missing duplicate/ownership check) exists regardless of caller-side ID generation practices.

### Recommendation
- In `HandleLegacyUserMessage`, reject the request (or generate a fresh internal correlation ID) if `h.savedCallbacks[msg.Body.MessageID]` already exists, mirroring the duplicate-check already present in `outgoing_connector_handler.go`'s `responses.new`.
- Scope the callback map key by both `MessageID` and caller identity (e.g., signer/sender address or session key) so that a collision cannot cross caller boundaries.
- Consider deriving `MessageID` server-side (gateway-generated) rather than trusting the client-supplied value for callback correlation.

### Proof of Concept
1. Caller A sends a legacy request through the gateway's public HTTP/WS endpoint (`gateway.ProcessRequest`) with `Body.Method = web_api_trigger` and `Body.MessageID = "X"`. This registers `savedCallbacks["X"] = callbackA` and forwards the request to all DON members.
2. Before a DON node responds, Caller B (unprivileged, no relationship to A) sends its own legacy request with the same `Body.MessageID = "X"`. This overwrites `savedCallbacks["X"]` with `callbackB` (no uniqueness check in `handler.go:411-414`).
3. A DON node responds (in response to either A's or B's forwarded request) with `MethodWebAPITrigger` and `MessageID = "X"`.
4. `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `callbackB`, deletes the entry, and delivers the node's response to Caller B — even if the response actually corresponds to Caller A's original request/payload.

Note: I was unable to fully verify from the indexed code whether any caller-side SDK enforces random/unique `MessageID` generation before this gateway code path is reached; if such enforcement exists upstream, it would reduce (but not eliminate, since the gateway API is directly reachable) the practical likelihood of exploitation.

### Citations

**File:** core/services/gateway/gateway.go (L253-272)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-420)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L449-462)
```go
func (r *responses) new(id string) (chan *api.Message, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	_, ok := r.chs[id]
	if ok {
		return nil, fmt.Errorf("already have response for id: %s", id)
	}

	// Buffered so we don't wait if sending
	ch := make(chan *api.Message, 1)
	r.chs[id] = ch
	return ch, nil
}
```
