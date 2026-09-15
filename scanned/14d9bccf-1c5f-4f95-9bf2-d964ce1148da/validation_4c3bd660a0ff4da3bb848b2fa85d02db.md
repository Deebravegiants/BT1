## Analysis Result

I confirmed that `MessageID` in the legacy gateway path (`core/services/gateway/api/message.go`, `Message.Validate()`) is entirely client-chosen — it is only length- and null-suffix-checked, and is never derived from or bound to the sender's signer address. The `handler.HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` then stores the pending callback keyed *only* by this attacker-controlled `MessageID`:

```go
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
``` [1](#0-0) 

This write is unconditional — there is no existence check before overwriting an existing map entry, unlike the JSON-RPC vault path (`GatewayVaultRequestProcessor`) which explicitly rejects duplicate/replay IDs. When a DON node later responds, matching happens purely by `MessageID`:

```go
savedCb, found := h.savedCallbacks[msg.Body.MessageID]
delete(h.savedCallbacks, msg.Body.MessageID)
...
return savedCb.SendResponse(...)
``` [2](#0-1) 

I was not able to fully verify, within the remaining tool budget, whether the gateway's outer request-routing layer (`core/services/gateway/gateway.go`, `ProcessRequest`) or the `requestcache`/`common.ValidatedRequestFromMessage` code enforces per-sender scoping of `MessageID` before dispatch to `HandleLegacyUserMessage` — this is the one open question that would need confirmation in a full session (e.g. via `handler_test.go` or `message_util.go`) before treating this as certain. Based on what was read, no such scoping exists in this handler itself.

### Title
Unscoped, attacker-controlled `MessageID` in legacy gateway trigger handler enables cross-user response hijacking - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The legacy Web API trigger handler (`handler.HandleLegacyUserMessage`) stores each pending user callback in a shared map keyed solely by the client-supplied `MessageID`, with no uniqueness check and no binding to the caller's signer/sender address. An unprivileged client can submit a legacy trigger request using the same `MessageID` as another in-flight request, silently overwriting the original caller's saved callback. When the DON node responds, the response is delivered to whichever callback currently occupies that map slot — potentially the attacker's — while the legitimate caller's request is dropped.

### Finding Description
`Message.Validate()` in `core/services/gateway/api/message.go` only checks the length and null-byte suffix of `Body.MessageID`; it never ties the ID to `Body.Sender` (the ECDSA-recovered signer) [3](#0-2) . `HandleLegacyUserMessage` then unconditionally assigns into `h.savedCallbacks[msg.Body.MessageID]` without checking for a pre-existing, unresolved entry for that ID [4](#0-3) . This is directly analogous to the reported bug class: the `HibernationDen.fulfillRandomWords` issue is fundamentally about a critical routing/callback operation ("`_setFermentedJars`"/"cross-chain send") being gated only by attacker-influenceable state (contract balance) rather than a proper authorization/ownership check; here, the routing of a sensitive callback response is gated only by an attacker-influenceable, unauthenticated field (`MessageID`) rather than being scoped to the authenticated sender.

`handleWebAPITriggerMessage` retrieves and deletes the callback purely by `MessageID` and forwards the DON's response to it [5](#0-4) . Since the map is a single shared namespace across all users (`map[string]*savedCallback` on the handler, not per-sender) [6](#0-5) , a collision — deliberately crafted by any unprivileged, unauthenticated caller (legacy user messages are not gated by any sender authentication beyond signature-derived `Sender`, and the DON ID/method are freely chosen) — is sufficient to hijack another user's pending response.

### Impact Explanation
If exploited, an attacker can receive the workflow-trigger response intended for a different, unrelated user (cross-user response confusion), including whatever payload the DON node echoes back for that trigger. It also causes the legitimate caller's request to be lost entirely (their `savedCallback` reference is overwritten, so the ticket that should be woken by the true response never fires and eventually only times out), a denial-of-service on a per-request basis. Depending on what data legacy trigger payloads carry back through this path, this could expose response data not meant for the attacker.

### Likelihood Explanation
Likelihood is low-to-moderate: the attacker must guess or otherwise learn a currently in-flight `MessageID` belonging to a victim within the response window (bounded by `CallbackMaxAgeSec`, default 120s) [7](#0-6) . If `MessageID`s are generated predictably (e.g., sequential counters, timestamps, or workflow execution IDs known to other parties) by client SDKs, this is easily exploitable; if IDs are high-entropy random UUIDs, exploitation requires either race-prediction or leakage of another user's ID from elsewhere.

### Recommendation
Scope `savedCallbacks` keys by both `Sender` and `MessageID` (e.g. `sender + "/" + messageID`), or reject a new legacy request outright if an unresolved callback already exists for that raw `MessageID`, mirroring the duplicate-request rejection already implemented for JSON-RPC vault requests. Additionally, bind the callback lookup as the response is processed to the expected sender established at `HandleLegacyUserMessage`, not just to the message ID.

### Proof of Concept
1. Victim submits a legacy Web API trigger message with `Body.MessageID = "X"`, signed with their own key; the gateway stores `savedCallbacks["X"] = victimCallback` and forwards the request to the DON.
2. Before the DON's response arrives, attacker submits their own legacy message using the same `Body.MessageID = "X"` (validly signed with the attacker's own key — `MessageID` is not bound to signer), causing `savedCallbacks["X"] = attackerCallback`, overwriting the victim's entry.
3. When the DON responds with `Body.MessageID = "X"`, `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds the attacker's callback, deletes the entry, and sends the DON's response to the attacker instead of the victim.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-43)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L48-61)
```go
type handler struct {
	services.StateMachine
	config          HandlerConfig
	don             handlers.DON
	donConfig       *config.DONConfig
	savedCallbacks  map[string]*savedCallback
	mu              sync.Mutex
	lggr            logger.Logger
	httpClient      network.HTTPClient
	nodeRateLimiter *ratelimit.RateLimiter
	wg              sync.WaitGroup
	stopCh          services.StopChan
	metrics         *metrics
}
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
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
