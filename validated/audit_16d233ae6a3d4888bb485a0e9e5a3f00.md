Confirmed: `MessageID` is fully attacker-controlled — it is part of the client-supplied, signed `Message` and is only checked for length/null-suffix in `Message.Validate()` [1](#0-0) . Any unprivileged caller can therefore submit two legacy `web_api_trigger` requests using the *same* `MessageID` in quick succession through the internet-facing gateway entrypoint `gateway.ProcessRequest` [2](#0-1) .

### Title
Race condition in `savedCallbacks` map allows cross-request response hijacking - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`handler.HandleLegacyUserMessage` stores a caller's `Callback` in the shared `savedCallbacks` map keyed only by the client-supplied `msg.Body.MessageID`, with no check for an existing, still-pending entry, and no per-connection/per-user scoping. This mirrors the reported `SignMessage` race: concurrent calls to the same function overwrite in-flight state, letting one request's execution/response reach the wrong caller.

### Finding Description
In `HandleLegacyUserMessage`, the handler unconditionally overwrites any existing entry for the same `MessageID`:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()
``` [3](#0-2) 

Later, when a DON node responds, `handleWebAPITriggerMessage` looks up and deletes whatever callback currently sits at that key and delivers the response to it, regardless of which caller originally registered it:
```go
h.mu.Lock()
savedCb, found := h.savedCallbacks[msg.Body.MessageID]
delete(h.savedCallbacks, msg.Body.MessageID)
h.mu.Unlock()
...
return savedCb.SendResponse(...)
``` [4](#0-3) 

`MessageID` is entirely attacker-supplied — the only server-side validation is length and null-suffix checks [1](#0-0) , with no uniqueness or per-sender enforcement. `gateway.ProcessRequest`, the HTTP-facing entrypoint reachable by any unprivileged client, decodes the raw request and forwards straight to `HandleLegacyUserMessage` with a fresh callback per HTTP call [5](#0-4) .

If an attacker sends two (or more) requests with the same `MessageID` before the first completes, the second overwrites the first's saved callback. When the DON responds to the first request, the response is delivered through the *second* caller's HTTP connection instead of the first's — a cross-user response confusion analogous to the reported overwrite-in-flight-state bug. The original caller instead times out or receives no response, while the attacker's connection receives content it never triggered (e.g., another tenant's trigger-response payload for a shared/legacy DON), since callback delivery has no ownership check.

### Impact Explanation
This is a request/response confusion vulnerability on the internet-facing gateway: one user's response payload can be delivered to a different, attacker-controlled HTTP connection purely by MessageID collision, without any authentication bypass needed beyond crafting a duplicate ID. Depending on payload sensitivity (trigger execution results), this can leak response data across callers. Impact is bounded by what data flows through `web_api_trigger`/`web_api_target` responses, but is a genuine cross-user data exposure.

### Likelihood Explanation
Likelihood is moderate-to-high: `MessageID` is fully client-controlled and only length/format-checked, so no special access or luck is required — an attacker only needs to send two requests back-to-back with an identical, guessable, or observed `MessageID` (e.g., replaying/matching a victim's ID) within the window before the first completes/prunes. The `mu.Lock`/`mu.Unlock` around the map write is present but only protects the map data structure, not the logical invariant that an ID should not be silently reassigned to a new caller.

### Recommendation
In `HandleLegacyUserMessage`, before inserting into `savedCallbacks`, check whether an entry for `msg.Body.MessageID` already exists and is still pending (not expired); if so, reject the new request with a duplicate/conflict error instead of silently overwriting the existing callback. Consider additionally scoping cache keys by sender/connection identity (e.g., `Sender+MessageID`) rather than `MessageID` alone, since `Message.Validate()` already derives `Body.Sender` from the signature [6](#0-5) .

### Proof of Concept
1. Attacker crafts a valid signed legacy `web_api_trigger` `Message` with `MessageID = "X"` and sends it to the gateway's user-facing HTTP endpoint, initiating `HandleLegacyUserMessage`, which registers `savedCallbacks["X"] = callbackA` and forwards the trigger to all DON nodes [7](#0-6) .
2. Before the DON responds, attacker immediately sends a second request reusing `MessageID = "X"` (possibly on a second connection or after guessing/observing a victim's in-flight ID), causing `savedCallbacks["X"]` to be overwritten with `callbackB`.
3. When any DON node's trigger response for `MessageID = "X"` arrives, `handleWebAPITriggerMessage` retrieves `callbackB` (not `callbackA`) and sends the response over the attacker's HTTP connection instead of the original caller's [4](#0-3) .
4. The original caller's request times out (`callback.Wait(ctx)` in `gateway.ProcessRequest` never resolves) [8](#0-7) , while the attacker receives the response payload intended for the other user.

### Citations

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

**File:** core/services/gateway/api/message.go (L82-87)
```go
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
```

**File:** core/services/gateway/gateway.go (L221-279)
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
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
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

**File:** core/services/gateway/gateway.go (L281-288)
```go
	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-160)
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
