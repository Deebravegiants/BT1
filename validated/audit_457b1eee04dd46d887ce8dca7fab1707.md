This confirms the technical claim fully: `ProcessRequest` reaches `HandleLegacyUserMessage` for any request bearing a `DonID`, with no allowlist/authentication check beyond signature-format validation via `msg.Validate()`, which does not check identity against the message ID or perform per-sender authorization. The `TODO: apply allowlist and rate-limiting here` comment in `handler.go` at line 384 confirms that no additional access control exists at this layer today.Confirmed: `HandleLegacyUserMessage` writes to `h.savedCallbacks` unconditionally with a `TODO: apply allowlist and rate-limiting here` comment above it, and no per-sender authorization exists at this layer before the write. The claim's technical details are accurate and match the actual code.

Audit Report

## Title
Unprivileged clients can hijack/DoS Web API trigger responses by front-running `MessageID` before the legitimate request in the Gateway's WebAPI capability handler - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
The Gateway's `webapicapabilities.handler.HandleLegacyUserMessage` stores a callback for a pending user request keyed only by the client-supplied `MessageID`, with no uniqueness check before insertion, unlike sibling handlers (`httpTriggerHandler.setupCallback`, vault `handler.newActiveRequest`) which explicitly reject collisions. A second request using the same `MessageID` silently overwrites the first entry in `h.savedCallbacks`, so a subsequent DON response for that ID is delivered to whichever caller's callback occupies the slot last.

## Finding Description
`HandleLegacyUserMessage` performs an unconditional map write at [1](#0-0) , immediately preceded by a `TODO: apply allowlist and rate-limiting here` comment at [2](#0-1) , confirming no per-sender authorization exists at this point. `msg.Body.MessageID` is attacker-controlled and validated only for length/format (not uniqueness or ownership) in `Message.Validate` at [3](#0-2) . This handler is reached from any client via the Gateway's public `ProcessRequest` entry point, which routes DonID-bearing legacy requests straight to `HandleLegacyUserMessage` after only signature/format validation (`msg.Validate()`), with no allowlist check at that layer either, at [4](#0-3) . When a node later responds, `handleWebAPITriggerMessage` looks up and deletes the entry by `MessageID` and delivers to whichever callback occupies that slot, at [5](#0-4) . This contrasts with `httpTriggerHandler.setupCallback`, which explicitly rejects ID collisions with `jsonrpc.ErrConflict` [6](#0-5) , and the vault handler's `newActiveRequest`, which rejects with "request ID already exists" [7](#0-6) .

## Impact Explanation
A colliding `MessageID` submitted before the legitimate response arrives causes the earlier caller's `savedCallback` to be overwritten; the victim's `ProcessRequest` call then blocks on `callback.Wait(ctx)` until timeout [8](#0-7) , and the DON's eventual response is delivered to the attacker's callback instead. This is a griefing/DoS on a specific request and a response-misdelivery condition, matching in-scope categories such as gateway request impersonation/cross-user response corruption.

However, this requires the attacker to (a) know or predict the victim's `MessageID` and (b) win a timing race before the DON node responds — the actual trigger delivery latency to the DON and back is typically short. Additionally, the payload of a webapi trigger request delivered to a workflow is validated against `allowedSenders`/`allowedTopics` at the workflow layer (`core/capabilities/webapi/trigger/trigger.go`), meaning the substantive trigger content itself is still checked against sender authorization downstream — the vulnerability here is specifically about callback/response routing at the Gateway layer, not about forging trigger data into a workflow.

## Likelihood Explanation
Exploitability is highly conditional: it requires knowledge of an in-flight victim `MessageID` and precise timing to insert a colliding request between the victim's request and the DON's response — a narrow race window, not a straightforward guess/collision attack. There is no evidence in the code that `MessageID`s are predictable or observable to third parties by design; the claim itself acknowledges this is speculative ("if callers use non-random or otherwise guessable IDs"). No PoC demonstrating actual `MessageID` predictability or a successful race was provided — the claim's PoC section is a description of the code flow, not an executed reproduction with timing analysis.

## Recommendation
Add a uniqueness check in `HandleLegacyUserMessage` before inserting into `h.savedCallbacks`, mirroring `httpTriggerHandler.setupCallback` and `vault handler.newActiveRequest`, rejecting a new request if an active (non-expired) callback already exists for the given `MessageID`.

## Proof of Concept
Not independently reproduced with concrete timing/race evidence; the described PoC is a code-path walkthrough asserting a race is possible, not a demonstrated exploit with realistic `MessageID` acquisition and win-condition timing.

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

**File:** core/services/gateway/api/message.go (L54-61)
```go
func (m *Message) Validate() error {
	if m == nil {
		return errors.New("nil message")
	}
	if len(m.Signature) != MessageSignatureHexEncodedLen {
		return errors.New("invalid hex-encoded signature length")
	}
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
```

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
