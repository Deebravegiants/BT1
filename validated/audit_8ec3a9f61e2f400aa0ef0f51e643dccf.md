Audit Report

## Title
Missing allowlist and rate-limiting enforcement on legacy WebAPI trigger user messages allows any client to broadcast unauthenticated requests to an entire DON - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`HandleLegacyUserMessage` in the legacy WebAPI capabilities handler only validates message structure (payload decoding, non-zero timestamp, staleness) and the `Method` field before saving a callback and broadcasting the request to every node in the DON. The code contains an explicit `// TODO: apply allowlist and rate-limiting here` immediately before the method check and dispatch loop, confirming no caller-identity, DON-membership, or workflow-ownership authorization is performed for this path. [1](#0-0) [2](#0-1) 

## Finding Description
`HandleLegacyUserMessage` decodes `TriggerRequestPayload`, checks `Timestamp != 0` and non-staleness, then hits the TODO marker before validating only `msg.Body.Method == MethodWebAPITrigger`. [3](#0-2)  It then registers the request in `h.savedCallbacks` and fans it out via `don.SendToNode` to every member of `h.donConfig.Members`, with no identity, allowlist, workflow-ownership, or rate-limit check anywhere in the function. [4](#0-3) 

Comparing this to the newer v2 HTTP trigger handler in the same codebase confirms this is a real gap rather than an intentional design: `httpTriggerHandler.HandleUserTriggerRequest` explicitly resolves the workflow, calls `h.authorizeRequest` (which calls `workflowMetadataHandler.Authorize` with request auth) and `h.checkRateLimit` (backed by `limits.RateLimiter`/`userRateLimiter.AllowErr`) before ever contacting the DON. [5](#0-4) [6](#0-5)  No equivalent exists in the legacy handler's `HandleLegacyUserMessage`.

The dispatch path from the gateway's `multiHandler` shows `HandleLegacyUserMessage` is called directly based on the request method with no additional authorization layer in between: `multiHandler.HandleLegacyUserMessage` simply looks up the handler by method and forwards the call. [7](#0-6)  The `Handler` interface documents that each user request is handled by `HandleLegacyUserMessage`/`HandleJSONRPCUserMessage` directly, with `HandleNodeMessage` reserved for node-originated traffic — there is no separate mandatory allowlist middleware documented or found upstream of these calls. [8](#0-7)  I was unable to locate the HTTP server ingress code (`core/services/gateway/network/httpserver.go` did not match relevant patterns during search, and further request-signature-verification logic for legacy user messages could not be confirmed within available tool budget) — this is a gap in my verification, though the TODO comment and downstream code strongly indicate that no allowlist/rate-limit check occurs in this handler regardless of what happens at ingress.

## Impact Explanation
If reachable by an unauthenticated or unallowlisted caller, this allows DON-wide broadcast amplification: a single request causes `don.SendToNode` calls to every DON member, and `h.savedCallbacks` grows unbounded until pruning (bounded by `MaxSavedCallbacks`/`CallbackPruneIntervalSec`), enabling resource-consumption/DoS-style abuse and bypass of the allowlist/rate-limit gating that is enforced in the equivalent newer v2 path. This maps to the in-scope "gateway request impersonation / allowlist or rate-limit bypass" impact category. Severity depends heavily on whether the legacy WebAPI trigger path is still reachable in production deployments or is a deprecated/soon-to-be-removed code path guarded by other means (e.g., only enabled when explicitly configured, or protected by an external ingress allowlist/mTLS not visible in this file) — this could not be fully confirmed.

## Likelihood Explanation
Within the function itself, the missing check is unconditional — reachable by any caller who can construct a well-formed, non-stale `TriggerRequestPayload` with `Method: "web_api_trigger"`. However, likelihood of real-world exploitability depends on factors outside this file that were not fully verifiable here: whether the gateway's ingress (HTTP/websocket layer, TLS client cert requirements, or an external API key check) already restricts who can reach `HandleLegacyUserMessage` before this code executes, and whether this legacy path is still actively used versus deprecated in favor of the v2 handler which does enforce authorization/rate-limiting.

## Recommendation
Implement the allowlist and rate-limiting checks referenced by the TODO in `HandleLegacyUserMessage` before saving the callback and broadcasting to DON members, mirroring the `authorizeRequest`/`checkRateLimit` pattern used in `httpTriggerHandler.HandleUserTriggerRequest`. At minimum, verify caller/workflow ownership against `donConfig` and apply a `ratelimit.RateLimiter`-backed check per caller before the `don.SendToNode` fan-out loop.

## Proof of Concept
1. Construct a JSON-RPC/legacy message with `Body.Method = "web_api_trigger"`, a valid non-stale `Timestamp` in `TriggerRequestPayload`, and submit it through whatever ingress calls `multiHandler.HandleLegacyUserMessage` → `handler.HandleLegacyUserMessage`.
2. Observe that execution proceeds past payload/staleness checks directly to the `Method` check and then to `don.SendToNode` for every `h.donConfig.Members` entry, with no call to any allowlist or rate-limiter function in `core/services/gateway/handlers/capabilities/handler.go`.
3. A Go unit test analogous to `core/services/gateway/handlers/capabilities/handler_test.go`'s existing tests for `HandleLegacyUserMessage` could assert that repeated calls with different unauthenticated caller identities are all accepted and broadcast without any distinguishing authorization check, contrasting with `http_trigger_handler_test.go`'s coverage of JWT/allowlist/rate-limit enforcement for the v2 path.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-396)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-417)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}

// resolveOrgID resolves the organization ID for owner, or returns "" if it can't be resolved
func (h *httpTriggerHandler) resolveOrgID(ctx context.Context, owner string) string {
	if h.orgResolver == nil {
		h.lggr.Warnw("OrgResolver is nil, continuing without an orgID", "workflowOwner", owner)
		return ""
	}
	orgID, err := h.orgResolver.Get(ctx, owner)
	if err != nil {
		h.lggr.Warnw("Failed to resolve organization ID, continuing without it", "workflowOwner", owner, "err", err)
		return ""
	}
	return orgID
}

func (h *httpTriggerHandler) checkRateLimit(ctx context.Context, workflowID, requestID string, callback handlers.Callback) error {
	workflowRef, found := h.workflowMetadataHandler.GetWorkflowReference(workflowID)
	if !found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflow reference not found", callback)
		return errors.New("workflow reference not found")
	}

	orgID := h.resolveOrgID(ctx, workflowRef.workflowOwner)
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: workflowRef.workflowOwner, Org: orgID, Workflow: workflowID})
	if err := h.userRateLimiter.AllowErr(ctx); err != nil {
		lggr := logger.With(h.lggr, platform.KeyWorkflowID, workflowID, platform.KeyWorkflowOwner, workflowRef.workflowOwner, "requestID", requestID, "err", err)
		if errLimited, ok := errors.AsType[limits.ErrorRateLimited](err); ok {
			switch errLimited.Scope {
			case settings.ScopeWorkflow:
				lggr.Errorf("failed to start execution: per workflow rate limit exceeded")
				h.metrics.IncrementWorkflowThrottled(ctx, h.lggr)
			default:
				lggr.Errorf("failed to start execution: unexpected rate limit for scope %s", errLimited.Scope)
			}
			h.handleUserError(ctx, requestID, jsonrpc.ErrLimitExceeded, "rate limit exceeded", callback)
			return err
		}
		return fmt.Errorf("failed to check rate limit: %w", err)
	}
	return nil
}
```

**File:** core/services/gateway/multihandler.go (L53-60)
```go
func (m *multiHandler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback handlers.Callback) error {
	h, err := m.getHandler(msg.Body.Method)
	if err != nil {
		return fmt.Errorf("failed to get handler for method %s: %w", msg.Body.Method, err)
	}

	return h.HandleLegacyUserMessage(ctx, msg, callback)
}
```

**File:** core/services/gateway/handlers/handler.go (L31-52)
```go
type Handler interface {
	job.ServiceCtx

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error

	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleJSONRPCUserMessage(ctx context.Context, jsonRequest jsonrpc.Request[json.RawMessage], callback Callback) error

	// Handlers should not make any assumptions about goroutines calling HandleNodeMessage.
	// should be non-blocking
	// should validate the message inside the response
	HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error

	// The methods support by this Handler.
	// Should be globally unique across all handlers.
	Methods() []string
}
```
