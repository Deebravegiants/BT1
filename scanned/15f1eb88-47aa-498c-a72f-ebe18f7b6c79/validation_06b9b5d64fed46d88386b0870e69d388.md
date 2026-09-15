Confirmed: `ProcessRequest` in `gateway.go` is the internet-facing entry point that any unauthenticated user can hit over HTTP, and for legacy requests (`isLegacyRequest == true`) it dispatches directly to `HandleLegacyUserMessage` on the target handler without requiring any allowlist membership, prior registration, or cost check on the caller — matching the report's bug class of an unprivileged actor being able to freely spam state-inflating requests.

### Title
Unauthenticated Gateway callers can freely spam `savedCallbacks`/DON fan-out via legacy `web_api_trigger` requests with no allowlist or rate limiting - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The `BountyCore.receiveFunds` bug allows an unprivileged caller to append zero-cost entries to an array that all users must later iterate, inflating gas costs. The reachable analog is `handler.HandleLegacyUserMessage` in the Chainlink Gateway's capabilities handler, reached from any external HTTP caller via `gateway.ProcessRequest` [1](#0-0) , which stores a `savedCallback` entry and fans the message out to every DON member for each request, with the code explicitly noting the missing check: `// TODO: apply allowlist and rate-limiting here` [2](#0-1) .

### Finding Description
`gateway.ProcessRequest` is the public HTTP entry point for the Gateway (`GetUserPort`) [3](#0-2) . For "legacy" JSON-RPC messages (those carrying a `DonID`), it only validates message shape via `msg.Validate()` and dispatches straight into the handler's `HandleLegacyUserMessage` — there is no authentication, allowlist check, or per-caller quota applied at this layer [4](#0-3) .

Inside `handler.HandleLegacyUserMessage`, the only gating is a timestamp freshness check; the comment immediately preceding the method dispatch explicitly documents that allowlisting and rate-limiting are *not yet implemented* for this legacy path: `// TODO: apply allowlist and rate-limiting here` [5](#0-4) . Every accepted request unconditionally inserts an entry into the shared `savedCallbacks` map and fans the request out to every member node of the DON: [6](#0-5) .

This mirrors the audit finding's root cause precisely: an unprivileged caller can perform a cheap/free action (an HTTP POST with an arbitrary but well-formed timestamp) that unconditionally grows internal server-side state (`savedCallbacks`) and triggers real downstream work (message fan-out to every DON node), without any check tying the action to caller identity, cost, or a rate/allow list.

Note that `pruneCallbacks` does cap the map at `MaxSavedCallbacks` (default 20000) and evicts oldest entries [7](#0-6) , which bounds memory growth, but it does not prevent the attacker from causing continuous DON-wide fan-out traffic and continuous churn/eviction of legitimate in-flight callbacks (a distinct, still-impactful DoS vector), since there is no per-caller admission control before the message reaches `HandleLegacyUserMessage`.

### Impact Explanation
An unauthenticated network client can flood the Gateway's legacy `web_api_trigger` endpoint. Each request causes: (1) an entry inserted into `savedCallbacks`, and (2) a message sent to every node in the DON via `don.SendToNode` for every member [8](#0-7) . At scale this amplifies a single unauthenticated HTTP request into N (DON size) internal messages, and continuously evicts legitimate pending callbacks once `MaxSavedCallbacks` is exceeded, causing legitimate users' triggered workflow responses to be lost/timed out — a availability/DoS impact analogous to the original bug's "large gas costs due to overloaded deposits array," here manifesting as DON-wide resource exhaustion and dropped legitimate callbacks.

### Likelihood Explanation
High from a reachability standpoint: the Gateway user-facing HTTP port is explicitly internet-facing (`GetUserPort`) and the legacy code path is reached without any authentication token, allowlist entry, or per-IP/per-caller rate limit before reaching the vulnerable logic — the only gates are JSON schema validation and a timestamp freshness check [9](#0-8) . The explicit `// TODO: apply allowlist and rate-limiting here` comment in production code confirms this is a known, unaddressed gap rather than a speculative concern.

### Recommendation
Add allowlist/authentication and per-caller rate limiting to the legacy `HandleLegacyUserMessage` path before inserting into `savedCallbacks` or fanning out to DON members, matching the protections already applied to node-originated traffic (`nodeRateLimiter`) and to newer JSON-RPC handlers (e.g., Vault's allowlist-based authorizer [10](#0-9) ). At minimum, resolve the outstanding TODO by wiring in a caller-facing rate limiter and/or allowlist check prior to accepting legacy `web_api_trigger` requests.

### Proof of Concept
1. Deploy a Gateway configured with the `capabilities` handler for a DON with `N` member nodes.
2. From an unauthenticated client, repeatedly POST well-formed legacy JSON-RPC requests to the Gateway's user HTTP port with method `web_api_trigger`, a fresh `Timestamp`, and a unique `MessageID` each time, and a valid but arbitrary `DonID`.
3. Observe that `gateway.ProcessRequest` accepts every request without checking caller identity [4](#0-3) , and each accepted request causes `handler.HandleLegacyUserMessage` to insert into `savedCallbacks` and send one message per DON member (`N` internal messages per request) [6](#0-5) .
4. With sufficient request volume, `savedCallbacks` repeatedly exceeds `MaxSavedCallbacks`, causing `pruneCallbacks` to evict legitimate, still-pending callbacks from real DON workflow triggers [11](#0-10) , and the DON is bombarded with amplified fan-out traffic sourced from a single unauthenticated attacker.

### Citations

**File:** core/services/gateway/gateway.go (L220-276)
```go
// Called by the server
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

**File:** core/services/gateway/gateway.go (L315-317)
```go
func (g *gateway) GetUserPort() int {
	return g.httpServer.GetPort()
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-338)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-420)
```go
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

**File:** core/capabilities/vault/gw_handler.go (L108-111)
```go
	if authorizer == nil {
		allowListBasedAuth := NewAllowListBasedAuth(lggr, workflowRegistrySyncer)
		authorizer = NewAuthorizer(allowListBasedAuth, jwtBasedAuth, lggr)
	}
```
