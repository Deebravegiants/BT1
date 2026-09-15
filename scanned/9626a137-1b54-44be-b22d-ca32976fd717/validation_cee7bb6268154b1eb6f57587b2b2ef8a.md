### Title
Missing allowlist/rate-limiting on legacy WebAPI trigger user messages enables unauthenticated workflow-trigger flooding through the gateway - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The Hyperdrive incident stemmed from a router that dispatched calls without adequately restricting who/what could be invoked, letting an attacker repeatedly abuse the unrestricted call path. The closest reachable analog in this codebase is `handler.HandleLegacyUserMessage` in the gateway's WebAPI capabilities handler, which accepts unauthenticated, internet-facing client (`api.Message`) requests, performs only payload/timestamp checks, and then fans the request out to every DON member — while a `TODO` comment in the code itself acknowledges that the intended allowlist and rate-limiting checks were never implemented for this path.

### Finding Description
`HandleLegacyUserMessage` is the entry point invoked by `gateway.ProcessRequest` for legacy (DonID-tagged) client requests reaching the internet-facing gateway [1](#0-0) . Inside the handler, the only checks performed on an inbound client message are: payload can be unmarshalled, a non-zero `Timestamp`, message not stale, and that `msg.Body.Method == MethodWebAPITrigger` [2](#0-1) . Immediately above the method check, the code has:

```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [3](#0-2) 

After these checks pass, the handler unconditionally registers a callback and forwards the request to *every* member of the DON:

```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()

// Send original request to all nodes
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [4](#0-3) 

Note that `h.nodeRateLimiter`, the only rate limiter defined on the handler, is applied exclusively in `handleWebAPIOutgoingMessage` for *node-to-gateway* traffic [5](#0-4) , not for client-to-gateway trigger requests. There is no per-sender/per-workflow allowlist check comparable to the vault handler's `Authorizer.AuthorizeRequest` gate [6](#0-5)  or to the v2 HTTP trigger handler's JWT/authorized-keys checks (per the README: "Authentication: Verifies JWT token... Rate Limiting: Enforces per-workflow-owner rate limits") [7](#0-6) .

This means any unprivileged, unauthenticated internet client that can reach the gateway's legacy JSON path can repeatedly submit `web_api_trigger` messages, each of which is broadcast to all DON members and registers a pending callback entry (bounded only by a periodic `pruneCallbacks` sweep on age/count) [8](#0-7) , with no allowlist gating who is permitted to trigger which workflow.

### Impact Explanation
An unauthenticated actor can repeatedly invoke the trigger-dispatch path with no allowlist/quota enforcement, driving unbounded fan-out traffic to every DON node and unbounded (until size/age limits are hit) growth of the `savedCallbacks` map. This is directly analogous to the Hyperdrive bug class of "repeatedly abusing" an under-restricted dispatch path: an unprivileged caller repeatedly invokes a router/handler that lacks the intended access-control layer, causing resource exhaustion and enabling workflow triggering by parties who were never meant to be authorized to do so on this DON.

### Likelihood Explanation
High for any deployment still exposing the legacy (`DonID`-tagged) JSON-RPC path — the code path is reachable directly from `gateway.ProcessRequest` for any external caller supplying a `DonID` message, requires no credentials beyond a well-formed `api.Message`, and the missing-control gap is explicitly flagged as unfinished work (`TODO: apply allowlist and rate-limiting here`) rather than a subtle logic bug, meaning it is trivially exploitable/reachable if this legacy handler is enabled in production.

### Recommendation
Implement the intended allowlist check (validating `msg.Body.Sender`/workflow owner against a configured allowlist, analogous to `AllowListBasedAuth` used in the vault gateway handler) and per-sender/global rate limiting on `HandleLegacyUserMessage` before registering the callback and fanning out to DON members. If the legacy path is deprecated in favor of the v2 JWT-based trigger handler, ensure it is fully disabled/unreachable in production gateway configs rather than left reachable with the TODO unresolved.

### Proof of Concept
1. An unauthenticated party crafts an `api.Message` with `Body.Method = "web_api_trigger"`, a valid `Body.MessageID`, a `webapicap.TriggerRequestPayload` with a non-zero, non-stale `Timestamp`, and a `Body.DonID` matching a target DON.
2. Send this message repeatedly to the gateway's legacy endpoint. Because `HandleLegacyUserMessage` performs no allowlist or rate-limit check before broadcasting [9](#0-8) , each request is accepted, a `savedCallbacks` entry is created, and the request is forwarded to every DON member.
3. Repeating step 2 at volume causes unbounded broadcast traffic to DON nodes and growth of the callback map, with no allowlist ever rejecting the sender — demonstrating the missing access-control layer acknowledged by the `TODO` comment in the code.

Note: I could not fully trace whether this legacy handler path is still wired into current production gateway deployments versus being superseded entirely by the v2 handler (`core/services/gateway/handlers/capabilities/v2/http_handler.go`), which does implement JWT auth and per-workflow-owner rate limiting. This affects the real-world severity/likelihood and would need confirmation in a live session with access to deployment/config wiring.

### Citations

**File:** core/services/gateway/gateway.go (L253-265)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-339)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}

	// If there are still too many callbacks, sort them by creation time and remove the oldest ones.
	maxSize := h.config.MaxSavedCallbacks
	var evicted int
	if len(h.savedCallbacks) > maxSize {
		type entry struct {
			id        string
			createdAt time.Time
		}
		entries := make([]entry, 0, len(h.savedCallbacks))
		for id, cb := range h.savedCallbacks {
			entries = append(entries, entry{id, cb.createdAt})
		}
		sort.Slice(entries, func(i, j int) bool {
			return entries[i].createdAt.Before(entries[j].createdAt)
		})
		// Trim to maxSize/2 to avoid sorting the list too frequently.
		for _, e := range entries[:len(entries)-maxSize/2] {
			delete(h.savedCallbacks, e.id)
			evicted++
		}
	}

	if expired > 0 || evicted > 0 {
		h.lggr.Infow("Pruned savedCallbacks", "expired", expired, "evicted", evicted, "remaining", len(h.savedCallbacks))
	}
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-420)
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

**File:** core/capabilities/vault/gw_handler.go (L187-211)
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
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L75-86)
```markdown
## 4. HTTP Trigger Message Handling

### 4.1 Process Flow

1. **Request Validation**: Validates JSON-RPC format, method, and parameters
2. **Workflow Resolution**: Resolves workflow ID from selector (ID, owner, name, tag)
3. **Authentication**: Verifies JWT token (ECDSA signature) and checks authorized keys
4. **Rate Limiting**: Enforces per-workflow-owner rate limits
5. **Node Distribution**: Sends request to all DON members with retry logic
6. **Response Aggregation**: Collects and aggregates responses from nodes (2f + 1 identical responses required, where f is max faulty nodes)
7. **User Response**: Returns aggregated result to the original requester

```
