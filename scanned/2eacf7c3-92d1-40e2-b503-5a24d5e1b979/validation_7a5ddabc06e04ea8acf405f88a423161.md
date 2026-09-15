## Analysis

The Gondi finding describes borrower signatures that remain valid until `expirationTime` and can be replayed multiple times to re-execute the same signed offer, because no nonce/replay-guard exists — only a time-bound check.

Searching the chainlink codebase for the equivalent "unprivileged external request + signed message + no replay tracking" pattern shows that this exact class of bug **has already been addressed** in the newer gateway/vault code paths, but is still present in the **legacy Web API Trigger path**.

### Where replay protection exists (mitigated)
- Vault JWT/allowlist auth uses `RequestReplayGuard.CheckAndRecord` keyed by request digest with expiry [1](#0-0) .
- `WorkflowMetadataHandler.Authorize` and the v2 HTTP Trigger handler enforce a JWT `jti`-based `jwtReplayCache` so a signed JWT can only authorize a request once [2](#0-1) .

### Where it is missing (the analog)
The **legacy** Web API Trigger message path only performs a timestamp freshness check — it never records or rejects an already-seen signature/message:

`handler.HandleLegacyUserMessage` decodes the payload, checks `payload.Timestamp == 0` and that the message isn't older than `MaxAllowedMessageAgeSec`, but has no dedup/nonce check before fanning the signed message out to all DON nodes: [3](#0-2) 

The `savedCallbacks` map is keyed by `msg.Body.MessageID` and is deleted as soon as one node responds [4](#0-3) , so the same signed message can be resubmitted through the gateway repeatedly (as long as it's within the freshness window) and will be processed again as a brand-new request each time.

On the DON side, `triggerConnectorHandler.processTrigger` re-validates sender/topic/rate-limit but does **not** track which `TriggerEventID`s (`body.Sender + payload.TriggerEventId`) have already been fired — it only uses this ID for logging/execution-ID generation, not for de-duplication: [5](#0-4) 

This means a captured/observed valid signed `web-api-trigger` message (whose signature is valid over `MessageID`/`Method`/`DonID`/`Receiver`/`Payload`, see `Message.Sign`) can be resubmitted to the gateway by anyone (an unprivileged network observer, since gateway HTTP endpoints are internet-facing) to re-trigger the same workflow execution multiple times within the message's freshness window, each producing a new execution — the direct analog of the Gondi "borrower signature reuse" issue, mitigated elsewhere in the codebase (vault, v2 HTTP trigger) but not in this legacy trigger path.

Given the "Unmitigated / Acknowledged" framing of the source report itself (the sponsor explicitly acknowledged replay is possible and only documented it rather than fixing it), this is presented as informational, but the chainlink analog above is a concrete code path where the same missing control exists and is reachable from an unauthenticated/unprivileged external caller through the gateway's legacy Web API Trigger endpoint.

### Title
Legacy Web API Trigger messages lack replay/nonce protection, allowing repeated workflow execution from a captured signed message - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
`handler.HandleLegacyUserMessage` and `triggerConnectorHandler.processTrigger` validate a signed gateway `Message` only by signature validity and a coarse timestamp freshness window (`MaxAllowedMessageAgeSec`). Neither the gateway nor the DON-side trigger handler records previously-seen message IDs/trigger event IDs to reject replays, unlike the vault (`RequestReplayGuard`) and v2 HTTP trigger (JWT `jti` cache) paths.

### Finding Description
`HandleLegacyUserMessage` checks `payload.Timestamp != 0` and staleness against `MaxAllowedMessageAgeSec`, then forwards the request to all DON members [6](#0-5) . The response-correlation map `savedCallbacks` is deyed by `MessageID` and deleted after the first response is sent, so resubmitting the identical signed message is not rejected as a duplicate by the gateway. On the node side, `processTrigger` matches by sender/topic/rate limit but keeps no record of consumed `TriggerEventID`s, so the same signed payload can be delivered to the workflow trigger channel again [5](#0-4) .

### Impact Explanation
An attacker who observes or captures a valid signed `web-api-trigger` message (e.g., from network traffic, logs, or a previously-authorized client) can resend it to the gateway within the freshness window and cause the target workflow to execute again — potentially multiple times — without needing the private key or a new authorization. Depending on the workflow's side effects (fund movement, external API calls, state changes), this can duplicate real-world actions.

### Likelihood Explanation
Moderate: requires capturing a valid signed message, which is architecturally possible since these are legacy client-facing gateway endpoints without a nonce and the freshness window (`MaxAllowedMessageAgeSec`) can be several seconds/minutes, giving a practical replay window.

### Recommendation
Apply the same replay-guard pattern already used for vault and v2 HTTP trigger requests: track consumed `MessageID`/`TriggerEventID` values (e.g., via a `RequestReplayGuard`-style cache keyed by ID with TTL equal to `MaxAllowedMessageAgeSec`) in both `handler.HandleLegacyUserMessage` and `triggerConnectorHandler.processTrigger`, rejecting any message whose ID has already been processed.

### Proof of Concept
1. Client signs and sends a valid `web-api-trigger` message to the gateway within `MaxAllowedMessageAgeSec`.
2. Gateway processes it, forwards to DON nodes, `processTrigger` fires the trigger and workflow executes.
3. Attacker resends the identical signed message (same `MessageID`/`Signature`) before it becomes stale.
4. Gateway re-validates timestamp/signature successfully (no ID tracking) and forwards again; `processTrigger` fires the trigger a second time, causing duplicate workflow execution.

### Citations

**File:** core/capabilities/vault/request_replay_guard.go (L30-47)
```go
// CheckAndRecord returns ErrRequestAlreadySeen if the digest was previously
// recorded and has not yet expired. Otherwise it records the digest with
// the given expiry timestamp (unix seconds, UTC).
//
// Expired entries are cleaned up on every call.
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-107)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
	if _, exists = keys[key]; !exists {
		h.lggr.Errorw("Signer not found in authorized keys", "signer", signer.Hex())
		return nil, fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)
	}
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-420)
```go
	if payload.Timestamp == 0 {
		h.lggr.Errorw(ErrDecodingPayload)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115: comparing unix timestamps, both fit within uint
		h.lggr.Errorw("stale message")
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.HandlerError),
				"stale message",
				nil,
			),
			ErrorCode: api.HandlerError,
		})
	}
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

**File:** core/capabilities/webapi/trigger/trigger.go (L106-153)
```go
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
				TriggerEventID := body.Sender + payload.TriggerEventId

				// Emit trigger execution started event
				workflowExecutionID, genErr := events.GenerateExecutionID(trigger.workflowID, TriggerEventID)
				if genErr != nil {
					h.lggr.Errorw("failed to generate execution ID", "err", genErr)
					workflowExecutionID = ""
				}
				emitErr := events.EmitTriggerExecutionStarted(ctx, map[string]string{}, TriggerEventID, workflowExecutionID)
				if emitErr != nil {
					h.lggr.Errorw("failed to emit trigger execution started event", "err", emitErr)
				}

				tr := capabilities.TriggerResponse{
					Event: capabilities.TriggerEvent{
						TriggerType: TriggerType,
						ID:          TriggerEventID,
						Outputs:     wrappedPayload,
					},
				}
				trigger.chWriteMu.Lock()
				if trigger.ch == nil {
					trigger.chWriteMu.Unlock()
					return nil
				}
				select {
				case <-ctx.Done():
					trigger.chWriteMu.Unlock()
					return nil
				case trigger.ch <- tr:
					trigger.chWriteMu.Unlock()
					// Sending n topics that match a workflow with n allowedTopics, can only be triggered once.
					break
				}
```
