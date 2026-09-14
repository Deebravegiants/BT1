### Title
Missing sender allowlist/authorization check before broadcasting legacy user messages to all DON nodes - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Gateway's `HandleLegacyUserMessage` accepts an unauthenticated, internet-facing user request and forwards it to every node in the DON without any allowlist, sender-reputation, or authorization check — this is explicitly called out as an unfinished TODO in the code itself.

### Finding Description
`(h *handler) HandleLegacyUserMessage` is the entrypoint the Gateway invokes for each user-submitted `api.Message` on the legacy (non-JSON-RPC) path. It performs payload decoding, timestamp/staleness checks, and method-name validation, but the line directly above the method check contains:

```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [1](#0-0) 

After these checks, the message is transformed via `common.ValidatedRequestFromMessage` and unconditionally broadcast to every DON member:
```go
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [2](#0-1) 

There is no check anywhere in this function that verifies the message sender (`msg.Body.Sender`, populated from the message signature via `Validate()`) is a member of an allowlist before the request is dispatched to node infrastructure. This is analogous to the reported bug class: input (here, a user-controlled gateway message) is accepted and acted upon by privileged downstream systems (DON nodes) without validating that its origin/content is authorized — mirroring the original report's concern about consuming untrusted/unverified input without a validity check.

Other handlers in the same package do perform this check — e.g. `webapi/outgoing_connector_handler.go` applies `incomingRateLimiter.AllowVerbose(body.Sender)` before acting on gateway messages [3](#0-2) , and `vault/gw_handler.go` routes every secrets request through `requestProcessor.ProcessRequest`/`Authorizer.AuthorizeRequest` before acting [4](#0-3) . The legacy capabilities handler's `HandleLegacyUserMessage` path lacks this equivalent control.

### Impact Explanation
Because the missing check sits on the path from an unauthenticated internet-facing user request straight to `don.SendToNode`, any external caller able to reach the Gateway's legacy user-message endpoint can cause requests to be relayed to every configured DON node, bypassing any intended per-sender allowlist and rate limiting that this code comment says is expected but not implemented. This can enable unauthorized job/trigger dispatch amplification and resource exhaustion of DON node infrastructure from unprivileged clients, and undermines any operator assumption that only allowlisted senders can trigger DON-side processing through this handler.

### Likelihood Explanation
Likelihood is high in the sense that the code path requires no authentication beyond a syntactically valid signed `api.Message` (which any client can construct with its own keypair, since `Validate()` only checks message format and extracts the signer — it does not check it against an allowlist). The main uncertainty is whether the legacy `HandleLegacyUserMessage` path is still reachable/enabled in current production Gateway configurations versus being superseded by the JSON-RPC/vault/webapi handlers that do enforce authorization — this could not be fully confirmed from the indexed code (the concrete HTTP-to-handler wiring for the legacy path was not found in the searched files).

### Recommendation
Implement the allowlist and rate-limiting check called out in the TODO comment in `HandleLegacyUserMessage` before the request is forwarded to `don.SendToNode`, mirroring the pattern used in `OutgoingConnectorHandler.HandleGatewayMessage` (rate limiter) and the vault `GatewayHandler` (`Authorizer.AuthorizeRequest`), so that only allowlisted/authorized senders' messages reach DON nodes.

### Proof of Concept
Not independently exploitable/verifiable from static review alone — the finding rests on the explicit `// TODO: apply allowlist and rate-limiting here` comment at [5](#0-4)  combined with the unconditional broadcast loop at [2](#0-1) , showing no allowlist enforcement occurs between message validation and node dispatch in this function.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L416-420)
```go
	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L318-332)
```go
	senderAllow, globalAllow := c.incomingRateLimiter.AllowVerbose(body.Sender)
	errJSON := jsonrpc.WireError{
		Code:    500,
		Message: "",
	}
	if !senderAllow {
		errJSON.Message = errorIncomingRatelimitSender
	}
	if !globalAllow {
		if errJSON.Message == "" {
			errJSON.Message = errorIncomingRatelimitGlobal
		} else {
			errJSON.Message += "\n" + errorIncomingRatelimitGlobal
		}
	}
```

**File:** core/capabilities/vault/gw_handler.go (L187-206)
```go
	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
```
