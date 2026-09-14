Confirmed: `MessageID` is fully user/client-controlled (arbitrary string chosen by the caller before signing), and the legacy gateway "WebAPI" handler stores/looks up the pending user callback keyed **only** by that self-chosen `MessageID`, with no binding to the message sender's address. This is the closest analog to the C4 report's root cause — the system implicitly trusts an unprivileged, client-chosen identifier to route sensitive responses, without verifying that the identifier is bound to the identity that is entitled to receive the corresponding response.

### Title
Cross-user response hijacking via attacker-chosen `MessageID` collision in the legacy WebAPI gateway handler - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The legacy `WebAPIHandler` (`core/services/gateway/handlers/capabilities/handler.go`) stores the caller's callback in a shared, DON-wide map keyed solely by `msg.Body.MessageID`, a field that is entirely chosen by the unprivileged client before signing the request. Nothing in `handleWebAPITriggerMessage`/`HandleLegacyUserMessage` binds a saved callback to the sender address of the message that will eventually complete it, mirroring the `UnstakeMessenger` root cause: an identity/routing field taken from client input is assumed to symmetrically and safely identify "who gets the response," when in fact it can be freely chosen and collided by any other unprivileged caller.

### Finding Description
`HandleLegacyUserMessage` unmarshals the trigger payload, validates the message, and then does: [1](#0-0) 
storing the user's `callback` in `h.savedCallbacks[msg.Body.MessageID]` — a package-level map shared across *all* callers of the DON, keyed purely by the client-supplied `MessageID` string.

`MessageID` is validated only for length/null-suffix in `Message.Validate()`: [2](#0-1) 
It carries no uniqueness guarantee and is not derived from or bound to the sender's address — the sender is derived independently via `ExtractSigner`/`Sign`: [3](#0-2) 

When a node eventually responds, `handleWebAPITriggerMessage` looks the callback up by `MessageID` only, and sends the raw node response back to whoever is registered under that key, then deletes it: [4](#0-3) 

If a second (attacker) message reuses the exact same `MessageID` as a victim's still-pending request, the map entry is silently overwritten with the attacker's callback: [1](#0-0) 
When the DON node responds to that `MessageID` (whichever request the node happens to answer first), the first response delivered is routed to whoever's callback is currently registered under the collided key — potentially delivering the victim's response data (or vice-versa: the victim's slow callback overwriting and swallowing the attacker's own response) to the wrong unprivileged caller. This is the same class of bug as the audit finding: a request-routing/destination identity field is trusted at face value from client input, with an implicit (and false) assumption that it uniquely and safely maps back to the original requester, exactly as `UnstakeMessenger` assumed `msg.sender` on the Spoke chain was equivalent to the intended recipient on the Hub chain.

By contrast, the newer v2 `httpTriggerHandler` (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`) explicitly guards against this: `setupCallback` rejects a `requestID` that is already in-flight rather than silently overwriting it: [5](#0-4) 
and node responses are further checked against `resp.Method != ar.req.Method` and per-node-once semantics in `HandleNodeMessage` for other handlers (vault, confidential relay) — showing the project is aware of and defends against this class elsewhere, but the legacy handler path lacks the same collision-rejection.

### Impact Explanation
An unprivileged client can deliberately choose (or predict) a `MessageID`, causing the gateway to misroute another user's HTTP-trigger response to the attacker's own callback (information disclosure of another workflow's outgoing HTTP trigger acknowledgment/response), or causing the victim's request to be silently dropped/never delivered (denial of service) once the attacker's later request overwrites the map entry. This is a "cross-user response confusion" bug directly enabled by trusting a client-chosen identifier as if it inherently and safely identified the correct recipient, matching the Accept criteria for this scan.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or brute-force a victim's chosen `MessageID` and time their own request to land in the `defaultCallbackMaxAgeSec` (120s) window while the victim's request is still pending. `MessageID` is caller-chosen (not a nonce enforced to be unpredictable) and the collision-window is generous (2 minutes, pruned every 30s), and the legacy handler performs no collision rejection at all (unlike its v2 counterpart), making unintentional collisions or deliberate id-guessing feasible for any unprivileged workflow author using this path.

### Recommendation
In `core/services/gateway/handlers/capabilities/handler.go`, apply the same defense already used by the v2 handler: reject (rather than silently overwrite) a `HandleLegacyUserMessage` call whose `MessageID` already has an active entry in `savedCallbacks`, and/or scope the `savedCallbacks` key to `(sender, MessageID)` instead of `MessageID` alone so that no two distinct unprivileged callers can ever collide on the same routing key. Additionally, validate on node-response delivery that the response corresponds to the same method/request context that was saved, as the v2 and confidential-relay handlers already do.

### Proof of Concept
Not independently executed (index-based analysis only); reasoning is based on directly reading `core/services/gateway/handlers/capabilities/handler.go` (`HandleLegacyUserMessage`, `handleWebAPITriggerMessage`) and `core/services/gateway/api/message.go` (`Message.Validate`, `Sign`), which confirm `MessageID` is client-chosen, unauthenticated with respect to routing, and used as the sole map key with unconditional overwrite-on-collision, unlike the collision-rejecting `setupCallback` in the v2 `httpTriggerHandler`.

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

**File:** core/services/gateway/api/message.go (L61-66)
```go
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
```

**File:** core/services/gateway/api/message.go (L96-108)
```go
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
