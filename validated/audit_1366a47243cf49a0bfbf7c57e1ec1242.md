### Title
Cross-user response hijacking via attacker-controlled `MessageID` colliding with a victim's in-flight WebAPI trigger request - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The Cooler `H-4` report is about an unprivileged (relative) party being able to force a "push" of an asset/response to an address it controls or to disrupt delivery, causing the wrong party to bear the consequence. The closest reachable analog in the Chainlink gateway is that the `savedCallbacks` map used to route a DON node's response back to the originating user request is keyed purely by a client-supplied `MessageID`, with no per-request uniqueness/ownership check enforced by the gateway.

### Finding Description
`gateway.ProcessRequest` decodes an incoming user message and, for "legacy" requests, calls `HandleLegacyUserMessage`, only checking `len(jsonRequest.ID) > 200` [1](#0-0) . Inside `HandleLegacyUserMessage`, the handler stores the caller's `callback` in a shared map keyed by the attacker-controlled `msg.Body.MessageID`, with no check that this ID is unique or not already in-flight: [2](#0-1) 

When a DON node later responds, `HandleNodeMessage` looks up and deletes the entry solely by `msg.Body.MessageID` and forwards the response to whichever callback is currently registered under that key: [3](#0-2) [4](#0-3) 

Because a `MessageID` collision simply overwrites the map entry (`h.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}`), an attacker who submits a second request with the *same* `MessageID` as a victim's still-pending request will replace the victim's saved callback with their own before the DON node's response arrives. When the node's response for that `MessageID` is eventually delivered, it is routed to the attacker's callback instead of the victim's — the attacker receives the victim's trigger response, and the victim's original HTTP request hangs until pruning/timeout (`pruneCallbacks`, `CallbackMaxAgeSec`) rather than receiving a response.

The identical class of bug (destination/routing controlled by an unprivileged actor with no ownership binding, causing legitimate response/delivery to be misdirected or lost) exists here just as it did in the Cooler `repayTo` case where the lender could redirect the "push" and force the wrong outcome for the counterparty.

### Impact Explanation
An unprivileged external client of the gateway (any caller that can reach `/v2` legacy WebAPI trigger message endpoint) can cause:
- Cross-user response confusion: the attacker's client receives another user's/workflow's trigger response payload.
- Denial of the legitimate request: the victim's original HTTP call to the gateway stalls until the callback ages out (`CallbackMaxAgeSec`, default 120s) and then errors with a timeout, rather than getting its intended DON response.

This does not directly move funds but does violate response confidentiality/integrity and availability guarantees between callers sharing a DON handler, which is the same "wrong recipient receives an outcome intended for someone else" root cause as the referenced report.

### Likelihood Explanation
Exploitation requires only knowledge/guess of another caller's `MessageID` value at the time it is in-flight (a narrow race window between request submission and node response). This is somewhat harder than a guaranteed exploit (it needs timing plus knowledge of a specific victim's `MessageID`), but the newer `v2` HTTP trigger handler mitigates this by rejecting IDs containing `/` and there under `validateRequestID` still relies solely on request-scoped IDs without any binding to caller identity except via signed JWT/authorization elsewhere in that path — meaning the legacy handler path (`core/services/gateway/handlers/capabilities/handler.go`) is the primary affected surface, since it has no such per-caller binding at all.

### Recommendation
Bind the saved-callback key to a value that cannot be forged or collided across users, e.g., derive/prefix the internal callback-map key with the authenticated caller/DON member identity or a gateway-generated nonce, and reject/detect duplicate `MessageID`s for still-pending requests before overwriting an existing `savedCallbacks` entry (return an error instead of silently overwriting, similar to the "duplicate message received for ID" check already used in `OutgoingConnectorHandler.handleSingleNodeRequest`) [5](#0-4) .

### Proof of Concept
1. Victim submits a legacy WebAPI trigger request to the gateway with `MessageID = "X"`. `HandleLegacyUserMessage` stores `h.savedCallbacks["X"] = victimCallback` and forwards the request to all DON members.
2. Before the DON node responds, attacker submits their own legacy request using the identical `MessageID = "X"`. `HandleLegacyUserMessage` overwrites `h.savedCallbacks["X"] = attackerCallback`.
3. The DON node responds for `MessageID = "X"` (correlating to the victim's original forwarded request). `HandleNodeMessage`/`handleWebAPITriggerMessage` looks up `savedCallbacks["X"]`, finds the attacker's callback, and delivers the victim's response to the attacker.
4. The victim's original HTTP call to the gateway blocks until `callback.Wait(ctx)` times out in `gateway.ProcessRequest`, returning `api.RequestTimeoutError` instead of the real DON response.

I could not fully verify whether any additional caller-identity binding exists upstream of `HandleLegacyUserMessage` in production deployment (e.g., at the HTTP layer or DON member address checks) that might mitigate collision across different callers versus the same caller reusing an ID; this would require tracing the full request path from the public HTTP listener into `gateway.ProcessRequest`, which was not fully covered by the indexed context.

### Citations

**File:** core/services/gateway/gateway.go (L221-234)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L248-267)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	msg, err := common.ValidatedMessageFromResp(resp)
	if err != nil {
		return err
	}
	if msg.Body.Sender != nodeAddr {
		return errors.New("message sender mismatch when reading from node ")
	}
	start := time.Now()
	switch msg.Body.Method {
	case MethodWebAPITrigger:
		err = h.handleWebAPITriggerMessage(ctx, msg, nodeAddr)
	case MethodWebAPITarget, MethodComputeAction, MethodWorkflowSyncer:
		err = h.handleWebAPIOutgoingMessage(ctx, msg, nodeAddr)
	default:
		err = fmt.Errorf("unsupported method: %s", msg.Body.Method)
	}
	h.metrics.recordHandleDuration(ctx, time.Since(start), msg.Body.Method, err == nil)
	return err
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-420)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L148-162)
```go

	userRateLimiter, err := lf.MakeRateLimiter(cresettings.Default.PerWorkflow.HTTPTrigger.RateLimit)
	if err != nil {
		return nil, fmt.Errorf("failed to create user rate limiter: %w", err)
	}

	mtlsRequestRateLimiter, err := lf.MakeRateLimiter(cresettings.Default.GatewayHTTPActionMtlsRequestRate)
	if err != nil {
		return nil, fmt.Errorf("failed to create mtls rate limiter: %w", err)
	}

	mtlsConcurrencyLimiter, err := limits.MakeResourcePoolLimiter(lf, cresettings.Default.GatewayHTTPActionMtlsConcurrencyLimit)
	if err != nil {
		return nil, fmt.Errorf("failed to create mtls concurrency limiter: %w", err)
	}
```

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L136-140)
```go
	ch, err := c.responses.new(messageID)
	if err != nil {
		return nil, fmt.Errorf("duplicate message received for ID: %s", messageID)
	}
	defer c.responses.cleanup(messageID)
```
