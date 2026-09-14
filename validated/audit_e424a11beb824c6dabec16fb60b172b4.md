### Title
Unauthenticated `web-api-capabilities` trigger requests are broadcast to all DON nodes with no sender allowlist, enabling request impersonation - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy `WebAPICapabilitiesType` handler (`core/services/gateway/handlers/capabilities/handler.go`) accepts any external HTTP user's `web_api_trigger` message, performs only payload-shape and staleness checks, and then fans the raw, attacker-controlled request out to **every member of the DON** — without verifying that the sender is an authorized/allowlisted party for the target workflow.

### Finding Description
`HandleLegacyUserMessage` [1](#0-0)  decodes the incoming `TriggerRequestPayload`, checks it is non-empty and not stale [2](#0-1) , and then — right at the point where a sender check should occur — has an explicit unimplemented guard:

```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [3](#0-2) 

After this, the handler unconditionally forwards the validated request to **all** `donConfig.Members` (i.e., every capability node in the DON), registering a callback keyed by message ID to relay the first node response back to the caller: [4](#0-3) .

This is the direct structural analog of the `FeeSplitter.distributeFees` bug: a function reachable by any unprivileged caller (`distributeFees(_token)` / here, an HTTP `web_api_trigger` request to the gateway) that pushes attacker-supplied data (an arbitrary token / here, an arbitrary trigger payload) out to a fixed set of trusted parties (preset `feeRecipients` / here, all DON node members) with no check that the caller/data is legitimately associated with those recipients. The test suite for this exact code acknowledges the gap is unresolved: `handler_test.go` ends with `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated` [5](#0-4) , and the sad-path tests only cover decode/stale/method errors, never a "not allowed sender" case for this handler (contrast with the DON-side `trigger.go`, which does reject unauthorized senders on the node, but that's a downstream/backstop check, not a gateway-side allowlist) [6](#0-5) .

By contrast, the newer v2 HTTP trigger path documents JWT-based sender authentication and workflow-scoped authorized-key sets as required security controls [7](#0-6) , confirming that sender authentication at the gateway is the intended security boundary for this class of message — a boundary this legacy handler admits (via its own TODO) it does not enforce.

The `handler_factory.go` confirms this legacy handler type (`web-api-capabilities`) is still wired up and selectable in the running gateway alongside the v2 handler: [8](#0-7) .

### Impact Explanation
Because the request is broadcast unconditionally to every node in the DON, an unauthenticated caller can:
- Impersonate a legitimate workflow's trigger request toward all capability nodes in the DON (cross-user/cross-workflow request impersonation), since there is no verification that the sender is authorized to trigger the target workflow at the gateway layer.
- Cause DON nodes to receive and process attacker-controlled trigger payloads carrying the credibility of having passed through the gateway, mirroring the "phishing via trusted distribution" pattern in the reference report — nodes/workflows that trust gateway-forwarded messages as gateway-vetted may act on them.
- Amplify load/DoS against every DON member per request, since fan-out is to the full membership with only a node-side rate limiter (`nodeRateLimiter`), not a per-sender gateway-side check gating this specific flow.

The severity depends on what downstream trust the receiving nodes place in a message merely having arrived via the gateway's legacy path (the DON-node-side `trigger.go` sender check is a mitigating backstop, but it is a separate component and the gateway itself performs none of the documented allowlist/authorization).

### Likelihood Explanation
High reachability: the vulnerable path is a standard external user-facing HTTP entry point (`HandleLegacyUserMessage`) with only shape/staleness validation — no signature/allowlist verification — before broadcasting to the whole DON. The code's own TODO and the test suite's own acknowledged gap confirm this is a known, currently-unaddressed omission in a still-registered handler type.

### Recommendation
Implement the sender allowlist/authorization check called out in the TODO before forwarding to DON members — e.g., verify the message signature corresponds to a workflow owner/sender authorized for the specific workflow referenced in the trigger payload (mirroring the `AllowListBasedAuth`/JWT approach used in `core/capabilities/vault/allow_list_based_auth.go` and the v2 HTTP trigger handler) at `core/services/gateway/handlers/capabilities/handler.go:384` before the `don.SendToNode` fan-out loop at lines 417-419.

### Proof of Concept
1. Any external client sends an HTTP request to the gateway targeting the legacy `web-api-capabilities` handler with `Method = web_api_trigger` and a well-formed, non-stale `TriggerRequestPayload` referencing an arbitrary/unauthorized workflow ID and sender.
2. `HandleLegacyUserMessage` passes the payload-decode check and staleness check (attacker controls `Timestamp`).
3. Since no allowlist check is implemented (per the TODO), the request is forwarded via `don.SendToNode` to every node in `donConfig.Members` [9](#0-8) .
4. Every DON node receives what appears to be a gateway-relayed trigger request for a workflow the caller is not authorized to trigger.

Note: I was unable to fully verify at what layer (if any) `MethodWebAPITrigger`'s workflow-owner authorization is enforced downstream of the gateway for this specific legacy handler in production deployments — the DON-side `trigger.go` sender check exists but operates on a different sender/allowlist model, and the extent to which it fully closes this gap could not be conclusively established from the available code paths.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-357)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L365-366)
```go
	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```

**File:** core/capabilities/webapi/trigger/trigger_test.go (L276-289)
```go
	t.Run("sad case Not Allowed Sender", func(t *testing.T) {
		gatewayRequest := gatewayRequest(t, privateKey2, []string{"ad_hoc_price_update"}, "")
		th.connector.EXPECT().SignMessage(mock.Anything, mock.Anything).Return([]byte("signature"), nil).Once()
		th.connector.On("SendToGateway", mock.Anything, mock.Anything, mock.Anything).Run(func(args mock.Arguments) {
			resp, err2 := getResponseFromArg(args.Get(2))
			require.NoError(t, err2)

			require.Equal(t, ghcapabilities.TriggerResponsePayload{Status: "ERROR", ErrorMessage: "unauthorized Sender 0x2dAC9f74Ee66e2D55ea1B8BE284caFedE048dB3A, messageID 12345"}, resp)
		}).Return(nil).Once()

		th.trigger.HandleGatewayMessage(ctx, "gateway1", gatewayRequest)
		requireNoChanMsg(t, channel)
		requireNoChanMsg(t, channel2)
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L205-209)
```markdown
### 7.1 Authentication & Authorization

- **JWT Verification**: All trigger requests must include valid JWT tokens
- **Address Validation**: All addresses must be 0x-prefixed and lowercase
- **Workflow-Scoped Auth**: Each workflow maintains its own authorized key set
```

**File:** core/services/gateway/handler_factory.go (L81-94)
```go
	switch handlerType {
	case DummyHandlerType:
		return handlers.NewDummyHandler(donConfig, don, hf.lggr)
	case WebAPICapabilitiesType:
		return capabilities.NewHandler(handlerConfig, donConfig, don, hf.httpClient, hf.lggr)
	case HTTPCapabilityType:
		return v2.NewGatewayHandler(handlerConfig, shardedDONs, shardsConnMgrs, hf.httpClient, hf.lggr, hf.lf, hf.httpClientFactory, hf.orgResolver)
	case VaultHandlerType:
		return vault.NewHandler(handlerConfig, donConfig, don, hf.capabilitiesRegistry, hf.workflowRegistrySyncer, hf.lggr, clockwork.NewRealClock(), hf.lf)
	case ConfidentialRelayHandlerType:
		return confidentialrelay.NewHandler(handlerConfig, donConfig, don, hf.lggr, clockwork.NewRealClock(), hf.lf)
	default:
		return nil, fmt.Errorf("unsupported handler type %s", handlerType)
	}
```
