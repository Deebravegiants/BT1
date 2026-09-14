## Title
Missing allowlist/authorization check lets any unprivileged external caller trigger DON node webhook execution via the Gateway - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The Aave flashloan bug in the report is a case where a privileged callback path (`executeOperation`) trusts *any* caller that arrives through the expected intermediary (the lending pool) without verifying that the original initiator was actually authorized. The analogous pattern exists in chainlink's Gateway `capabilities` handler: `HandleLegacyUserMessage` forwards a signed, but otherwise unauthenticated/un-allowlisted, user request straight to every DON node, with the authorization check explicitly stubbed out via a `TODO`.

### Finding Description
`handler.HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` is the entry point the Gateway (`core/services/gateway/gateway.go`, `ProcessRequest`) uses for any legacy signed request that resolves to a DON handler. After basic sanity checks (payload decoding, timestamp/staleness, method match) it contains: [1](#0-0) 

```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
```

Immediately after this stubbed check, the request is turned into a signed node request and fanned out to every member of the DON: [2](#0-1) 

The only prior validation is that the message is well-formed and has a valid signature (`msg.Validate()` inside `common.ValidatedRequestFromMessage`) and is not stale - it does **not** verify that the signer is an authorized/allowlisted workflow owner or user. Any caller who can produce an ECDSA-signed `api.Message` (an unprivileged, unauthenticated party on the internet-facing Gateway HTTP endpoint) can therefore have their `web_api_trigger` payload delivered to every node in the DON, consuming node resources, triggering webhook logic, and occupying the `savedCallbacks` map that resource limits (`MaxSavedCallbacks`, pruning) only partially bound.

This mirrors the Aave analog precisely: the code assumes requests reaching this path have already gone through an authorization gate (an allowlist), but the gate is missing, so the "trusted-path" assumption is violated by any external, unprivileged initiator.

### Impact Explanation
An unauthenticated/unprivileged external actor can force every node in a capability DON to process a `web_api_trigger` webhook request of the attacker's choosing (bypassing the intended per-user/per-workflow allowlist that is supposed to gate this trigger). This can be used to run node compute/network resources on arbitrary payloads, exhaust the rate limiter/callback map budget for legitimate users, and trigger workflow executions that were never authorized for that caller - a form of unauthorized job/run invocation on behalf of the attacker through the Gateway's node-facing channel.

### Likelihood Explanation
The vulnerable path is directly reachable from an unauthenticated user request to the Gateway's public HTTP endpoint (`gateway.ProcessRequest` → `HandleLegacyUserMessage`), requiring only a validly-signed `api.Message` with method `web_api_trigger`, which any external party can construct with any ECDSA key. The missing check is explicitly marked with a `TODO` comment in the shipped code, confirming the gap is not intentional or otherwise mitigated elsewhere in this function.

### Recommendation
Before forwarding to `don.SendToNode`, `HandleLegacyUserMessage` must verify the request's signer/owner against the DON's/handler's configured allowlist (and apply the intended rate-limiting) - i.e., implement the work described by the `// TODO: apply allowlist and rate-limiting here` comment - and reject the request (respond with an authorization error) if the caller is not permitted to trigger that workflow/DON.

### Proof of Concept
1. Construct an `api.Message` with `Body.Method = MethodWebAPITrigger`, an arbitrary `TriggerRequestPayload` (valid `Timestamp`, arbitrary target), and sign it with any freshly generated ECDSA key (no relationship to any registered/allowlisted user).
2. Submit it to the Gateway's public HTTP user endpoint so it reaches `gateway.ProcessRequest` → `handler.HandleLegacyUserMessage`.
3. Observe that `msg.Validate()`/timestamp/method checks pass, the `TODO`'d allowlist check performs no verification, and the request is forwarded via `don.SendToNode` to every DON member, exactly as with a legitimate, allowlisted caller. [3](#0-2)

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-421)
```go
func (h *handler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback handlers.Callback) error {
	body := msg.Body
	var payload webapicap.TriggerRequestPayload
	codec := api.JSONRPCCodec{}
	err := json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw(ErrDecodingPayload, "err", err)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload+" "+err.Error(),
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

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
}
```
