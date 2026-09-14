The report describes a stateless-router race condition: an operation is split into two non-atomic steps sharing a single mutable slot, and a second, independent caller can control the same key during the gap between the steps to hijack or corrupt the first caller's result. The closest reachable analog in Chainlink is in the gateway's legacy Web API trigger handler.

### Title
Cross-user response confusion via attacker-controlled `MessageID` collision in gateway `savedCallbacks` map - (`core/services/gateway/handlers/capabilities/handler.go`)

### Summary
`handler.HandleLegacyUserMessage` stores a user's callback in a shared map keyed solely by the client-supplied `msg.Body.MessageID`, then later `handleWebAPITriggerMessage` looks the callback up by that same ID when a DON node responds. Because `MessageID` is fully attacker-controlled and the map is shared across all users of the DON, one unprivileged caller can overwrite another caller's pending callback entry during the window between request submission and node response, causing responses to be delivered to the wrong caller (or lost entirely) — the same "non-atomic two-step operation, second actor interferes" bug class as the audited `UlyssesRouter.addLiquidity` finding.

### Finding Description
`HandleLegacyUserMessage` unconditionally stores the caller's callback keyed by `msg.Body.MessageID` with no existing-entry check and no per-sender scoping: [1](#0-0) 

`MessageID` is taken directly from the incoming legacy JSON-RPC/HTTP payload and is entirely caller-chosen, as shown by the CLI tool that constructs such messages: [2](#0-1) 

Later, when a DON node sends back a `MethodWebAPITrigger` response, the handler looks the callback up purely by `MessageID`, deletes it, and forwards the response to whichever callback is currently registered for that ID: [3](#0-2) 

This mirrors the audited flaw exactly: the map entry keyed by `MessageID` acts like the router's "assumed prior deposit" — it is set in one request/response round trip that isn't atomic. Between the time User A's `HandleLegacyUserMessage` call registers `savedCallbacks["X"]` and the time the DON responds for User A's request, an unprivileged User B can submit their own legacy request reusing the same `MessageID` "X" (nothing prevents ID reuse or requires it to be scoped to the sender), overwriting `savedCallbacks["X"]` with User B's callback. When the node's response for User A's original request arrives (still tagged `MessageID: "X"`), `handleWebAPITriggerMessage` will deliver User A's trigger response to User B's callback instead, and User A's callback is discarded, resulting in cross-user response confusion (User B receives data/results intended for User A) and denial of response for User A.

### Impact Explanation
This is a request/response confusion vulnerability reachable by any unprivileged, unauthenticated internet-facing client hitting the gateway's legacy Web API trigger endpoint. An attacker can deliberately guess or reuse a victim's `MessageID` (or brute force collisions if IDs are short/predictable, as in the default `"12345"` shown in the CLI helper) to receive workflow trigger responses meant for another caller, or to deny a victim's response by evicting their callback. Depending on what data flows through `MethodWebAPITrigger` responses, this can leak workflow execution results to an unauthorized third party.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to know or predict the victim's chosen `MessageID` and to time their request within the response window of the victim's request (bounded by `defaultCallbackMaxAgeSec` = 120s and node round-trip latency), which is a realistic race window for an automated attacker continuously submitting requests with a small set of guessed IDs against a busy gateway/DON pair.

### Recommendation
Scope `savedCallbacks` keys by both sender identity and `MessageID` (e.g., `sender + ":" + MessageID`) rather than by `MessageID` alone, and/or reject registration if an active (non-expired) callback already exists for the derived key, returning an explicit "duplicate/in-flight request ID" error to the caller instead of silently overwriting the existing entry.

### Proof of Concept
1. User A sends a legacy `web_api_trigger` HTTP request to the gateway with `MessageID = "X"`; `HandleLegacyUserMessage` stores `savedCallbacks["X"] = callbackA` and forwards the request to all DON members.
2. Before the DON responds, User B sends their own legacy request also using `MessageID = "X"`; `HandleLegacyUserMessage` overwrites `savedCallbacks["X"] = callbackB`.
3. A DON node responds to User A's original request (tagged `MessageID: "X"`); `handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds `callbackB`, deletes the entry, and delivers User A's response payload to User B via `callbackB.SendResponse`.
4. User A's HTTP connection never receives a response (or times out), while User B has received data associated with User A's triggered workflow execution.

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
