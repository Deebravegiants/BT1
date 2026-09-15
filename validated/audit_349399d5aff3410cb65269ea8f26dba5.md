### Title
Missing sender allowlist/rate-limit enforcement on legacy `web_api_trigger` gateway messages allows any client to trigger unauthorized DON job runs - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Chainlink Gateway's legacy web API trigger path, `handler.HandleLegacyUserMessage`, accepts and forwards `web_api_trigger` messages from any unprivileged client that can reach the gateway's HTTP endpoint, without performing the sender allowlist or rate-limiting checks that are explicitly called out as required but not implemented.

### Finding Description
The Gateway is an internet-facing component. Incoming HTTP requests are decoded and routed by `gateway.ProcessRequest` in `core/services/gateway/gateway.go` (lines 220-295). For legacy requests carrying a `DonID`, the code path is: [1](#0-0) 

which calls `msg.Validate()` (structural/shape validation, not sender authorization) and then dispatches to `h.HandleLegacyUserMessage(ctx, msg, callback)`.

Inside `handler.HandleLegacyUserMessage` (in `core/services/gateway/handlers/capabilities/handler.go`), the function decodes the payload, checks the timestamp for staleness, and then explicitly flags that access-control is missing: [2](#0-1) 

The comment `// TODO: apply allowlist and rate-limiting here` sits directly above the method check, and no call to any allowlist/authorization component exists anywhere in this function or in the rest of `handler.go` for the `MethodWebAPITrigger` path — a `grep` for `allowlist`/`Allowlist` in the whole `core/services/gateway/handlers/capabilities` package only matches this same TODO comment, confirming no enforcement exists.

After the (missing) authorization step, the handler builds a `savedCallback` and forwards the request to *every* DON member node as a legitimate trigger: [3](#0-2) 

This mirrors the reported bug class: a function meant to be restricted to an authorized caller (in the original report, `JUSDBank`; here, an allowlisted external sender/DON member) has no `access-control` check at all — any unprivileged client that can reach the gateway's public endpoint can invoke it directly.

By contrast, the modern JSON-RPC vault and gateway-capabilities-v2 paths in the same codebase (`core/services/gateway/handlers/vault/handler.go`, `core/capabilities/vault/gw_handler_test.go`) *do* call an `Authorizer.AuthorizeRequest`/allowlist check before processing sensitive requests, showing that the legacy trigger path is inconsistent with the intended security model and was left without the same protection.

### Impact Explanation
Because `HandleLegacyUserMessage` forwards the trigger to all DON nodes without verifying the sender is an allowlisted/authorized workflow owner, an unprivileged actor can submit crafted `web_api_trigger` messages that DON nodes will process as legitimate triggers (subject only to timestamp freshness and payload shape checks), enabling unauthorized triggering of workflow/job runs against the DON. This directly matches the "unauthorized job run" acceptance criterion — an attacker who can reach the gateway's public interface can impersonate a trigger request without ever needing to be on the sender allowlist.

### Likelihood Explanation
The gateway HTTP endpoint is designed to be internet-facing and reachable by external, unauthenticated clients (that's its purpose — external initiators/webhooks call it). The vulnerable code path is reached whenever a legacy request (one that still carries a `DonID`) is routed to this handler; no additional privilege is required beyond crafting a validly-shaped `api.Message` with a fresh timestamp and `MethodWebAPITrigger`. This makes exploitation straightforward for any actor capable of sending HTTP requests to the gateway.

### Recommendation
Implement the missing allowlist and rate-limiting check in `HandleLegacyUserMessage` before processing `MethodWebAPITrigger` (or any method), analogous to the `Authorizer.AuthorizeRequest`/allowlist pattern already used in the vault and v2 capability gateway handlers. Reject/return an authorization error for any request whose sender is not present in the DON's/method's allowlist, and apply the same per-sender rate limiting used elsewhere (e.g. `nodeRateLimiter`) to this inbound trigger path.

### Proof of Concept
1. An attacker crafts an `api.Message` with `Body.Method = "web_api_trigger"`, a valid `DonID` matching a configured DON, a `TriggerRequestPayload` containing `Timestamp` set to `time.Now().Unix()`, and any workflow-trigger-shaped payload.
2. The attacker POSTs this message (wrapped as required by `jsonrpc2.DecodeRequest`) to the gateway's public HTTP endpoint.
3. `gateway.ProcessRequest` decodes it, sees `msg.Body.DonID != ""`, calls `msg.Validate()` (structural only) and routes to `handler.HandleLegacyUserMessage`.
4. `HandleLegacyUserMessage` checks payload decoding, timestamp freshness, and method name — all satisfied by the crafted message — then calls `don.SendToNode` for every DON member, without ever verifying whether the sender is allowlisted to trigger workflows on that DON.
5. DON nodes receive and process the trigger message as if it came from an authorized source, resulting in an unauthorized workflow/job trigger.

### Citations

**File:** core/services/gateway/gateway.go (L253-276)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-397)
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
