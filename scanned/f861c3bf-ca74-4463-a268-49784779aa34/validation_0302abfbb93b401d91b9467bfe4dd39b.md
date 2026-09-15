### Title
Unauthenticated fan-out amplification via `HandleLegacyUserMessage` with no user-level rate limiting — ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The GitLab CVE describes a DoS where an unprivileged user causes unbounded server-side work by repeatedly submitting content (issue comments) with no throttling. The closest reachable analog in this codebase is the Gateway's legacy user-facing entrypoint `HandleLegacyUserMessage`, which is reachable directly from an unauthenticated HTTP client via `gateway.ProcessRequest` → `httpServer.handleRequest`, and which explicitly has **no rate limiting or allowlist enforcement** on the user-request path, despite fanning each request out to every node in the DON and creating server-side state per request.

### Finding Description
`ProcessRequest` in [1](#0-0)  is invoked directly by the internet-facing HTTP server for every incoming user request (see `handleRequest` in [2](#0-1) , which is bound to an unauthenticated `net/http` listener). For legacy DON-ID-addressed requests, it calls `h.HandleLegacyUserMessage(ctx, msg, callback)` [3](#0-2) .

Inside `HandleLegacyUserMessage`, the code explicitly marks the missing protection:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [4](#0-3) 

Past that check, every valid request:
1. Is recorded in `h.savedCallbacks[msg.Body.MessageID]` under a mutex [5](#0-4) .
2. Triggers a fan-out `SendToNode` call to **every member of the DON** [6](#0-5) .

There is no per-sender or per-IP rate limiter applied on this user-facing path (unlike `handleWebAPIOutgoingMessage`, which does check `h.nodeRateLimiter.Allow(nodeAddr)` for node-originated traffic, see [7](#0-6) ). The only mitigations are:
- A global `MaxSavedCallbacks` (default 20000) with pruning every `CallbackPruneIntervalSec` (default 30s) [8](#0-7) [9](#0-8) .
- A global HTTP body size cap (`MaxRequestBytesLimiter`) [10](#0-9) .
- A per-request `RequestTimeoutMillis` wrapper.

None of these are per-sender or per-IP throttles; an unprivileged client can send many small, distinct-`MessageID` requests in a tight loop, and each one is fully processed (JSON decoded, validated, stored, and dispatched to all N DON nodes) before any global cap kicks in. This differs from the newer JSON-RPC/V2 and vault/HTTP-trigger-v2 handlers, which document explicit per-sender + global rate limiting [11](#0-10) .

### Impact Explanation
An unprivileged, unauthenticated client hitting the Gateway's user HTTP port can cause N-fold outbound message amplification per request to DON connection managers/nodes, and grow `savedCallbacks` up to the eviction threshold, consuming gateway CPU/memory and DON node bandwidth — a resource-exhaustion/availability impact analogous to the GitLab issue-comment DoS (CVSS AV:N/AC:L/PR:L/UI:N/A:H). This does not disclose secrets or bypass authorization for privileged actions, but it does affect availability of the gateway/DON communication path.

### Likelihood Explanation
Likelihood is moderate-to-high in a deployment where the legacy DON-ID-based routing path (`isLegacyRequest = true`) is still enabled and reachable without authentication — the code path is exercised whenever `msg.Body.DonID` is set, requiring only a validly-signed message (`msg.Validate()`), not privileged access, and the TODO comment confirms the gap is a known, un-remediated omission rather than a hardened design decision.

### Recommendation
Add per-sender (and/or per-IP) rate limiting and an allowlist check in `HandleLegacyUserMessage`, consistent with the `TODO` already present, mirroring the `nodeRateLimiter.Allow(...)` pattern used in `handleWebAPIOutgoingMessage` and the dual (global + per-sender) rate limiter pattern documented for the V2/vault handlers.

### Proof of Concept
Not independently executed; based on static code review, a PoC would consist of repeatedly POSTing distinct, validly-signed legacy JSON-RPC messages (unique `MessageID`, `Method = "web_api_trigger"`, valid `DonID`) to the Gateway's user HTTP endpoint faster than the 30-second prune interval, observing unthrottled growth of `savedCallbacks` and proportional fan-out traffic to all DON node connections, with no rejection until the global `MaxSavedCallbacks`/body-size ceiling is hit.

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

**File:** core/services/gateway/network/httpserver.go (L195-245)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}

	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		msg := "Failed to get request size limit"
		s.lggr.Errorw(msg, "err", err)
		http.Error(w, msg, http.StatusInternalServerError)
		return
	}
	source := http.MaxBytesReader(nil, r.Body, int64(maxRequestBytes))
	rawMessage, err := io.ReadAll(source)
	if err != nil {
		s.lggr.Error("error reading request", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
	duration := time.Since(startTime)
	s.hMetrics.RecordRequestDuration(r.Context(), httpStatusCode, duration)
	s.hMetrics.RecordRequestCount(r.Context(), httpStatusCode)

	w.Header().Set("Content-Type", s.config.ContentTypeHeader)
	w.WriteHeader(httpStatusCode)
	_, err = w.Write(rawResponse) //nolint:gosec // G705: response body is written with an explicit Content-Type, not rendered as HTML
	if err != nil {
		s.lggr.Error("error when writing response", err)
	}
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L416-419)
```go
	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L211-223)
```markdown
### 7.2 Rate Limiting

- **Dual Rate Limiting**: Separate limits for node and user requests
- **Per-Sender Limits**: Individual rate limits per sending entity
- **Global Limits**: System-wide rate limiting for overall protection

### 7.3 Input Validation

- **Request ID Validation**: Prevents malicious request ID injection
- **JSON Validation**: Ensures valid JSON input for workflow parameters
- **Workflow Field Validation**: Validates workflow selector format
- **Public Key Validation**: Ensures proper ECDSA key format

```
