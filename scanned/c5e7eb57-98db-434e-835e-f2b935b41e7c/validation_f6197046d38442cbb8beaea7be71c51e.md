### Title
Unbounded `topics` array in Web API Trigger requests causes O(N×M) resource-exhaustion DoS during allowlist matching - (File: `core/capabilities/webapi/trigger/trigger.go`)

### Summary
The `web-api-trigger` capability's node-side connector handler processes every message received from the Gateway synchronously and iterates a nested, unbounded double loop over all registered triggers and all attacker-supplied `topics` strings before any size limit on the `topics` array is enforced. An unauthenticated/unprivileged external sender (anyone able to produce a plain ECDSA signature — not a privileged node or gateway operator) can submit a single request with a very large `topics` array to blow up this loop's cost, matching the "unbounded for loop with array input can consume resources" bug class from the referenced report.

### Finding Description
`triggerConnectorHandler.HandleGatewayMessage` receives a message forwarded by the Gateway, decodes `payload.Topics` from the request body, and calls `processTrigger`: [1](#0-0) 

`processTrigger` only checks that `topics` is non-empty — there is no upper bound on its length — and then iterates over every registered workflow trigger, and for each trigger over every topic in the (attacker-controlled) array, performing map lookups and rate-limiter calls under a shared allowlist check: [2](#0-1) 

The only constraint on the size of this input is the overall message byte-size limit (`MaxMessageLenBytes`/`MaxRequestBytes`, e.g. 500000/100000 bytes by default): [3](#0-2) 

Because `topics` entries can be very short strings, an attacker can pack tens of thousands of topic entries into a single request while staying under the byte limit, at essentially no cost of their own. The Gateway's message validation (`Message.Validate`) only bounds `MessageID`, `Method`, `DonID`, and `Receiver` lengths — it performs no validation on the JSON payload contents such as the `topics` array: [4](#0-3) 

Critically, the node's gateway connector `readLoop` dispatches each inbound message to its handler synchronously, in-line, before reading the next message from that gateway connection: [5](#0-4) 

This means a single malicious/oversized `web-api-trigger` request blocks the connector's read loop (and the mutex-protected `registeredWorkflows` map access) for the duration of the O(len(triggers) × len(topics)) loop, delaying processing of all other legitimate gateway traffic destined for that node.

### Impact Explanation
This is a denial-of-service vector reachable by any external, unauthenticated sender able to reach the Gateway's HTTP endpoint and produce a valid signature over an arbitrary payload (the "sender" here is just a self-chosen keypair, not a privileged/allowlisted identity — allowlisting only happens inside the vulnerable loop itself). A crafted request with a very large `topics` array can consume disproportionate CPU/lock time on the node-side connector handler relative to the request's cost, delaying or starving delivery of legitimate trigger/target/compute messages over the same gateway connection. Severity is Medium: it's a resource-exhaustion/availability issue rather than fund loss or authentication bypass, but it directly maps to the reported bug class (unbounded loop over user-supplied array).

### Likelihood Explanation
Likelihood is Medium-High: no special privileges, valid node registration, or workflow ownership are required — only a syntactically valid signed Gateway message with an oversized `topics` array, which any external caller of the Gateway's public/legacy interface can construct.

### Recommendation
Enforce a maximum length on `payload.Topics` (and correspondingly on `TriggerConfig.AllowedTopics`) before entering the nested loop in `processTrigger`, e.g.:
```go
if len(topics) == 0 || len(topics) > maxTopicsPerRequest {
    return errors.New("invalid number of topics")
}
```
Additionally, consider capping array-typed fields generically at message validation time (`Message.Validate` / `ValidatedMessageFromReq`) and moving expensive per-message handler work off the connector's synchronous `readLoop` so a single slow/expensive message cannot delay delivery of subsequent Gateway messages.

### Proof of Concept
1. An external caller with any ECDSA key crafts a `web-api-trigger` message whose `TriggerRequestPayload.Topics` contains tens of thousands of short strings (e.g. `"a0"`..`"a49999"`), staying under `MaxMessageLenBytes`/`MaxRequestBytes`.
2. The caller signs the message (`msg.Sign(privateKey)`) — no allowlisting or privileged role is needed to produce a syntactically valid message, since `AuthenticateExternalInitiator`/session auth is not involved in this Gateway path.
3. The message passes `Message.Validate()` (only ID/Method/DonID/Receiver length checks) and is forwarded to the node via `HandleLegacyUserMessage` → `don.SendToNode`.
4. On the node side, `connector.readLoop` synchronously invokes `triggerConnectorHandler.HandleGatewayMessage` → `processTrigger`, which iterates `len(registeredWorkflows) × len(topics)` times while holding/using the allowlist maps and rate limiter, blocking further message processing on that connection for the duration.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L91-119)
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
			if trigger.allowedTopics[topic] {
				matchedWorkflows++
				if !trigger.allowedSenders[sender.String()] {
					err = fmt.Errorf("unauthorized Sender %s, messageID %s", sender.String(), body.MessageID)
					h.lggr.Debugw(err.Error())
					continue
				}
				if !trigger.rateLimiter.Allow(body.Sender) {
					err = fmt.Errorf("request rate-limited for sender %s, messageID %s", sender.String(), body.MessageID)
					continue
				}
				fullyMatchedWorkflows++
```

**File:** core/capabilities/webapi/trigger/trigger.go (L167-184)
```go
func (h *triggerConnectorHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) error {
	msg, err := hc.ValidatedMessageFromReq(req)
	if err != nil {
		h.lggr.Errorw("error validating message from request", "err", err, "request", req)
		return nil
	}
	body := &msg.Body
	sender := ethCommon.HexToAddress(body.Sender)
	var payload webapicap.TriggerRequestPayload
	err = json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw("error decoding payload", "err", err)
		err = h.sendResponse(ctx, gatewayID, body, ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: fmt.Errorf("error %s decoding payload", err.Error()).Error()})
		if err != nil {
			h.lggr.Errorw("error sending response", "err", err)
		}
		return nil
	}
```

**File:** docs/CONFIG.md (L1941-1946)
```markdown
### MaxMessageLenBytes
```toml
MaxMessageLenBytes = 500000 # Default
```
MaxMessageLenBytes is the max size of a message in bytes.

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
