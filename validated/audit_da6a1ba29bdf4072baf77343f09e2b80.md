I have enough confirmation now. `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` forwards `web_api_trigger` messages to all DON nodes without any sender/allowlist check at the gateway layer — the actual `AllowedSenders`/`allowedTopics` enforcement lives only downstream, inside `RegisterTrigger`/trigger execution on the node side (`core/capabilities/webapi/trigger/trigger.go`), not in the gateway's `HandleLegacyUserMessage`. This matches the OpenClaw bug class: an interactive/callback-style entry point that is reachable and forwards attacker-controlled input before the sender authorization layer has had a chance to reject it.

### Title
Gateway forwards unauthenticated `web_api_trigger` legacy user messages to all DON nodes before any sender/allowlist check - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy web-API-capabilities handler (`HandleLegacyUserMessage`) accepts any inbound HTTP JSON-RPC-legacy request addressed to a DON, validates only structural/timestamp fields, and then broadcasts the request to every node in the DON — explicitly skipping sender allowlist and rate-limit enforcement, which is marked with a `TODO` comment and never implemented at this layer.

### Finding Description
`HandleLegacyUserMessage` is the entry point invoked by `gateway.ProcessRequest` (`core/services/gateway/gateway.go`) for any externally-submitted legacy request whose `DonID` resolves to a `web-api-capabilities` handler. The function:
1. Decodes the payload and checks `Timestamp` staleness.
2. Contains the comment `// TODO: apply allowlist and rate-limiting here` immediately before checking only that `msg.Body.Method == MethodWebAPITrigger`.
3. Calls `common.ValidatedRequestFromMessage(msg)` (signature/structure validation only — no sender authorization).
4. Saves the callback and forwards the request to **every** node in `h.donConfig.Members` via `don.SendToNode`. [1](#0-0) 

No sender allowlist, workflow-owner allowlist, or `allowedSenders`/`allowedTopics` gating exists in this gateway-layer path. The only allowlist enforcement (`allowedSenders`, `allowedTopics`) for `web_api_trigger` payloads is implemented much later, inside the per-workflow `webapiTrigger.processTrigger`/`RegisterTrigger` logic on the node side, driven by the config a workflow registered: [2](#0-1) 

The handler's own test suite explicitly flags this as an unresolved gap: `// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated`. [3](#0-2) 

This mirrors the OpenClaw bug class (GHSA-x2ff-j5c2-ggpr): an interactive/message-forwarding code path that performs structural validation but defers sender authorization to a later stage, allowing a request to be accepted and dispatched into the trusted processing pipeline (here, broadcast to all DON worker nodes) before any allowlist check occurs at the gateway boundary.

### Impact Explanation
Any unprivileged client able to reach the gateway's user-facing HTTP endpoint can submit a `web_api_trigger` legacy message for an arbitrary registered `DonID` without being on that trigger's `allowedSenders` list. The message is broadcast to every node in the DON before the node-side trigger logic evaluates the allowlist. While the ultimate node-side `allowedSenders` check should still reject unauthorized senders before the workflow executes, the gateway itself performs no authorization, meaning: (a) unauthorized traffic and resource consumption reach all DON nodes regardless of sender identity, (b) any DON-level authorization gap or inconsistency between gateway and node config is not defended in depth, and (c) the security boundary intended by `allowedSenders` is enforced solely by application logic deep in the node pipeline rather than at the gateway ingress, consistent with an authorization-bypass-adjacent design gap (CWE-863: Incorrect Authorization).

### Likelihood Explanation
High reachability: the codepath is hit for every externally-submitted legacy `web_api_trigger` request with no precondition beyond a valid `DonID`/timestamp — no authentication token or sender check is required to reach `don.SendToNode` for all DON members. The gap is also self-documented via the in-code `TODO` and the corresponding test-file TODO, confirming it is a known, currently-unaddressed gap rather than a subtle theoretical issue.

### Recommendation
Enforce sender/allowlist authorization at the gateway layer in `HandleLegacyUserMessage` before broadcasting to `don.SendToNode`, mirroring the `allowedSenders`/rate-limit checks already present in `RegisterTrigger` (`core/capabilities/webapi/trigger/trigger.go`), so unauthorized senders are rejected at the gateway ingress rather than solely relying on node-side enforcement.

### Proof of Concept
1. Register a `web_api_trigger` workflow with `allowedSenders = [addressA]` via `RegisterTrigger`.
2. From an unrelated client (not `addressA`, no allowlisted signature), submit a legacy JSON-RPC request to the gateway's `/` user endpoint with `DonID` set to the DON hosting that workflow and `Method = web_api_trigger`, with a valid signature/structure and fresh timestamp (satisfying `common.ValidatedRequestFromMessage` and the staleness check only).
3. Observe that `HandleLegacyUserMessage` accepts the request, saves the callback, and calls `don.SendToNode` for every member of `h.donConfig.Members` — i.e., the request reaches all DON nodes — without any gateway-side rejection based on sender identity, confirming the missing allowlist check described in the code's own `TODO`.

### Citations

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

**File:** core/capabilities/webapi/trigger/trigger.go (L212-269)
```go
func (h *triggerConnectorHandler) RegisterTrigger(ctx context.Context, req capabilities.TriggerRegistrationRequest) (<-chan capabilities.TriggerResponse, error) {
	cfg := req.Config
	if cfg == nil {
		return nil, errors.New("config is required to register a web api trigger")
	}

	reqConfig, err := h.ValidateConfig(cfg)
	if err != nil {
		return nil, err
	}

	if len(reqConfig.AllowedSenders) == 0 {
		return nil, errors.New("allowedSenders must have at least 1 entry")
	}

	h.mu.Lock()
	defer h.mu.Unlock()
	_, errBool := h.registeredWorkflows[req.TriggerID]
	if errBool {
		return nil, fmt.Errorf("triggerId %s already registered", req.TriggerID)
	}

	rateLimiterConfig := reqConfig.RateLimiter
	commonRateLimiter := ratelimit.RateLimiterConfig{
		GlobalRPS:      rateLimiterConfig.GlobalRPS,
		GlobalBurst:    int(rateLimiterConfig.GlobalBurst),
		PerSenderRPS:   rateLimiterConfig.PerSenderRPS,
		PerSenderBurst: int(rateLimiterConfig.PerSenderBurst),
	}

	rateLimiter, err := ratelimit.NewRateLimiter(commonRateLimiter)
	if err != nil {
		return nil, err
	}

	allowedSendersMap := map[string]bool{}
	for _, k := range reqConfig.AllowedSenders {
		allowedSendersMap[k] = true
	}

	allowedTopicsMap := map[string]bool{}
	for _, k := range reqConfig.AllowedTopics {
		allowedTopicsMap[k] = true
	}

	ch := make(chan capabilities.TriggerResponse, defaultSendChannelBufferSize)

	h.registeredWorkflows[req.TriggerID] = &webapiTrigger{
		workflowID:     req.Metadata.WorkflowID,
		allowedTopics:  allowedTopicsMap,
		allowedSenders: allowedSendersMap,
		ch:             ch,
		config:         *reqConfig,
		rateLimiter:    rateLimiter,
	}

	return ch, nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L339-366)
```go
	t.Run("savedCallbacks stored only when message is valid", func(t *testing.T) {
		require.Empty(t, handler.savedCallbacks)

		invalidPayloadMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "123456", `{"foo":"bar"}`)
		cb := hc.NewCallback()
		err := handler.HandleLegacyUserMessage(ctx, invalidPayloadMsg, cb)
		require.NoError(t, err)
		_, _ = cb.Wait(t.Context())

		staleMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "", "123456", "")
		cb2 := hc.NewCallback()
		err = handler.HandleLegacyUserMessage(ctx, staleMsg, cb2)
		require.NoError(t, err)
		_, _ = cb2.Wait(t.Context())

		badMethodMsg := triggerRequest(t, nodes[0].PrivateKey, []string{"daily_price_update"}, "foo", "", "")
		cb3 := hc.NewCallback()
		err = handler.HandleLegacyUserMessage(ctx, badMethodMsg, cb3)
		require.NoError(t, err)
		_, _ = cb3.Wait(t.Context())

		handler.mu.Lock()
		require.Empty(t, handler.savedCallbacks, "error paths must not leave entries in savedCallbacks")
		handler.mu.Unlock()
	})

	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```
