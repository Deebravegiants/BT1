Audit Report

## Title
Unbounded `topics` array in Web API Trigger requests causes O(N×M) resource-exhaustion DoS during allowlist matching - (File: `core/capabilities/webapi/trigger/trigger.go`)

## Summary
`triggerConnectorHandler.processTrigger` iterates a nested loop over every registered trigger and every entry in the attacker-supplied `payload.Topics` array, with no upper bound on the array's length beyond the overall message byte-size limit. Because the handler is invoked synchronously and in-line from `gatewayConnector.readLoop`, a single oversized request can consume disproportionate CPU/lock time and delay processing of subsequent legitimate Gateway messages on that connection.

## Finding Description
`HandleGatewayMessage` decodes `body.Payload` into `webapicap.TriggerRequestPayload` and calls `processTrigger` with the parsed `topics` slice: [1](#0-0) . `processTrigger` only validates that `topics` is non-empty, then does `for _, trigger := range triggers { for _, topic := range topics { ... } }`, performing map lookups and rate-limiter calls for every (trigger, topic) pair: [2](#0-1) . There is no cap on `len(topics)` anywhere in this path or in `Message.Validate` (`core/services/gateway/api/message.go`), which only checks `MessageID`, `Method`, `DonID`, and `Receiver` lengths and does not inspect the JSON payload contents. The only real constraint is the overall message byte-size limit (`MaxMessageLenBytes`/`MaxRequestBytes`), which does not meaningfully limit the number of short topic strings that fit in a single message. On the node side, `gatewayConnector.readLoop` calls `handler.HandleGatewayMessage` synchronously before reading the next message off the channel: [3](#0-2) , so a single expensive `processTrigger` call blocks subsequent Gateway message processing on that connection.

## Impact Explanation
This is a resource-exhaustion/availability issue (in-scope DoS category): a crafted request with an oversized `topics` array increases CPU and lock-hold time in `processTrigger` disproportionately to the attacker's own cost, and because the connector's `readLoop` processes messages synchronously and in-line, this can delay delivery of other legitimate trigger/target/compute messages arriving on the same gateway connection while the loop executes and while `h.mu`/`chWriteMu` are held. This does not cause fund loss or authentication bypass, so it is appropriately a Medium-severity availability finding rather than a critical one, and it maps to the unbounded-loop/array resource-exhaustion class referenced in the report.

## Likelihood Explanation
Likelihood is Medium-High. Reaching `processTrigger` requires only a message that passes `Message.Validate()` (a well-formed signature over the message body and length-bounded metadata fields) and is routed through `HandleLegacyUserMessage` in the Gateway's capabilities handler, which forwards the request to every DON member without any allowlist check prior to `don.SendToNode`: [4](#0-3) . No workflow registration, node privilege, or gateway-operator role is required to produce a syntactically valid, signed message with a large `Topics` array, and the cost of generating tens of thousands of short strings is negligible for the attacker.

## Recommendation
Enforce a maximum length on `payload.Topics` (and on `TriggerConfig.AllowedTopics`) before entering the nested loop in `processTrigger`, e.g., reject requests where `len(topics) > maxTopicsPerRequest`. Additionally, consider bounding array-typed JSON fields generically at message validation time (`Message.Validate` / `ValidatedMessageFromReq`), and avoid doing expensive per-message work synchronously inside `gatewayConnector.readLoop` so that one expensive message cannot delay delivery of subsequent Gateway messages.

## Proof of Concept
1. Craft a `web_api_trigger` message body with `TriggerRequestPayload.Topics` containing tens of thousands of short strings (e.g., `"a0"`..`"a49999"`), keeping the total message size under `MaxMessageLenBytes`/`MaxRequestBytes`.
2. Sign the message with any ECDSA keypair (`msg.Sign(privateKey)`) — no allowlisting or DON membership is checked before `Message.Validate()` and forwarding via `HandleLegacyUserMessage`.
3. Submit the message to the Gateway's legacy HTTP endpoint; `Message.Validate()` passes since it only checks `MessageID`/`Method`/`DonID`/`Receiver` lengths, not payload contents, and the message is forwarded to every DON node via `don.SendToNode`.
4. On the node, `gatewayConnector.readLoop` synchronously calls `triggerConnectorHandler.HandleGatewayMessage` → `processTrigger`, iterating `len(registeredWorkflows) × len(topics)` times, which can be measured (e.g., via a Go benchmark/unit test instantiating `triggerConnectorHandler` with several registered triggers and calling `processTrigger` with a large `topics` slice) to show CPU time growing linearly with the attacker-controlled array size while blocking the read loop.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
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
	req, err := common.ValidatedRequestFromMessage(msg)
	if err != nil {
		h.lggr.Errorw(ErrTransformingMessageToRequest)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrTransformingMessageToRequest,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```
