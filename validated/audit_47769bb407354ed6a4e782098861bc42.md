## Analysis

I found a valid analog: a missing-authorization check in the legacy Web API trigger path of the gateway's capabilities handler, directly mirroring the CDP contract bug where a privileged-only action (`repay_stable_coin`) can be invoked by anyone because the caller isn't verified.

### Title
Missing allowlist/authorization check lets any client trigger workflow execution via the legacy Web API gateway path - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The Chainlink gateway's `capabilities` handler exposes a legacy user-message path (`HandleLegacyUserMessage`) that forwards a `web_api_trigger` request to every member node of a DON without performing any authorization/allowlist check on the caller, unlike the parallel `vault` handler which enforces an `Authorizer`/allowlist before processing any privileged method.

### Finding Description
`HandleLegacyUserMessage` validates the message age, decodes the payload, and checks that `msg.Body.Method == MethodWebAPITrigger`, but the code explicitly notes the missing control: [1](#0-0) 

Specifically: [2](#0-1) 

After that comment (`// TODO: apply allowlist and rate-limiting here`), the request is transformed and broadcast to all DON members with no ownership/allowlist verification of the caller: [3](#0-2) 

Compare this with the `vault` gateway handler's `HandleJSONRPCUserMessage`, which routes every privileged secrets method through `requestProcessor.ProcessRequest` (backed by `Authorizer`/`allowListBasedAuth`) before any node interaction: [4](#0-3) 

The `web_api_trigger` legacy path lacks the equivalent authorization gate — just as the CDP contract's `repay_stable_coin` function lacked a caller-identity check to ensure only the trusted `stable_pool` contract could invoke it, here nothing ensures only workflows/owners entitled to trigger a DON's capability can do so. Any client capable of reaching the gateway's user-facing HTTP endpoint (`gateway.ProcessRequest` → `HandleLegacyUserMessage`, per `core/services/gateway/gateway.go:270-272`) can construct a `web_api_trigger` message and have it broadcast to every node in the target DON.

### Impact Explanation
An unprivileged/unauthenticated caller can invoke DON-wide execution paths (capability trigger dispatch to every DON member node) without being an allowlisted workflow owner. This can cause unauthorized workflow trigger fan-out, DoS via forced processing across nodes, and potentially unauthorized state changes if downstream capability nodes trust that a `web_api_trigger` message reaching them was pre-authorized by the gateway (mirroring the "act without proper authorization" root cause of the CDP report).

### Likelihood Explanation
The vulnerable code path is reachable directly from `gateway.ProcessRequest`, the top-level entry point for legacy (DON-ID-bearing) user messages, requiring only network access to the gateway's user-facing HTTP port — no credentials or session are checked in the legacy trigger flow. The `TODO` comment in the source itself confirms the control is known to be absent, indicating high likelihood of exploitation if this path is reachable/enabled in production DON configurations.

### Recommendation
Add allowlist/authorization enforcement to `HandleLegacyUserMessage` (or route `web_api_trigger` through the same `Authorizer`/allowlist pattern used in `core/services/gateway/handlers/vault/handler.go`) before forwarding the message to `don.SendToNode` for any DON member, verifying the sender/owner against the DON's configured allowlist prior to broadcast.

### Proof of Concept
1. Send a JSON body to the gateway's user HTTP endpoint containing a legacy `api.Message` with `Body.DonID` set to a target DON and `Body.Method = "web_api_trigger"`, with a valid `TriggerRequestPayload.Timestamp` within `MaxAllowedMessageAgeSec`.
2. `gateway.ProcessRequest` routes it via `isLegacyRequest` to `h.HandleLegacyUserMessage` (`core/services/gateway/gateway.go:253-272`).
3. `HandleLegacyUserMessage` performs no allowlist check on the caller, then calls `don.SendToNode` for every member of `h.donConfig.Members` (`core/services/gateway/handlers/capabilities/handler.go:416-420`), causing the trigger to be dispatched to the entire DON despite the caller never being verified as an authorized workflow owner.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L383-397)
```go
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

**File:** core/services/gateway/handlers/vault/handler.go (L422-434)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```
