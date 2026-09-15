Audit Report

## Title
Missing duplicate-check on client-supplied `MessageID` in `HandleLegacyUserMessage` allows cross-user response hijacking of the `savedCallbacks` map - ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
`HandleLegacyUserMessage` stores the caller's callback under `h.savedCallbacks[msg.Body.MessageID]` unconditionally, with no check for whether that ID already has an in-flight entry, unlike the `confidentialrelay` and `v2/http_trigger_handler` handlers in the same codebase which explicitly reject duplicate/in-flight request IDs. Since `MessageID` is a client-chosen field inside the signed message body (not derived from the sender's identity), any two distinct signers can pick the same `MessageID`, and the second submission silently overwrites the first entry in the shared map, causing the DON node's eventual response for that ID to be delivered to whichever caller's callback currently occupies the slot.

## Finding Description
`HandleLegacyUserMessage` writes to the shared map without checking existence: [1](#0-0) 

`msg.Body.MessageID` is fully attacker-controlled data included in the signed payload — it is not tied to sender identity or made unique by the signature scheme: [2](#0-1) [3](#0-2) 

The signature (`ExtractSigner`/`m.Body.Sender`) only proves who signed a given message; it does not prevent a different signer from independently choosing the identical `MessageID` string for their own, separately-signed request.

Later, when a DON node responds, the router looks up whatever callback is currently stored for that `MessageID`, deletes it, and forwards the response to it, with no cross-check that the response's originating request/sender matches the requester who registered that callback: [4](#0-3) 

`HandleNodeMessage` only validates that the responding node's address matches `msg.Body.Sender` (i.e., that the response really came from the DON node it claims to be from) — it performs no validation that the `MessageID` slot still belongs to the original requester: [5](#0-4) 

This is structurally different from the sibling `confidentialrelay` handler, which explicitly rejects a second request using an ID already in flight (`"request ID already exists"`), and from `v2/http_trigger_handler`, which rejects with `"in-flight request"`. There is also a standing `TODO: apply allowlist and rate-limiting here` comment directly above the vulnerable code path, confirming this legacy endpoint currently lacks the access controls applied elsewhere: [6](#0-5) 

## Impact Explanation
Any unprivileged client able to submit a legacy WebAPI trigger request to the gateway can collide on `MessageID` with another in-flight request and hijack the eventual DON node response intended for the original requester, receiving data not meant for them while the legitimate requester's callback is silently dropped (denial for that specific request). This matches the in-scope "gateway request impersonation / cross-user response corruption" impact category, since it corrupts the mapping between requester and response at the Gateway layer, a component with direct internet-facing exposure.

## Likelihood Explanation
Exploitation only requires the attacker to send a validly-signed legacy message (using their own key) with a `MessageID` matching or predicted from a victim's request before the DON node's response for that ID returns — no privileged role, node compromise, or credential theft is needed. The absence of a duplicate-ID check here, contrasted with the presence of such checks in the `confidentialrelay` and `v2/http_trigger_handler` code paths handling analogous requests, indicates this specific legacy code path was not hardened consistently.

## Recommendation
Add the same duplicate-ID rejection used in `confidentialrelay`/`v2/http_trigger_handler` to `HandleLegacyUserMessage`: check `h.savedCallbacks[msg.Body.MessageID]` for an existing, unexpired entry before storing, and reject with an error (e.g., "in-flight request") rather than overwriting. Additionally, scope callback storage by a composite key (sender + MessageID) and validate that a node's response is tied to the exact original requester before dispatching it to a saved callback.

## Proof of Concept
1. Victim signs and sends a legacy `web_api_trigger` message with `MessageID = "X"`; gateway stores `savedCallbacks["X"] = victimCallback` (handler.go:411-412) and forwards the request to all DON members.
2. Before a DON node responds, attacker signs and sends their own legacy message also using `MessageID = "X"`; the handler overwrites `savedCallbacks["X"] = attackerCallback` with no error, since no existence check is performed.
3. A DON node's response for `MessageID = "X"` (originally destined for the victim) arrives at `handleWebAPITriggerMessage`, which looks up and deletes `savedCallbacks["X"]`, finding the attacker's callback, and delivers the response to the attacker (handler.go:148-161).
4. This can be directly reproduced as a Go unit test analogous to `TestConfidentialRelayHandler_DuplicateRequestID` (confidentialrelay/handler_test.go:863-881): call `HandleLegacyUserMessage` twice with the same `MessageID` but different callbacks/signers, then call `HandleNodeMessage`/`handleWebAPITriggerMessage` and assert that the second (attacker) callback receives the response instead of an error being returned on the duplicate submission.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L248-267)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	msg, err := common.ValidatedMessageFromResp(resp)
	if err != nil {
		return err
	}
	if msg.Body.Sender != nodeAddr {
		return errors.New("message sender mismatch when reading from node ")
	}
	start := time.Now()
	switch msg.Body.Method {
	case MethodWebAPITrigger:
		err = h.handleWebAPITriggerMessage(ctx, msg, nodeAddr)
	case MethodWebAPITarget, MethodComputeAction, MethodWorkflowSyncer:
		err = h.handleWebAPIOutgoingMessage(ctx, msg, nodeAddr)
	default:
		err = fmt.Errorf("unsupported method: %s", msg.Body.Method)
	}
	h.metrics.recordHandleDuration(ctx, time.Since(start), msg.Body.Method, err == nil)
	return err
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-396)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/api/message.go (L42-52)
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
```

**File:** core/services/gateway/api/message.go (L90-108)
```go
// Message signatures are over the following data:
//  1. MessageID aligned to 128 bytes
//  2. Method aligned to 64 bytes
//  3. DonID aligned to 64 bytes
//  4. Receiver (in hex) aligned to 42 bytes
//  5. Payload (raw bytes before parsing)
func (m *Message) Sign(privateKey *ecdsa.PrivateKey) error {
	if m == nil {
		return errors.New("nil message")
	}
	rawData := GetRawMessageBody(&m.Body)
	signature, err := gw_common.SignData(privateKey, rawData...)
	if err != nil {
		return err
	}
	m.Signature = utils.StringToHex(string(signature))
	m.Body.Sender = strings.ToLower(crypto.PubkeyToAddress(privateKey.PublicKey).Hex())
	return nil
}
```
