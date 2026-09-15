The claim is verified against the actual source and holds up.

Audit Report

## Title
Unauthenticated MessageID collision in legacy WebAPI trigger handler causes response misdelivery/loss - (File: `core/services/gateway/handlers/capabilities/handler.go`)

## Summary
`HandleLegacyUserMessage` stores a caller's response callback in `h.savedCallbacks` keyed solely by the caller-supplied `msg.Body.MessageID`, with an unconditional overwrite and no in-flight/uniqueness check, unlike the newer v2 HTTP trigger handler which explicitly rejects duplicate in-flight request IDs. A second unrelated request reusing the same `MessageID` silently evicts the first caller's callback, causing that caller's response to be lost and misdelivered to the second caller.

## Finding Description
`HandleLegacyUserMessage` performs payload decoding, timestamp/staleness validation, and method checks, but explicitly defers authorization ("// TODO: apply allowlist and rate-limiting here" at line 384), then unconditionally overwrites the shared map: [1](#0-0) 

`MessageID` is decoded directly from the client-controlled JSON-RPC request ID at the gateway ingress and is only bounded by a 200-character length check, with no uniqueness enforcement: [2](#0-1) 

When a node responds, `handleWebAPITriggerMessage` looks up and deletes the callback purely by `MessageID`, delivering the response to whatever callback currently occupies that slot with no verification that it belongs to the original requester: [3](#0-2) 

This is confirmed to differ from the v2 handler, which has an explicit in-flight duplicate-ID rejection test (`ErrConflict`) — a protection entirely absent from the legacy path. The orphaned first callback is only cleaned up after `CallbackMaxAgeSec` (120s default) via `pruneCallbacks`, during which the original caller receives nothing.

## Impact Explanation
This maps to the in-scope "cross-user response corruption" / "gateway request impersonation" impact class: an unprivileged caller's legacy trigger response can be misdirected to another unprivileged caller, and the original caller experiences a silent denial of service (up to 120s hang, then permanent loss). This is a genuine logic flaw in code that ties responses back to requesters without an ownership check, matching the reported bug class.

## Likelihood Explanation
Exploitation requires only two unauthenticated/unprivileged JSON-RPC requests to the legacy `web_api_trigger` gateway endpoint sharing the same caller-chosen `MessageID`, won as a race before the first DON response arrives. No credential elevation, host access, or malicious-node assumption is needed — this is directly reachable by any client hitting the gateway's public legacy endpoint, and the timing window (multi-hop gateway → DON → gateway round trip) is generous enough to be practically winnable.

## Recommendation
Add the same in-flight/duplicate-`MessageID` guard used in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go` to `HandleLegacyUserMessage`: check `h.savedCallbacks` for an existing non-expired entry under the same key before insertion and reject (rather than overwrite) with an error response; additionally consider scoping the key by sender/signer identity in addition to `MessageID`.

## Proof of Concept
1. Send legacy request R1 with `Body.MessageID = "X"` to the gateway's legacy webapi-trigger endpoint; `savedCallbacks["X"] = cb1` is stored and forwarded to DON members.
2. Before DON responds, send legacy request R2 with the same `Body.MessageID = "X"`; the gateway overwrites `savedCallbacks["X"] = cb2` at `handler.go:412` with no error returned to either caller.
3. When the DON responds to R1 with `MessageID = "X"`, `handleWebAPITriggerMessage` (`handler.go:148-161`) looks up `savedCallbacks["X"]`, finds `cb2`, deletes it, and delivers R1's response to R2's caller. R1's caller (`cb1`) never receives a response and times out after `CallbackMaxAgeSec` (120s), at which point `pruneCallbacks` (`handler.go:299-312`) silently discards the orphaned reference (already discarded from the map upon overwrite, but conceptually the caller is left hanging).
   This can be codified as a Go unit test analogous to `http_trigger_handler_test.go`'s "duplicate request ID" test, but asserting the (currently absent) rejection in `HandleLegacyUserMessage`.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
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
