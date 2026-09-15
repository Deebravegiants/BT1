### Title
Missing allowlist/authorization check in `capabilities.handler.HandleLegacyUserMessage` allows unauthenticated triggering of DON workflow execution - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The external report's bug class is a publicly reachable state-changing entry point (`checkMerkleRootAndVerifySignatures`) that lacks caller authentication/authorization, letting any unprivileged caller trigger fund-affecting logic that should only be reachable via an authenticated, gated path (`createNewTask`, guarded by `onlyBatcher`). The closest reachable analog in this chainlink codebase is the internet-facing Gateway's legacy web-API capability handler, which forwards unauthenticated user HTTP requests directly to all DON nodes with an explicit unimplemented authorization check.

### Finding Description
The Gateway's public HTTP entry point `gateway.ProcessRequest` [1](#0-0)  routes any legacy request (one that carries a `DonID`) to `handler.HandleLegacyUserMessage` after only calling `msg.Validate()`, which performs structural validation, not caller authorization.

Inside `HandleLegacyUserMessage`, the code explicitly marks the missing check with a `TODO` comment and proceeds to broadcast the trigger request to every member node of the DON regardless of who sent it: [2](#0-1) 

Specifically:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
    ...
}
req, err := common.ValidatedRequestFromMessage(msg)
...
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
```
There is no verification of `msg.Body.Sender`/workflow ownership, no allowlist lookup, and no rate limiting before forwarding the trigger to the DON — unlike the JSON-RPC path in the same package, which explicitly rejects such messages (`HandleJSONRPCUserMessage` at line 295 returns an error for this handler), and unlike the Vault capability's gateway handler (`core/capabilities/vault/gw_handler.go`) and the v2 HTTP trigger handler (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go`), which both perform explicit `AuthorizeRequest`/JWT checks before processing.

This mirrors the Solidity bug pattern exactly: a function that is reachable by any unprivileged actor and performs a state-mutating, resource-consuming action (triggering workflow execution across an entire DON) without the access control that a sibling/expected code path enforces.

### Impact Explanation
Any unauthenticated client that can reach the Gateway's user-facing HTTP server can submit a `web_api_trigger` legacy message with an arbitrary `DonID` and have it broadcast to every node in that DON, invoking `MethodWebAPITrigger` handling on the node side. This can be used to:
- Trigger unauthorized workflow executions on nodes (unauthorized job runs), which — combined with the workflow billing/metering system documented in `core/services/workflows/metering` — can cause unintended balance deductions/spend against a workflow owner's credits.
- Flood DON nodes with attacker-controlled trigger payloads (`payload.Timestamp` staleness check exists, but no per-sender/allowlist gating), leading to resource exhaustion / DOS, analogous to the "user fund loss" and "legitimate transactions being reverted" outcomes described in the report.

### Likelihood Explanation
High for reachability: the legacy path is exercised directly from `gateway.ProcessRequest`, the primary internet-facing ingress point, whenever a request includes a `DonID` (mirroring `isLegacyRequest` handling in `core/services/gateway/gateway.go`). The missing check is explicitly flagged by the developers themselves via the `TODO` comment, confirming it's a known gap rather than a hypothetical one.

### Recommendation
Implement the allowlist/authorization and rate-limiting check called out by the `TODO` in `HandleLegacyUserMessage` before forwarding any message to DON members — mirroring the `Authorizer`/allowlist pattern already used by `core/capabilities/vault/gw_handler.go` and the v2 HTTP trigger handler. At minimum, verify `msg.Body.Sender` against a workflow/owner allowlist and apply per-sender rate limiting prior to the `don.SendToNode` broadcast loop.

### Proof of Concept
Conceptual PoC (not executed, based on code path reading):
1. Send an HTTP POST to the Gateway's user-facing port with a legacy-format JSON-RPC message: `{"body": {"donId": "<victim-don>", "method": "web_api_trigger", "payload": {"timestamp": <now>, ...}}}`.
2. `gateway.ProcessRequest` detects `msg.Body.DonID != ""`, treats it as a legacy request, calls `msg.Validate()` (structural only), and looks up the handler for that DON via `g.handlers[handlerKey]`.
3. `handler.HandleLegacyUserMessage` is invoked; since there's no allowlist/sender check, it decodes the payload, saves the callback, and loops over `h.donConfig.Members`, sending the trigger to every node via `don.SendToNode`.
4. Nodes process `MethodWebAPITrigger` and execute the corresponding workflow, without ever verifying that the caller (`msg.Body.Sender`) was authorized to trigger it.

Note: I could not fully trace whether an additional allowlist check exists elsewhere upstream (e.g., in `ConnectionManager` or DON-side ingestion) within the indexing limits available; the explicit `TODO` in the handler code and the absence of any authorization call within `HandleLegacyUserMessage` are the concrete evidence supporting this finding. If deeper verification of upstream gating is needed, a full Devin session with repository access would be required.

### Citations

**File:** core/services/gateway/gateway.go (L221-265)
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
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L380-420)
```go
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
