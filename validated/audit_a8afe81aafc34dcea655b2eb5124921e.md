### Title
Cross-user response confusion via unscoped, client-controlled `MessageID` in gateway legacy WebAPI callback map - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The bug-class hint from the report is "a shared resource is only tracked/returned by a single key, so a second, unrelated party's later interaction lets them capture what belongs to the first party." In the Chainlink gateway `capabilities` handler, the callback used to deliver a `web_api_trigger` response back to an external caller is stored in a process-wide map keyed **only** by the client-supplied `MessageID`, with no binding to the sender/session that submitted it [1](#0-0) . Because `MessageID` comes straight from the user-controlled JSON-RPC request ID [2](#0-1) , any unprivileged caller of the gateway can supply a `MessageID` colliding with another in-flight request and hijack the map entry, causing the DON's response to be delivered to the attacker's callback instead of the legitimate caller's.

### Finding Description
`HandleLegacyUserMessage` accepts a `web_api_trigger` request from an external (unprivileged) HTTP client, and stores the client's response `callback` in `h.savedCallbacks` keyed purely by `msg.Body.MessageID`:

```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
``` [1](#0-0) 

`MessageID` is taken verbatim from the incoming JSON-RPC request `ID` field by `ValidatedMessageFromReq`/legacy message parsing (`m.Body.MessageID = req.ID`), with only length/null-byte checks in `Message.Validate()` — no uniqueness or sender-binding is enforced [2](#0-1) [3](#0-2) .

When the DON eventually responds with the same `MessageID` (echoed by the node), `handleWebAPITriggerMessage` looks the `MessageID` up in the map, deletes it, and forwards the response to whatever callback is currently stored there:

```go
h.mu.Lock()
savedCb, found := h.savedCallbacks[msg.Body.MessageID]
delete(h.savedCallbacks, msg.Body.MessageID)
h.mu.Unlock()

if found {
    // Send first response from a node back to the user, ignore any other ones.
    codec := api.JSONRPCCodec{}
    return savedCb.SendResponse(...)
}
``` [4](#0-3) 

Because the map is not scoped by sender/owner (unlike the `ProxyCall`/stablecoin case where one asset type was tracked but not returned per-owner), any second unprivileged caller who submits a request with the **same `MessageID`** while the first request is still pending will overwrite the map entry. When the legitimate node response for the original request finally arrives, it is delivered to the attacker's callback (`savedCb.SendResponse`) — i.e., the attacker receives a response payload intended for a different user's request. This is directly analogous to the reported bug class: a shared resource (the pending-response slot) is checked/returned using only a coarse key, ignoring the finer-grained ownership that should gate delivery — exactly the "missing per-party check before handing back the asset/response" pattern in the original report.

### Impact Explanation
An unprivileged external client of the gateway's legacy WebAPI trigger endpoint can:
- Cause responses (including any DON/workflow computed data returned via `web_api_trigger`) belonging to another user's request to be delivered to itself, if it can predict or guess/brute-force another caller's chosen `MessageID` and race the timing window before the real response arrives.
- Deny service to the legitimate caller, whose callback is silently overwritten and dropped (their request will simply hang until callback pruning/timeout), since the `found` branch only delivers to whichever callback is currently in the map.

This matches the required "cross-user response confusion" acceptance criterion: unauthorized disclosure of one user's response payload to another unprivileged user via ID collision in a shared, unscoped resource map.

### Likelihood Explanation
Exploitability depends on the attacker being able to submit a request with the exact same `MessageID` as an in-flight victim request before the victim's response returns. If `MessageID`s are predictable, low-entropy, or attacker-supplied without validation against collision (only length and null-byte checks are enforced — no format/uniqueness/sender-binding requirement is imposed by `Message.Validate()`), an attacker controlling request timing (e.g., flooding the gateway with many candidate `MessageID`s during the response window) has a realistic chance of collision, especially in busy/production DONs handling many concurrent legacy requests with the same DON config. Since `HandleLegacyUserMessage` is reachable directly from unprivileged external users of the gateway (no auth/allowlist is applied at this point — the code even has a `// TODO: apply allowlist and rate-limiting here` comment) [5](#0-4) , the attack surface is directly internet-facing.

### Recommendation
Scope the `savedCallbacks` map key (and the corresponding lookup on node response) by both `MessageID` and the authenticated sender/session identity (e.g., `sender + "/" + MessageID`), not by `MessageID` alone, so that a collision from an unrelated caller cannot overwrite or hijack another user's pending callback. Additionally, enforce that `MessageID` is unique per outstanding request (reject duplicate in-flight IDs) and apply the still-pending allowlist/rate-limiting TODO before allowing entry into the callback map.

### Proof of Concept
1. User A sends a `web_api_trigger` legacy request to the gateway with `MessageID = "X"`. `HandleLegacyUserMessage` stores `savedCallbacks["X"] = callbackA` and forwards the request to DON members.
2. Before the DON responds, Attacker B sends a `web_api_trigger` legacy request to the same gateway/DON, also using `MessageID = "X"` (guessed or brute-forced). This overwrites `savedCallbacks["X"] = callbackB`.
3. The DON node eventually replies for User A's original request, echoing `MessageID = "X"`. `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `callbackB` (Attacker B's callback), deletes the entry, and calls `callbackB.SendResponse(...)`.
4. Attacker B receives User A's response payload; User A's original callback never fires and eventually times out/gets pruned.

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

**File:** core/services/gateway/handlers/common/message_util.go (L34-58)
```go
// ValidatedMessageFromReq validated and extracts a legacy Gateway Message
// from params field of JSON-RPC request
func ValidatedMessageFromReq(req *jsonrpc.Request[json.RawMessage]) (*api.Message, error) {
	if req.Version != "2.0" {
		return nil, errors.New("incorrect jsonrpc version")
	}
	if req.Method == "" {
		return nil, errors.New("empty method field")
	}
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
	var m api.Message
	err := json.Unmarshal(*req.Params, &m)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal request params: %w", err)
	}
	m.Body.Method = req.Method
	m.Body.MessageID = req.ID
	err = m.Validate()
	if err != nil {
		return nil, err
	}
	return &m, nil
}
```

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
