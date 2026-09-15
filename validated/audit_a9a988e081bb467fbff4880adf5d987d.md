Audit Report

## Title
Missing allowlist/authorization enforcement on `web_api_trigger` messages allows any unprivileged gateway caller to broadcast requests to an entire DON - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`handler.HandleLegacyUserMessage` processes inbound legacy `web_api_trigger` gateway messages and, after only format/timestamp checks, broadcasts the caller's request to every member of the target DON via `don.SendToNode`, skipping the allowlist/rate-limiting check explicitly marked with a `// TODO` comment [1](#0-0) . The only "authentication" performed on the message is `msg.Validate()`/`ExtractSigner()`, which merely recovers whatever address signed the payload and does not check that address against any allowlist, so an attacker can self-generate an ECDSA keypair, sign an arbitrary message, and pass validation [2](#0-1) .

## Finding Description
The gateway's `ProcessRequest` routes any legacy request (one that includes a `DonID`) to the DON's registered handler's `HandleLegacyUserMessage` after only calling `msg.Validate()`, which is a structural/signature-format check, not an authorization/allowlist check [3](#0-2) . Inside `HandleLegacyUserMessage`, after payload decoding and staleness checks, the code proceeds directly past `// TODO: apply allowlist and rate-limiting here` to convert the message into a JSON-RPC request and fan it out to every DON member with no check on whether the signer/sender is authorized for this DON or workflow [4](#0-3) . This is confirmed as an actual gap, not a misreading — the comment is present verbatim in the shipped code, and no allowlist function call exists anywhere in the function body between message validation and the `don.SendToNode` loop.

This contrasts with the vault handler (`core/services/gateway/handlers/vault/handler.go`), which routes `HandleJSONRPCUserMessage` requests through `h.requestProcessor.ProcessRequest`, which enforces `authorizer.AuthorizeRequest` via an allowlist/JWT-based `Authorizer` before dispatching to nodes [5](#0-4) , and with the v2 HTTP trigger handler, which enforces `authorizeRequest`/`checkRateLimit` scoped to a specific workflow owner before processing [6](#0-5) . The legacy `capabilities/handler.go` path for `web_api_trigger` has no equivalent gate.

## Impact Explanation
This maps to the in-scope "allowlist/quota bypass" and "unauthorized job run" impact categories. Any external caller who can reach the gateway's legacy JSON-RPC ingress with a `DonID` set can, without any pre-registered identity or credential beyond a self-generated signing key, cause the gateway to broadcast a `web_api_trigger` JSON-RPC request to every node in a targeted DON's `donConfig.Members`, bypassing the intended per-user/per-workflow authorization boundary that exists for the vault and v2 HTTP trigger paths. Whether this results in actual unauthorized workflow execution depends on how each node's `MethodWebAPITrigger` capability handler interprets and further authorizes the trigger payload on the node side, but the gateway-side allowlist gap itself is concrete and directly exploitable as an unauthorized broadcast to DON members.

## Likelihood Explanation
The gap requires no privileged role: an attacker only needs to construct a syntactically valid `api.Message` with `Method = "web_api_trigger"`, sign it with any ECDSA key (self-generated, since `Validate()`/`ExtractSigner()` only recovers a signer address without checking it against any allowlist), include a non-stale `Timestamp`, and submit it through the gateway's legacy ingress (`ProcessRequest` routes any request carrying `DonID` to `HandleLegacyUserMessage`). No rate limiting or allowlist check blocks this before the broadcast, and the flaw is explicitly marked by the maintainers' own TODO comment in production code, making it directly and repeatably exploitable rather than speculative.

## Recommendation
- Implement the allowlist and rate-limiting check called out in the TODO in `HandleLegacyUserMessage` before broadcasting `web_api_trigger` messages to DON members, mirroring the workflow-owner/authorizer validation already present in `vault/handler.go`'s `ProcessRequest` and the v2 `httpTriggerHandler`'s `authorizeRequest`/`checkRateLimit`.
- Validate that the message's recovered signer (`msg.Body.Sender`) is a registered/authorized entity for the target DON/workflow before calling `don.SendToNode`.
- If the legacy handler is deprecated in favor of the v2 handler, confirm it is disabled/unreachable in production DON configurations, or remove it.

## Proof of Concept
1. Generate an arbitrary ECDSA keypair (no pre-registration required).
2. Construct an `api.Message` with `Body.Method = "web_api_trigger"`, a valid `Body.DonID` for a target DON, a `TriggerRequestPayload` with a non-zero, fresh `Timestamp`, and sign it with the generated key via `Message.Sign` — this passes `Message.Validate()` since it only checks structural constraints and signature recoverability, not sender identity against any allowlist.
3. Submit the message as a legacy JSON-RPC request (with `DonID` set) to the gateway's `ProcessRequest` endpoint.
4. Observe that `HandleLegacyUserMessage` proceeds past the `// TODO: apply allowlist and rate-limiting here` line with no authorization call, and loops over `h.donConfig.Members` calling `don.SendToNode` for each member — confirmable via a Go unit test analogous to existing tests in `handler_test.go` (e.g. `TestHandlerReceiveHTTPMessageFromClient`) but asserting that a message signed by an out-of-allowlist/unregistered key is still broadcast to all DON members. [7](#0-6)

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

**File:** core/services/gateway/api/message.go (L54-88)
```go
func (m *Message) Validate() error {
	if m == nil {
		return errors.New("nil message")
	}
	if len(m.Signature) != MessageSignatureHexEncodedLen {
		return errors.New("invalid hex-encoded signature length")
	}
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
	if len(m.Body.Method) == 0 || len(m.Body.Method) > MessageMethodMaxLen {
		return errors.New("invalid method name length")
	}
	if strings.HasSuffix(m.Body.Method, NullChar) {
		return errors.New("method name ending with null bytes")
	}
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
}
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
