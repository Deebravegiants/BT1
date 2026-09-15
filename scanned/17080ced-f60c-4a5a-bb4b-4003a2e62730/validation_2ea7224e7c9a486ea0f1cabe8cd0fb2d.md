### Title
Cross-caller response hijacking via unkeyed `MessageID` collision in gateway WebAPI trigger handler - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The gateway's legacy WebAPI trigger handler stores pending callbacks in a map keyed **only** by the client-supplied `MessageID`, with no binding to the caller/sender. Any unprivileged external caller can submit a `web_api_trigger` message with a `MessageID` that collides with another in-flight request, silently overwriting the other caller's saved callback. When the DON later responds (matched purely by `MessageID`), the response is delivered to whichever callback currently occupies that map slot — potentially the attacker's — resulting in cross-caller response confusion/hijacking. This mirrors the reported bug class: a client-controlled identifier is trusted and persisted without any ownership/ownership-scoping check, and later used to route access/response to a resource across authorization/caller boundaries.

### Finding Description
`HandleLegacyUserMessage` accepts an inbound `api.Message` from an external caller and stores the caller's callback in `h.savedCallbacks`, keyed solely by `msg.Body.MessageID`: [1](#0-0) 

There is no uniqueness check here — unlike the shared `RequestCache` abstraction used by other gateway handlers (e.g., target/action), which explicitly keys pending requests by `{sender, id}` and rejects duplicates: [2](#0-1) 

The trigger handler bypasses this safer cache entirely and uses a bespoke `map[string]*savedCallback` keyed only by the message ID string: [3](#0-2) 

`MessageID` is a value chosen by the external HTTP submitter of the trigger request (see `core/scripts/gateway/web_api_trigger/invoke_trigger.go`, where `messageID` is a plain CLI/user-supplied flag), not a server-generated or per-sender-scoped identifier: [4](#0-3) 

When a node eventually responds, `handleWebAPITriggerMessage` looks up and deletes the callback purely by `MessageID`, again with no sender/receiver correlation check, and forwards the DON's payload to whatever callback is found: [5](#0-4) 

Because the "TODO: apply allowlist and rate-limiting here" comment confirms this legacy path currently performs no caller authentication/authorization at all: [6](#0-5) 

any two unrelated, unprivileged submitters that happen to pick (or are induced to pick) the same `MessageID` will collide in `h.savedCallbacks`. Whichever request registers last "wins" the map slot; the earlier submitter's entry is silently discarded (no error returned), and the eventual node response for either message ID will be routed to whoever currently owns that slot — not necessarily the caller who actually sent the corresponding request payload.

### Impact Explanation
This allows an unprivileged, unauthenticated actor hitting the internet-facing gateway to:
- Cause response misdelivery: an attacker's callback can receive another caller's trigger response payload (potential data/response confusion across callers), or conversely, the victim's callback silently receives nothing (its earlier registration was overwritten) while the attacker's request masquerades as it.
- Disrupt/deny legitimate submitters' responses (their saved callback is dropped without any error signal, unlike `RequestCache.NewRequest`, which explicitly errors on duplicate keys).

This matches the reported bug class's essence: trusting a caller-supplied identifier as an implicit authorization/ownership token for routing a response, without validating that the identifier is scoped to the requesting party.

### Likelihood Explanation
Reachable by any unauthenticated HTTP client able to POST a `web_api_trigger` message to the gateway (no prior session, token, or role required per the current TODO). Exploitation only requires guessing or reusing a `MessageID` value used by another concurrent submitter — since `MessageID` is entirely attacker-chosen and there is no per-sender scoping or collision rejection, this is trivial to trigger deliberately (e.g., always submitting `MessageID="12345"` as in the project's own example script) and can occur accidentally as well under load.

### Recommendation
- Scope `savedCallbacks` (and any lookup on node response) by a composite key that includes the message sender/DON member identity, mirroring the `{sender, id}` keying already used in `common.RequestCache`.
- Reject (rather than silently overwrite) registration of a duplicate key, as `RequestCache.NewRequest` already does.
- Prefer migrating this legacy trigger path onto the shared `RequestCache` implementation instead of the bespoke `savedCallbacks` map.
- Implement the still-outstanding "apply allowlist and rate-limiting" TODO for this handler.

### Proof of Concept
1. Submitter A sends a `web_api_trigger` HTTP message to the gateway with `MessageID = "X"`; the gateway registers A's callback in `savedCallbacks["X"]` and forwards the request to DON nodes.
2. Before the DON responds, Attacker B sends a second `web_api_trigger` message also using `MessageID = "X"`; this call overwrites `savedCallbacks["X"]` with B's callback with no error returned to either party.
3. When a DON node responds to A's original forwarded request (echoing `MessageID = "X"`), `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds B's callback, deletes the entry, and delivers A's trigger-execution response payload to B.
4. B thereby receives a response belonging to A's request, while A's callback never resolves (until any handler-level timeout, if configured at all for this legacy path).

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L72-76)
```go
type savedCallback struct {
	id        string
	createdAt time.Time
	handlers.Callback
}
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

**File:** core/services/gateway/handlers/common/requestcache.go (L50-63)
```go
func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
```

**File:** core/scripts/gateway/web_api_trigger/invoke_trigger.go (L56-105)
```go
	messageID := flag.String("id", "12345", "Request ID")
	methodName := flag.String("method", "web_api_trigger", "Method name")
	donID := flag.String("don_id", "workflow_don_1", "DON ID")

	flag.Parse()

	if privateKey == nil || *privateKey == "" {
		if err := godotenv.Load(); err != nil {
			panic(err)
		}

		privateKeyEnvVar := os.Getenv("PRIVATE_KEY")
		privateKey = &privateKeyEnvVar
		fmt.Println("Loaded private key from .env")
	}

	// validate key and extract address
	key, err := crypto.HexToECDSA(*privateKey)
	if err != nil {
		fmt.Println("error parsing private key", err)
		return
	}

	address := crypto.PubkeyToAddress(key.PublicKey)
	fmt.Printf("Public Address: %s\n", address.Hex())

	payload := map[string]any{
		"trigger_id":       "web-api-trigger@1.0.0",
		"trigger_event_id": "action_1234567890",
		"timestamp":        int(time.Now().Unix()),
		"topics":           []string{"daily_price_update"},
		"params": map[string]string{
			"bid": "101",
			"ask": "102",
		},
	}

	payloadJSON, err := json.Marshal(payload)
	if err != nil {
		fmt.Println("error marshalling JSON payload", err)
		return
	}
	msg := &api.Message{
		Body: api.MessageBody{
			MessageID: *messageID,
			Method:    *methodName,
			DonID:     *donID,
			Payload:   payloadJSON,
		},
	}
```
