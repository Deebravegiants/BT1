Audit Report

## Title
Cross-user response hijacking via attacker-controlled `MessageID` collision in WebAPI Gateway legacy trigger handler - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`HandleLegacyUserMessage` stores a pending callback in `h.savedCallbacks` keyed solely by the caller-supplied `msg.Body.MessageID`, without checking for an existing entry or binding the entry to the requester's signer/identity. When the DON later responds, `handleWebAPITriggerMessage` looks up the callback purely by `MessageID` and forwards the response, allowing any second caller who submits a request with a colliding `MessageID` to overwrite the pending callback and receive another user's response.

## Finding Description
`HandleLegacyUserMessage` unconditionally overwrites the map entry: [1](#0-0) 

`handleWebAPITriggerMessage` retrieves and deletes whatever callback is currently registered under that `MessageID` and delivers the DON's response to it: [2](#0-1) 

`Message.Validate()` extracts a `Sender` from the signature (`ExtractSigner`), but this value is only used later for `HandleNodeMessage`'s check that the message came from the expected connected DON node (`msg.Body.Sender != nodeAddr`, i.e., verifying node identity on the Gateway↔DON link), not for verifying that a request's `MessageID` "belongs" to the original requester: [3](#0-2) 

The gateway's dispatch path (`gateway.ProcessRequest`) performs no per-sender authorization before calling `HandleLegacyUserMessage`; it only calls `msg.Validate()` (signature format check) and routes by `DonID`/`Method`, meaning any caller capable of producing a valid ECDSA signature over any body can reach this handler with any `MessageID` of their choosing. The `dummyHandler.HandleLegacyUserMessage` reference implementation exhibits the identical unconditional-overwrite pattern, and its `HandleNodeMessage`'s `nodeAddr != msg.Body.Sender` check is likewise a node-identity check, not an owner-of-callback check — so the claim's suggestion that the dummy handler already fixes this is incorrect, but this doesn't change the fact that the real handler lacks any binding between the saved callback and the original submitter.

Illustrating realistic likelihood, the provided reference client tool defaults its `MessageID` to a static, low-entropy value ("12345") unless the caller overrides it via a flag, showing that in practice `MessageID`s are not guaranteed to be high-entropy/unpredictable, increasing the practical chance of collision either accidentally or through deliberate attack.

## Impact Explanation
This maps to the "cross-user response corruption" impact class explicitly listed as in-scope. A successful collision lets an unrelated caller receive the payload/result intended for another user's `web_api_trigger` request — response data intended for one caller is silently redirected to a different caller due to a broken assumption that `MessageID` uniquely and safely identifies the original requester.

## Likelihood Explanation
Exploitability requires the attacker to submit a request with a `MessageID` matching a victim's in-flight request within the `CallbackMaxAgeSec` window (default 120s): [4](#0-3) 
No credential above "ability to sign an arbitrary message with any keypair" is required to reach `HandleLegacyUserMessage`, since the gateway performs no allowlist/sender check at this layer (marked as a `TODO` in the code): [5](#0-4) 
Likelihood is not purely theoretical: the shipped reference invocation tool uses a static default `MessageID`, and nothing in the gateway enforces uniqueness or randomness of this field, so collisions are plausible in real deployments where callers reuse or predict IDs (e.g., retries, idempotency keys, or scripted/tooling-driven submissions).

## Recommendation
Bind each `savedCallback` entry to the sender/signer computed in `Message.Validate()` and verify sender identity (or scope the map key to `(Sender, MessageID)`) rather than `MessageID` alone. Additionally, reject registration of a `MessageID` if an active, non-expired callback already exists (fail closed) instead of silently overwriting it, matching the recommendation in the underlying report.

## Proof of Concept
1. Victim signs and submits a legacy `web_api_trigger` JSON-RPC request to the gateway with `Body.MessageID = "X"`. `HandleLegacyUserMessage` stores `savedCallbacks["X"] = victimCallback` and forwards to all DON members.
2. Before the DON responds, an attacker — using their own independently generated keypair, requiring no special credential — submits their own signed legacy request also using `Body.MessageID = "X"`. Because `msg.Validate()` only validates signature format/length and does not check for MessageID ownership or uniqueness, this call succeeds and overwrites `savedCallbacks["X"] = attackerCallback`.
3. When the DON node completes the victim's original request and replies with `MessageID = "X"`, `handleWebAPITriggerMessage` (`handler.go` L148-161) looks up `savedCallbacks["X"]`, finds the attacker's callback, deletes the entry, and forwards the victim's response payload to the attacker via `SendResponse`.

This can be verified with a Go unit test in `core/services/gateway/handlers/capabilities/handler_test.go` extending `TestHandlerReceiveHTTPMessageFromClient`: call `HandleLegacyUserMessage` twice with the same `MessageID` from two different signing keys/callbacks, then call `HandleNodeMessage` with the DON's response for the first (victim) request, and assert that the second (attacker) callback receives the response instead of the first.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L248-255)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	msg, err := common.ValidatedMessageFromResp(resp)
	if err != nil {
		return err
	}
	if msg.Body.Sender != nodeAddr {
		return errors.New("message sender mismatch when reading from node ")
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
