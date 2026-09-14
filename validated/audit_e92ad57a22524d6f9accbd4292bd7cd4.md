Based on my investigation, I found `MessageID`/request ID is fully client-controlled in the legacy WebAPI trigger gateway handler, and it is used as the key into a shared `savedCallbacks` map that any of the DON's nodes can complete. This is the closest analog to the reported bug class (a permissionless action keyed on attacker-controllable data that another user relies on completing correctly), but it is a genuine finding only if two different unprivileged users can collide on the same ID and thereby steal/consume each other's callback — which the code does allow, since there is no per-caller binding on the ID before it's stored.

### Title
Attacker-controlled `MessageID` collision in gateway `WebAPIHandler` allows cross-user response hijacking / loss of trigger callback - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy WebAPI trigger flow (`handler.HandleLegacyUserMessage`) stores a caller's response callback in a shared, gateway-wide map keyed solely by the client-supplied `msg.Body.MessageID` [1](#0-0) . Any unprivileged client can choose an arbitrary `MessageID` string when submitting a request (there is no server-side uniqueness enforcement, ownership binding, or per-sender namespacing of the ID) [2](#0-1) . When any DON node later reports back a `web_api_trigger` result for that `MessageID`, the gateway looks the ID up in the map, deletes it, and forwards the response to whichever caller's `Callback` is currently stored there [3](#0-2) .

### Finding Description
This mirrors the root cause of the Tapioca H-03 report: an action that is supposed to be completed for a specific requester is instead gated only on a value (`_tokenId`/`MessageID`) that is public/guessable and not bound to `msg.sender`/caller identity, so a second unprivileged actor can race the intended flow and consume the slot meant for someone else. Here, if Attacker A submits a legacy WebAPI trigger request using the exact same `MessageID` that a legitimate user B is about to use (or has already used but the entry has not yet been pruned/consumed), A's callback overwrites B's entry in `h.savedCallbacks` [1](#0-0) . When the DON node's response for that `MessageID` arrives, `handleWebAPITriggerMessage` delivers it to whichever callback is currently stored under that key — which may now be Attacker A's callback instead of B's — because the lookup/delete only checks the raw ID, with no binding to the original caller's identity or session [4](#0-3) . Conversely, B's genuine trigger response is lost since the map entry it needed was overwritten and already deleted by A's earlier completion, leaving B's HTTP request to the gateway to hang until callback timeout with no data ever delivered — an unprivileged-client-triggerable denial/response-confusion, analogous to the Tapioca reward token becoming permanently unreachable when a third party front-runs the claim of a slot the victim expected to consume itself.

### Impact Explanation
An unauthenticated caller of the gateway's legacy `web_api_trigger` interface can (a) cause another user's trigger response to be silently dropped (denial of service on legitimate requests) and (b) in principle receive a response object addressed to a different caller's request if the collision timing allows the attacker's slot to still be present when the legitimate node response for that ID arrives — a cross-user response confusion. Because this endpoint sits directly in the internet-facing gateway path and requires no privileged access to exploit, and legacy `MessageID`s are entirely attacker-chosen, this is a concretely reachable client-side authentication/business-logic gap in the gateway trust boundary.

### Likelihood Explanation
Likelihood is moderate: the attacker must guess or observe a `MessageID` that a legitimate concurrent caller is using. Because the invocation examples/scripts in the repo show trivially predictable, human-chosen IDs (e.g., a hardcoded `"12345"` default) [5](#0-4) , and there is no requirement to authenticate or prove the ID is unique/owned by the caller before storing a callback, collisions are plausible in any multi-tenant deployment reusing default or non-random client-side ID generation, and can be forced deliberately by a malicious client racing against a known/target request ID.

### Recommendation
Bind each `savedCallbacks` entry to the identity of the request's sender (e.g., derive the map key from a combination of the authenticated/signed sender and the client-supplied `MessageID`, similar to how `HandleNodeMessage` already verifies `msg.Body.Sender != nodeAddr` before dispatch [6](#0-5) ), reject/overwrite-protect duplicate `MessageID`s from different senders, and consider generating the storage key server-side rather than trusting the client-supplied value verbatim.

### Proof of Concept
1. User B signs and sends a `web_api_trigger` legacy message to the gateway with `MessageID = "shared-id"`; the gateway stores B's callback at `savedCallbacks["shared-id"]` and forwards the request to DON nodes [7](#0-6) .
2. Before a DON node responds, Attacker A sends a second legacy `web_api_trigger` message also using `MessageID = "shared-id"`; the gateway overwrites the map entry with A's callback [1](#0-0) .
3. When a DON node eventually reports the trigger result tagged with `MessageID = "shared-id"` (which could correspond to either A's or B's original request depending on node processing order), `handleWebAPITriggerMessage` pops the current map entry — now A's callback — and delivers the response to A [4](#0-3) .
4. B's original HTTP call to the gateway never receives a response and stalls until the callback times out, while A may receive an unrelated node response, none of which was verified server-side as belonging to A.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-419)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
```

**File:** core/scripts/gateway/web_api_trigger/invoke_trigger.go (L53-105)
```go
func main() {
	gatewayURL := flag.String("gateway_url", "http://localhost:5002", "Gateway URL")
	privateKey := flag.String("private_key", "65456ffb8af4a2b93959256a8e04f6f2fe0943579fb3c9c3350593aabb89023f", "Private key to sign the message with")
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
