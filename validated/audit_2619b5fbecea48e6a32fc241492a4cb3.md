Audit Report

## Title
Missing allowlist and rate-limiting enforcement on legacy WebAPI trigger user messages allows any client to broadcast unauthenticated requests to an entire DON - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`HandleLegacyUserMessage` in the capabilities gateway handler only validates message structure (payload decoding, non-zero timestamp, staleness, and the `Method` value) before saving a callback and broadcasting the request to every member of the DON via `don.SendToNode`. The code contains an explicit, unresolved `// TODO: apply allowlist and rate-limiting here` directly before dispatch, confirming that the intended authorization/rate-limit gate is not implemented.

## Finding Description
The call chain is `gateway.ProcessRequest` → `msg.Validate()` (structural JSON-RPC/message validation) → `handler.HandleLegacyUserMessage`, as shown in [1](#0-0) . Inside `HandleLegacyUserMessage`, the only checks performed are payload decoding, a non-zero timestamp check, and a staleness check [2](#0-1) , followed immediately by the `TODO: apply allowlist and rate-limiting here` comment and a bare method-name check [3](#0-2) . No caller-identity, sender-allowlist, or per-caller rate-limit check exists anywhere in this path before the request is registered as a pending callback and fanned out to every DON member [4](#0-3) . The `nodeRateLimiter` field on the handler is only applied to outgoing node messages in `handleWebAPIOutgoingMessage` [5](#0-4) , not to inbound user messages, confirming the gap is real and not mitigated elsewhere in this file.

## Impact Explanation
This maps to a gateway allowlist/rate-limit bypass: any caller who can reach the gateway's legacy user-message endpoint can force `HandleLegacyUserMessage` to broadcast a `web_api_trigger` request to every node in the configured DON with only structural validation, with no verification of caller identity or workflow/DON authorization. This causes resource consumption on the DON (fan-out to all members) and growth of the `savedCallbacks` map, bounded only by pruning, bypassing the protection that an allowlist/rate-limiter is meant to provide before a state-changing/costly broadcast action.

## Likelihood Explanation
High: this is the unconditional default code path for any legacy user message reaching this handler; it requires no privileged role, valid signature beyond basic message validation, or special network position — only a structurally valid, non-stale payload with `Method = "web_api_trigger"`.

## Recommendation
Implement the allowlist and rate-limiting checks referenced by the TODO in `HandleLegacyUserMessage` before saving the callback and broadcasting to DON members, consistent with the JWT/rate-limit enforcement present in the v2 HTTP trigger handler.

## Proof of Concept
1. Send a JSON-RPC message to the gateway's legacy user endpoint with `Body.DonID` set to a configured DON, `Body.Method = "web_api_trigger"`, a valid non-stale `Timestamp`, and an arbitrary `TriggerRequestPayload`.
2. Observe that `gateway.ProcessRequest` routes it to `HandleLegacyUserMessage` [1](#0-0) , which passes the timestamp/method checks and, per the TODO marker, performs no allowlist or rate-limit check [3](#0-2)  before saving a callback and calling `don.SendToNode` for every DON member [4](#0-3) .
3. Repeat from a single client to confirm unthrottled fan-out to all DON nodes and unbounded growth of `savedCallbacks` until pruning triggers.

### Citations

**File:** core/services/gateway/gateway.go (L253-272)
```go
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-383)
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
```

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L410-420)
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
