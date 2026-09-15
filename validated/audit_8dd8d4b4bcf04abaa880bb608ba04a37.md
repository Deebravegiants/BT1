Audit Report

## Title
Attacker-chosen `MessageID` collision overwrites another user's pending gateway callback, causing cross-user response delivery - ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
`HandleLegacyUserMessage` stores a user's response `callback` in the shared `savedCallbacks` map keyed solely by the client-controlled `msg.Body.MessageID`, with no existing-key check, so a second request reusing the same `MessageID` silently overwrites the first user's callback entry. When a DON node later responds with that `MessageID`, `handleWebAPITriggerMessage` looks up and delivers the response to whichever callback currently occupies that map slot, allowing an unprivileged attacker to intercept a victim's Gateway response.

## Finding Description
`HandleLegacyUserMessage` writes directly to the map without checking for a pre-existing entry:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()
``` [1](#0-0) 

`MessageID` is a plain client-supplied string bounded only by length (`MessageIDMaxLen`) and non-null-terminated suffix — it is not derived from the sender's address or a server-generated nonce, so distinct signers can independently choose the same value, and `Validate()` performs no uniqueness check across senders. [2](#0-1) 

When a DON node responds, the handler looks up and deletes the entry purely by `MessageID` and dispatches to whatever callback is stored there at that moment:
```go
h.mu.Lock()
savedCb, found := h.savedCallbacks[msg.Body.MessageID]
delete(h.savedCallbacks, msg.Body.MessageID)
h.mu.Unlock()

if found {
    codec := api.JSONRPCCodec{}
    return savedCb.SendResponse(handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError})
}
``` [3](#0-2) 

The outer `gateway.ProcessRequest` flow confirms this is reachable directly from an unprivileged, unauthenticated-by-role HTTP client: it decodes the raw request, invokes `HandleLegacyUserMessage`, and blocks on `callback.Wait(ctx)` for the eventual result. [4](#0-3) 

No other check (signature validation, allowlist, or per-sender scoping of `savedCallbacks`) mitigates this: signature validation only confirms the message was signed by *some* valid key, not that the `MessageID` is unique or bound to that sender — `HandleLegacyUserMessage` explicitly notes `// TODO: apply allowlist and rate-limiting here`, and there is no equivalent of the `activeRequests` existing-ID guard present in the newer `vault`/`confidentialrelay` handlers.

Exploit sequence: victim submits a request with `MessageID = "X"`, gateway stores `victimCallback` under key `"X"` and fans out to DON members; attacker submits their own signed message reusing `MessageID = "X"` before a node responds, overwriting `savedCallbacks["X"]` with `attackerCallback`; when a DON node responds to the victim's original fan-out (same `MessageID`), the handler delivers the victim's response payload to `attackerCallback` instead.

## Impact Explanation
This is a concrete cross-user response confusion/corruption bug in the Gateway's legacy user-message handling path: an unprivileged client can hijack another user's in-flight `web_api_trigger` response and simultaneously deny/delay the victim's own response delivery. This maps to the in-scope "cross-user response corruption" impact class for the Gateway component.

## Likelihood Explanation
Exploitation requires only the ability to sign and submit a normal message to the Gateway's user-facing endpoint (no elevated role) and to guess or observe an in-flight `MessageID`, which is entirely attacker/client-chosen and not validated for uniqueness across senders — the race window is realistic given that fan-out to DON nodes and their processing/response introduces natural latency.

## Recommendation
Scope `savedCallbacks` keys by a tuple including the sender/signer address in addition to `MessageID` (e.g., `sender+":"+MessageID`), and/or add an existing-key guard in `HandleLegacyUserMessage` that rejects a request with a conflict error when the `MessageID` is already active, mirroring the `activeRequests` guard in the `vault`/`confidentialrelay` handlers. Additionally, `handleWebAPITriggerMessage` should verify that the DON node's response actually corresponds to the same original requester before dispatching to the saved callback.

## Proof of Concept
Extend `TestHandlerReceiveHTTPMessageFromClient` in `core/services/gateway/handlers/capabilities/handler_test.go`:
1. Call `handler.HandleLegacyUserMessage(ctx, victimMsg, victimCallback)` with `MessageID = "collide-1"`.
2. Call `handler.HandleLegacyUserMessage(ctx, attackerMsg, attackerCallback)` with the same `MessageID = "collide-1"` (different valid signer), before any node response is processed.
3. Call `handler.HandleNodeMessage(ctx, respForCollide1, nodes[0].Address)`, simulating the DON node's response to the victim's original fan-out.
4. Observe `attackerCallback.Wait(ctx)` returns the victim's response payload, while `victimCallback.Wait(ctx)` never resolves (times out).

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

**File:** core/services/gateway/api/message.go (L42-88)
```go
type MessageBody struct {
	MessageID string `json:"message_id"`
	Method    string `json:"method"`
	DonID     string `json:"don_id"`
	Receiver  string `json:"receiver"`
	// Service-specific payload, decoded inside the Handler.
	Payload json.RawMessage `json:"payload,omitempty"`

	// Fields only used locally for convenience. Not serialized.
	Sender string `json:"-"`
}

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

**File:** core/services/gateway/gateway.go (L267-288)
```go
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

	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
	}
```
