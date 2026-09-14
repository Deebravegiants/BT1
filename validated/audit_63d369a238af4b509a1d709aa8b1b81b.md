## Analog Found

### Title
Missing sender/workflow allowlist check before forwarding user-triggered messages to DON nodes - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The Allora `OnRecvPacket` bug is a case where an incoming, unauthenticated-by-channel/sender message is processed and forwarded downstream without verifying the sender is authorized to trigger that action. The Chainlink Gateway has a directly analogous gap: `handler.HandleLegacyUserMessage` accepts an unprivileged, internet-facing user request (`MethodWebAPITrigger`) and forwards it to every node in the DON without any allowlist or authorization check on the sender, despite an explicit unresolved `TODO` marking this gap.

### Finding Description
The gateway's user-facing entry point `gateway.ProcessRequest` decodes an inbound request and, for `isLegacyRequest` (message with a `DonID`), calls `msg.Validate()` (which only validates message shape/signature format) and then dispatches to `h.HandleLegacyUserMessage(ctx, msg, callback)`: [1](#0-0) 

Inside `HandleLegacyUserMessage`, the handler validates the payload structure and timestamp freshness, but the authorization step is explicitly missing, marked by a `TODO`: [2](#0-1) 

Immediately after that unimplemented check, the handler converts the message to a request and unconditionally broadcasts it to every DON member: [3](#0-2) 

This mirrors the report's root cause: the incoming request is only checked for well-formedness (analogous to unmarshalling the ICS-20 packet), but the actual authorization check — verifying the sender/channel is permitted to invoke this action — is commented out / not implemented (`TODO: apply allowlist and rate-limiting here` vs. Allora's commented-out `if data.Sender != AxelarGMPAcc`). In both cases, unauthorized principals reach privileged downstream logic (DON node execution vs. ICS-20 transfer + GMP payload handling) purely because the surrounding structural validation succeeds.

By contrast, other gateway handlers in the same codebase (e.g. Vault's `GatewayHandler`) explicitly wire an `Authorizer`/allowlist check into the request pipeline before processing: [4](#0-3) 

confirming that allowlist-based sender authorization is the established pattern this handler is missing.

### Impact Explanation
Because `HandleLegacyUserMessage` sends the triggered request to **every member of the DON** (`for _, member := range h.donConfig.Members { ... don.SendToNode(ctx, member.Address, req) }`), any unprivileged HTTP client that can reach the Gateway's user port can trigger `web_api_trigger` workflow execution requests on all nodes in the DON, without being checked against a workflow-specific sender allowlist at this layer. This can result in unauthorized triggering of workflow runs (a job-run authorization bypass analog to unauthorized packet processing in the IBC report), potential resource exhaustion of DON nodes, and unintended execution paths being invoked by unvetted senders.

### Likelihood Explanation
The path is reachable directly from an unprivileged client: `gateway.ProcessRequest` is the HTTP-facing entry point invoked for any external request, and it unconditionally calls `HandleLegacyUserMessage` for any legacy (DonID-bearing) message that passes basic `msg.Validate()` structural checks — no additional authentication of the sender/workflow is performed before dispatch to nodes. The `TODO` comment confirms this is a known, currently-unaddressed gap in the shipped code rather than a hypothetical scenario.

### Recommendation
Implement the missing allowlist/authorization check flagged by the `TODO` in `HandleLegacyUserMessage` before dispatching to DON nodes — verify that `msg.Body.Sender` (and associated workflow/topic) is permitted to invoke `MethodWebAPITrigger` for the target DON, mirroring the `Authorizer`/allowlist pattern already used in `core/capabilities/vault/gw_handler.go`, and apply the appropriate rate limiting per sender prior to broadcasting requests to node members.

### Proof of Concept
1. An unprivileged client sends a well-formed legacy JSON-RPC request to the Gateway's user HTTP port with `Body.Method = "web_api_trigger"`, a valid `DonID`, and a fresh `Timestamp` in the payload, but with an arbitrary/unauthorized `Sender`.
2. `gateway.ProcessRequest` validates only structural correctness via `msg.Validate()` and routes to `HandleLegacyUserMessage`.
3. `HandleLegacyUserMessage` checks payload decoding, timestamp staleness, and method name — but performs no allowlist check on `Sender` (per the `TODO`) — then calls `common.ValidatedRequestFromMessage` and loops over `h.donConfig.Members`, sending the trigger request to every node in the DON via `don.SendToNode`.
4. The unauthorized sender's trigger request is thus processed and forwarded to all DON nodes as if legitimate.

### Citations

**File:** core/services/gateway/gateway.go (L253-279)
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
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L397-420)
```go
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

**File:** core/capabilities/vault/gw_handler.go (L108-112)
```go
	if authorizer == nil {
		allowListBasedAuth := NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
		authorizer = NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)
	}

```
