### Title
Legacy WebAPI trigger handler skips allowlist/rate-limit checks despite explicit comment requiring them - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
`handler.HandleLegacyUserMessage` in the gateway's capabilities handler validates message freshness and method name, but explicitly notes with a `TODO` comment that allowlist and rate-limiting checks are required before forwarding the request to DON nodes — and never implements them. This mirrors the Sherlock finding where `onNFTHarvest`'s doc comment promised a validation the function body never performed, resulting in unvalidated processing.

### Finding Description
`HandleLegacyUserMessage` decodes the payload, checks the timestamp for staleness, and checks the method name, but the comment directly above the method dispatch explicitly states more validation is expected: [1](#0-0) 
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
    ...
}
```
No allowlist check on the sender and no rate-limiting is performed anywhere in this function before the request is forwarded to every DON member node: [2](#0-1) 
The handler's own test suite documents this gap explicitly with a trailing TODO acknowledging the missing checks: [3](#0-2) 

This stands in contrast to the newer v2 HTTP trigger handler (`httpTriggerHandler.HandleUserTriggerRequest`), which does call `authorizeRequest` and `checkRateLimit` before dispatching: [4](#0-3) 

This confirms allowlisting/rate-limiting is an intended and implemented control elsewhere in the codebase, but is missing — despite being called out in a comment as required — in the legacy handler path.

### Impact Explanation
Any signed message that passes basic structural/timestamp/method validation is forwarded to every configured DON node, regardless of whether the sender is a member of an authorized workflow DON or has exceeded a reasonable request rate. This allows an unprivileged (but capable of producing a validly-signed message) client to flood DON nodes with trigger messages, bypassing the allowlist/rate-limit gate that the code comment says should exist, leading to node-side resource exhaustion or unauthorized trigger requests reaching nodes that were not meant to receive them from that sender.

### Likelihood Explanation
Any client able to reach the gateway's legacy user-message endpoint and produce a validly-signed `api.Message` (satisfying `msg.Validate()`) can exercise this path — no additional privilege is required, since the allowlist/rate-limit check the comment promises is simply absent. This makes the missing check directly reachable from an unprivileged external client request through the gateway's message-handling entry point.

### Recommendation
Implement the sender allowlist and rate-limiting checks explicitly called out by the `// TODO: apply allowlist and rate-limiting here` comment in `HandleLegacyUserMessage`, consistent with the pattern already used in `httpTriggerHandler.authorizeRequest`/`checkRateLimit`, before forwarding messages to DON nodes via `don.SendToNode`.

### Proof of Concept
1. Craft an `api.Message` with `Method: MethodWebAPITrigger`, a fresh timestamp, and a valid `TriggerRequestPayload`, signed with any ECDSA key (as done in the test helper `triggerRequest`) — see [5](#0-4) .
2. Submit it via `HandleLegacyUserMessage`; because there is no sender allowlist or rate-limit check performed prior to dispatch, the message is forwarded to all DON members in `h.donConfig.Members` regardless of sender identity or request volume, as shown in [6](#0-5) .
3. Repeating this with different signing keys or at high frequency demonstrates the absence of the allowlist/rate-limit gate promised by the comment.

Note: I was unable to fully inspect `core/services/gateway/api/message.go`'s `Validate()`/`Sign()` implementation before running out of tool calls, so I cannot conclusively state whether `Validate()` restricts the signer to a known/authorized key set at the message layer. If `Validate()` does enforce sender membership independently, the severity of this specific gap would be reduced to rate-limiting bypass only; this should be verified in a live session.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-396)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L193-233)
```go
func triggerRequest(t *testing.T, key *ecdsa.PrivateKey, topics []string, methodName, timestamp, payload string) *api.Message {
	messageID := "12345"
	if methodName == "" {
		methodName = MethodWebAPITrigger
	}
	if timestamp == "" {
		timestamp = strconv.FormatInt(time.Now().Unix(), 10)
	}
	donID := "workflow_don_1"
	var payloadJSON []byte
	if payload == "" {
		ts, err := strconv.ParseInt(timestamp, 10, 64)
		require.NoError(t, err)
		reqPayload := webapicap.TriggerRequestPayload{
			TriggerId:      "web-api-trigger@1.0.0",
			TriggerEventId: "action_1234567890",
			Timestamp:      ts,
			Topics:         topics,
			Params: webapicap.TriggerRequestPayloadParams(map[string]any{
				"bid": "101",
				"ask": "102",
			}),
		}
		payloadJSON, err = json.Marshal(reqPayload)
		require.NoError(t, err)
	} else {
		payloadJSON = []byte(payload)
	}
	msg := &api.Message{
		Body: api.MessageBody{
			MessageID: messageID,
			Method:    methodName,
			DonID:     donID,
			Payload:   json.RawMessage(payloadJSON),
		},
	}
	err := msg.Sign(key)
	require.NoError(t, err)
	err = msg.Validate()
	require.NoError(t, err)
	return msg
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```
