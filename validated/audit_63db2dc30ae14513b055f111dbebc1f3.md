Audit Report

## Title
Missing allowlist and rate-limiting enforcement in `HandleLegacyUserMessage` allows unauthenticated fan-out of `web_api_trigger` requests to every DON node - ([File: core/services/gateway/handlers/capabilities/handler.go])

## Summary
`handler.HandleLegacyUserMessage`, invoked for every legacy (DON-ID-keyed) JSON-RPC request via `gateway.ProcessRequest`, contains an explicit `// TODO: apply allowlist and rate-limiting here` comment at L384 immediately before the code path that forwards the client-supplied request unconditionally to every member of the target DON. No allowlist check or per-caller/per-workflow rate limiter is actually applied on this ingress path, only a method-name check (`msg.Body.Method != MethodWebAPITrigger`) and generic payload/staleness validation.

## Finding Description
`gateway.ProcessRequest` (`core/services/gateway/gateway.go` L221-295) decodes the JSON-RPC request, and for legacy requests (identified by a non-empty `msg.Body.DonID`) calls `msg.Validate()` and then dispatches directly to `h.HandleLegacyUserMessage(ctx, msg, callback)` at L270-272. `msg.Validate()` performs structural validation, not caller authorization or rate limiting.

Inside `HandleLegacyUserMessage` (`core/services/gateway/handlers/capabilities/handler.go` L341-421), the checks performed before broadcast are: JSON payload unmarshal success, non-zero timestamp, and message staleness (L345-383). Immediately after these, at L384, the comment `// TODO: apply allowlist and rate-limiting here` appears, followed only by a check that the method equals `MethodWebAPITrigger` (L385-396) — no allowlist lookup and no rate limiter call exist anywhere in this function. The request is then unconditionally sent to `don.SendToNode` for every `member := range h.donConfig.Members` (L416-419).

The only rate limiter in the file, `h.nodeRateLimiter`, is applied in `handleWebAPIOutgoingMessage` (L164-168), which governs node→gateway traffic (`HandleNodeMessage`), not the user-ingress path. This confirms there is no equivalent protection on `HandleLegacyUserMessage`.

By contrast, the newer `capabilities/v2` handler design (per its README) explicitly implements "Authentication," "Rate Limiting," and per-workflow-owner enforcement, and the `vault` gateway handler (`core/capabilities/vault/gw_handler.go`) uses an `Authorizer`/allowlist pattern — showing that this class of protection is a recognized architectural requirement that is simply absent from the legacy capabilities handler's trigger path.

## Impact Explanation
Any client able to reach the gateway's user-facing HTTP port with a well-formed, non-stale, structurally valid legacy JSON-RPC request (`Method: web_api_trigger`, a known/valid `DonID`) causes the gateway to broadcast that request to every node of the targeted DON, with no allowlist restricting who may submit such requests and no rate limiter throttling repeated submissions. This enables resource-exhaustion / amplification abuse (a single small request fans out to N DON nodes) and unauthorized triggering of `web_api_trigger`-driven workflow executions by any caller who can reach the endpoint, which maps to the in-scope "unauthorized job run" / gateway request abuse impact category.

## Likelihood Explanation
High for any caller capable of reaching the gateway's user HTTP endpoint: the only gates are generic message well-formedness and staleness, both trivially satisfiable, and the code path is exercised on every legacy `web_api_trigger` request through `gateway.ProcessRequest` → `HandleLegacyUserMessage`. Whether this rises to "unauthenticated" in practice depends on whether the surrounding deployment/network layer (e.g., an API gateway, mTLS, or reverse proxy in front of the user HTTP port) enforces caller identity before reaching this code — that is outside this file's scope but is not evidenced anywhere in the reviewed handler code, `ProcessRequest`, or `msg.Validate()`.

## Recommendation
Implement the allowlist and rate-limiting logic the TODO comment calls for in `HandleLegacyUserMessage` before the `don.SendToNode` fan-out loop (`core/services/gateway/handlers/capabilities/handler.go` L416-419) — e.g., reuse the `ratelimit.RateLimiter` pattern already used for `nodeRateLimiter` keyed by caller/workflow, and an `Authorizer`/allowlist check analogous to `core/capabilities/vault/gw_handler.go` L108-111 — so unprivileged/unauthorized callers cannot trigger unrestricted broadcast to DON members.

## Proof of Concept
1. Send a well-formed legacy JSON-RPC request to the gateway's user HTTP port with `Body.DonID` set to a valid configured DON ID, `Body.Method = "web_api_trigger"`, and a valid recent `Timestamp` in the trigger payload — no additional credential is validated by `HandleLegacyUserMessage` beyond these fields.
2. Trace execution: `gateway.ProcessRequest` (`core/services/gateway/gateway.go` L270-272) → `handler.HandleLegacyUserMessage` (`core/services/gateway/handlers/capabilities/handler.go` L341) passes the payload/staleness/method checks (L345-396) without any allowlist or rate-limit check.
3. Observe the loop at L416-419 calls `don.SendToNode` once per `h.donConfig.Members` entry for this single request.
4. Repeat the request rapidly from one caller to confirm no throttling occurs on this path (contrast with `handleWebAPIOutgoingMessage`'s `h.nodeRateLimiter.Allow(nodeAddr)` check at L166, which has no analog here) — this can be validated with a Go unit test instantiating `handler` with a mock `handlers.DON` and asserting `SendToNode` is called for every member on repeated calls with no rejection. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

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

**File:** core/capabilities/vault/gw_handler.go (L108-111)
```go
	if authorizer == nil {
		allowListBasedAuth := NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
		authorizer = NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)
	}
```
