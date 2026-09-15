Confirmed: `Message.Validate()` bounds `MessageID`, `Method`, `DonID`, and `Receiver` lengths but never bounds `Payload` size or the number of elements inside it, so `payload.Topics` array length is entirely unconstrained by any validation in the message pipeline. [1](#0-0) 

Audit Report

## Title
Unbounded `Topics` array in web-api trigger requests enables synchronous CPU-exhaustion DoS that blocks all Gateway message processing - ([File: core/capabilities/webapi/trigger/trigger.go])

## Summary
`triggerConnectorHandler.processTrigger` performs a nested loop over every registered workflow trigger and every element of the attacker-controlled `payload.Topics` slice, with the only length check being that it is non-empty. Since `HandleGatewayMessage` runs synchronously inside the node's single-threaded `readLoop` per Gateway connection, an oversized `Topics` array causes `O(registeredWorkflows × len(topics))` work to execute inline, delaying processing of all other queued messages on that connection.

## Finding Description
`processTrigger` reads `topics := payload.Topics` and iterates `triggers × topics` with only a check for `len(topics) == 0`, no upper bound: [2](#0-1) 

The message validation path, `hc.ValidatedMessageFromReq` → `json.Unmarshal` → `m.Validate()`, bounds `MessageID`, `Method`, `DonID`, and `Receiver` string lengths and signature format but never inspects or bounds `Payload` (raw JSON) size or the decoded `Topics` array length: [1](#0-0) [3](#0-2) 

The generated schema for `TriggerRequestPayload` also imposes no `maxItems`/length constraint on `topics`: [4](#0-3) 

The only size control anywhere in the ingestion path is the overall HTTP request byte cap (`MaxRequestBytesLimiter`) enforced in the Gateway's HTTP server, which limits total request bytes but not element counts — a payload well under the byte cap can still contain a very large number of short topic strings. [5](#0-4) 

Critically, `HandleGatewayMessage` is invoked synchronously, once per message, in `gatewayConnector.readLoop`, which is a single loop goroutine per gateway connection dispatching messages serially: [6](#0-5) [7](#0-6) 

This confirms the exact mechanism described in the claim: no bound on `len(topics)`, no bound enforced upstream, and synchronous single-threaded dispatch per connection.

## Impact Explanation
A caller able to reach the Gateway's `web_api_trigger` method (any client that can sign a valid message and is an `allowedSender` for at least one registered trigger — required for the message to pass the trigger's sender check, though the CPU cost of iterating `topics` inside the inner loop's `trigger.allowedTopics[topic]` map lookups is paid regardless of sender authorization, since it happens before the sender check on each matching topic) can inflate `len(topics)` to impose extra CPU work per registered trigger on that node's connector read loop. This delays delivery of subsequent Gateway messages for that connection, a cross-workflow/cross-tenant availability degradation. This maps to a legitimate availability/DoS impact category, but the severity is bounded: the work is CPU-bound map lookups (`O(len(topics))` per registered trigger, not `O(len(topics)²)` or unbounded blocking), the topics are matched against `trigger.allowedTopics` maps (only workflows registering that trigger type participate), and per-connection readLoop blocking only affects gateway↔node traffic for that one Gateway/DON connection — not the whole node process or all Gateways.

## Likelihood Explanation
Constructing a large `Topics` array requires only a validly signed message and matches the sender allowlist of at least one registered trigger to bypass early-return `no Matching Workflow Topics`. Note that even without matching any `allowedTopics`, `matchedWorkflows` stays 0 for non-matching topics — the loop still iterates `triggers × topics` regardless of match, so a completely unprivileged, unregistered sender can still cause the full iteration cost via a large array of arbitrary (non-matching) strings before returning `"no Matching Workflow Topics"`. This makes the DoS trivially reachable by any unprivileged, unregistered client, requiring only a validly formatted and signed Gateway message.

## Recommendation
Enforce a strict maximum on `len(payload.Topics)` (e.g., via schema `maxItems` and/or a runtime check in `processTrigger`) before entering the nested loop, and consider bounding total iteration cost (`triggers × topics`) explicitly. Additionally, consider dispatching per-message handling in `readLoop` to a bounded worker pool so a single expensive message cannot delay unrelated Gateway traffic on the same connection.

## Proof of Concept
1. Register at least one `web-api-trigger` workflow (any config).
2. As any client with a valid signing key (no allowlist match required), construct a `web_api_trigger` JSON-RPC message with `payload.Topics` set to tens of thousands of short strings, keeping total body size under `MaxRequestBytesLimiter`.
3. Send via the Gateway HTTP/WS endpoint; observe `triggerConnectorHandler.processTrigger` iterate `len(registeredWorkflows) × len(topics)` map lookups synchronously inside `gatewayConnector.readLoop`, as demonstrated by the existing test harness pattern in `core/capabilities/webapi/trigger/trigger_test.go`'s `gatewayRequest`/`HandleGatewayMessage` calls, extended to a large `topics` slice to measure wall-clock blocking of the read loop. [8](#0-7)

### Citations

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

**File:** core/capabilities/webapi/trigger/trigger.go (L91-107)
```go
	topics := payload.Topics

	// empty topics is error for V1
	if len(topics) == 0 {
		return errors.New("empty Workflow Topics")
	}

	h.mu.Lock()
	triggers := slices.Collect(maps.Values(h.registeredWorkflows))
	h.mu.Unlock()

	// workflows that have matched topics
	matchedWorkflows := 0
	// workflows that have matched topic and passed all checks
	fullyMatchedWorkflows := 0
	for _, trigger := range triggers {
		for _, topic := range topics {
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

**File:** core/capabilities/webapi/webapicap/event_trigger-schema.json (L69-75)
```json
                "topics": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description" : "An array of a single topic (string) to be started by this event."
                    }
                },
```

**File:** core/services/gateway/network/httpserver.go (L211-224)
```go
	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		msg := "Failed to get request size limit"
		s.lggr.Errorw(msg, "err", err)
		http.Error(w, msg, http.StatusInternalServerError)
		return
	}
	source := http.MaxBytesReader(nil, r.Body, int64(maxRequestBytes))
	rawMessage, err := io.ReadAll(source)
	if err != nil {
		s.lggr.Error("error reading request", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
```

**File:** core/services/gateway/connector/connector.go (L268-298)
```go
func (c *gatewayConnector) readLoop(gatewayState *gatewayState) {
	defer c.closeWait.Done()
	ctx, cancel := c.shutdownCh.NewCtx()
	defer cancel()

	for {
		select {
		case <-c.shutdownCh:
			return
		case item := <-gatewayState.conn.ReadChannel():
			var req jsonrpc.Request[json.RawMessage]
			err := json.Unmarshal(item.Data, &req)
			if err != nil {
				c.lggr.Errorw("parse error when reading from Gateway", "id", gatewayState.config.ID, "err", err)
				break
			}
			c.handlersMu.RLock()
			handler, exists := c.handlers[req.Method]
			c.handlersMu.RUnlock()
			if !exists {
				c.lggr.Errorw("no handler for method", "id", gatewayState.config.ID, "method", req.Method)
				break
			}
			// do not break on error. HandleGatewayMessage handles errors
			// by sending a response back to the Gateway.
			err = handler.HandleGatewayMessage(ctx, gatewayState.config.ID, &req)
			if err != nil {
				c.lggr.Warnw("failed to handle message from Gateway", "id", gatewayState.config.ID, "method", req.Method, "err", err)
			}
		}
	}
```

**File:** core/services/gateway/connector/connector.go (L335-348)
```go
func (c *gatewayConnector) Start(ctx context.Context) error {
	return c.StartOnce("GatewayConnector", func() error {
		c.lggr.Info("starting gateway connector")
		c.recordGatewaysPerDon(ctx)
		for _, gatewayState := range c.gateways {
			if err := gatewayState.conn.Start(ctx); err != nil {
				return err
			}
			c.closeWait.Add(2)
			go c.readLoop(gatewayState)
			go c.reconnectLoop(gatewayState)
		}
		return nil
	})
```

**File:** core/capabilities/webapi/trigger/trigger_test.go (L84-120)
```go
func gatewayRequest(t *testing.T, privateKey string, topics []string, methodName string) *jsonrpc.Request[json.RawMessage] {
	messageID := "12345"
	if methodName == "" {
		methodName = ghcapabilities.MethodWebAPITrigger
	}
	donID := "workflow_don_1"

	key, err := crypto.HexToECDSA(privateKey)
	require.NoError(t, err)

	payload := webapicap.TriggerRequestPayload{
		TriggerId:      TriggerType,
		TriggerEventId: "action_1234567890",
		Timestamp:      1234567890,
		Topics:         topics,
		Params: webapicap.TriggerRequestPayloadParams{
			"bid": "100",
			"ask": "101",
		},
	}

	payloadJSON, err := json.Marshal(payload)
	require.NoError(t, err)
	msg := &api.Message{
		Body: api.MessageBody{
			MessageID: messageID,
			Method:    methodName,
			DonID:     donID,
			Payload:   json.RawMessage(payloadJSON),
		},
	}
	err = msg.Sign(key)
	require.NoError(t, err)
	req, err := hc.ValidatedRequestFromMessage(msg)
	require.NoError(t, err)
	return req
}
```
