### Title
Unbounded `Topics` array in Web API trigger requests causes O(triggers × topics) nested-loop DoS - ([File: core/capabilities/webapi/trigger/trigger.go])

### Summary
`triggerConnectorHandler.processTrigger`, which is invoked directly from `HandleGatewayMessage` for every incoming `web_api_trigger` gateway message, iterates over **all registered triggers** nested inside a loop over the **attacker-supplied** `payload.Topics` slice, with no upper bound on the number of topics a caller may submit.

### Finding Description
`HandleGatewayMessage` unmarshals the request payload from an unprivileged, internet-facing gateway request into `webapicap.TriggerRequestPayload` and calls `processTrigger` unconditionally for `MethodWebAPITrigger` requests [1](#0-0) .

Inside `processTrigger`, the only validation performed on `payload.Topics` is that it must be non-empty — there is no maximum length check: [2](#0-1) 

The function then snapshots every currently registered trigger (one per registered workflow on the node) and runs a nested loop: for each registered trigger, it iterates over every topic in the caller-controlled `topics` slice, doing map lookups (`trigger.allowedTopics[topic]`, `trigger.allowedSenders[...]`) and rate-limiter checks per iteration: [3](#0-2) 

The cost of a single incoming message is therefore `O(len(registeredWorkflows) × len(payload.Topics))`. The number of registered triggers grows as more workflows with the `web-api-trigger@1.0.0` capability are deployed on the node/DON, and `payload.Topics` is fully attacker-controlled JSON input — an unprivileged sender can pad it with many short string elements within the HTTP body size limit enforced at the gateway's HTTP server layer [4](#0-3) , but that limit only bounds total bytes, not the number of array elements, so a modest byte budget can still encode tens of thousands of short topic strings.

This is a direct structural analog of the reported Solidity bug: an unbounded loop over externally-influenced/growing data processed on every request, reachable by an unprivileged actor, with no batching or per-request cap.

### Impact Explanation
A single crafted `web_api_trigger` gateway message with a very large `Topics` array forces the node to perform `registeredWorkflows × topics` map lookups and comparisons synchronously inside `HandleGatewayMessage`, which is invoked from the gateway connector's single-goroutine-per-connection `readLoop` [5](#0-4) . Because this processing is synchronous and blocking within the connector's read loop, a computationally expensive request can add significant latency to the processing of a single connection, delaying delivery of subsequent legitimate trigger messages and gateway responses for all workflows on that connection. Repeated or scripted requests exploiting this pattern amplify CPU consumption proportional to the number of deployed workflows, which grows over time — mirroring the original report's warning that the loop's cost increases as the tracked state (external rewards / here, registered triggers) grows, and can degrade or deny service for all workflow triggers relying on that node's gateway connector.

### Likelihood Explanation
The `Topics` field is fully attacker-controlled and reachable without any privileged role — any sender able to submit a `web_api_trigger` JSON-RPC message to the gateway (an intentionally externally-facing entry point) can trigger this path. No authentication beyond the basic gateway signature/sender check is required to reach `processTrigger`, and there's no rejection of oversized `Topics` arrays before the nested loop executes, making exploitation straightforward for any external caller of the trigger capability's gateway endpoint.

### Recommendation
Enforce a hard upper bound on `len(payload.Topics)` in `processTrigger` (or earlier, during JSON-RPC decoding/validation) and reject requests exceeding it before entering the nested loop. Consider also restructuring the matching logic to avoid the full `registeredWorkflows × topics` cross-product — e.g., by indexing triggers by topic in a reverse lookup map so cost scales with matches rather than the full trigger/topic Cartesian product.

### Proof of Concept
1. Deploy several workflows registering `web-api-trigger@1.0.0` triggers, populating `registeredWorkflows` on a node.
2. Send a `web_api_trigger` JSON-RPC gateway message whose `Topics` field contains tens of thousands of short strings, staying under the gateway HTTP body size limit.
3. Observe that `processTrigger` performs `registeredWorkflows × topics` iterations synchronously in the connector's read loop, measurably delaying processing of concurrent/subsequent gateway messages on that connection; repeating the request from multiple senders compounds CPU load node-wide.

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L91-96)
```go
	topics := payload.Topics

	// empty topics is error for V1
	if len(topics) == 0 {
		return errors.New("empty Workflow Topics")
	}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L98-118)
```go
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
```

**File:** core/capabilities/webapi/trigger/trigger.go (L167-200)
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

	switch body.Method {
	case ghcapabilities.MethodWebAPITrigger:
		resp := h.processTrigger(ctx, gatewayID, body, sender, payload)
		var response ghcapabilities.TriggerResponsePayload
		if resp == nil {
			response = ghcapabilities.TriggerResponsePayload{Status: "ACCEPTED"}
		} else {
			response = ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: resp.Error()}
			h.lggr.Errorw("Error processing trigger", "gatewayID", gatewayID, "body", body, "response", resp)
		}
		err = h.sendResponse(ctx, gatewayID, body, response)
		if err != nil {
			h.lggr.Errorw("Error sending response", "body", body, "response", response, "err", err)
		}
		return nil
```

**File:** core/services/gateway/network/httpserver.go (L1-1)
```go
package network
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
