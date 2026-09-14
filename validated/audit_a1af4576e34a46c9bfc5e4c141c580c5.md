Confirmed: there is no per-client/IP rate limiting or authentication gate applied before `HandleJSONRPCUserMessage` is invoked for the Vault handler's `MethodPublicKeyGet` path — `gateway.ProcessRequest` only validates JSON-RPC shape and request-ID length before dispatching directly to the handler.

### Title
Unauthenticated Vault Gateway `PublicKeyGet` requests allow unbounded `activeRequests` map growth causing memory exhaustion - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The Vault gateway handler explicitly skips authorization for `MethodPublicKeyGet` requests and, whenever the cached public key is unset, inserts an entry into the in-memory `activeRequests` map keyed by attacker-controlled `req.ID` for every such request, with no rate limiting or per-caller quota before that allocation.

### Finding Description
`HandleJSONRPCUserMessage` explicitly documents that "Public key requests don't require authorization" and only checks the cache before creating an `activeRequest`: [1](#0-0) 
If `h.cachedPublicKeyGetResponse` is `nil` (e.g., at startup before the first background refresh succeeds in `fetchVaultPublicKey`, called on a 1-minute ticker, or any time refresh transiently fails), every incoming `MethodPublicKeyGet` request bypasses `requestProcessor.ProcessRequest` (the auth/allowlist gate) and goes straight to `newActiveRequest`, which allocates a new `activeRequest` struct (containing a `map[string]*jsonrpc.Response`, a mutex, and a callback) and inserts it into `h.activeRequests`: [2](#0-1) 
The only precondition enforced upstream in `gateway.ProcessRequest` is that the JSON-RPC request ID be non-empty and ≤200 characters — there is no authentication requirement, allowlist check, or per-IP/per-caller rate limiter applied before this handler is reached: [3](#0-2) 
An unprivileged, unauthenticated HTTP client can therefore submit an unbounded stream of `MethodPublicKeyGet` requests, each with a unique `req.ID` (duplicate IDs are only rejected, not rate-limited), causing the handler to allocate a new map entry per request. Entries are only reaped by a background ticker (`defaultCleanUpPeriod = 5 * time.Second`) once each entry has aged past `requestTimeout` (default 30s): [4](#0-3) [5](#0-4) [6](#0-5) 
This is structurally analogous to the CVE-2017-7472 bug class: an unprivileged caller can repeatedly trigger allocation of a tracked, per-request kernel/application object (there, a `reqkey` keyring; here, an `activeRequest` map entry) with no bound on the number of concurrently outstanding objects, relying solely on time-based reaping rather than an admission/quota control, allowing memory to grow proportionally to attacker request rate during the retention window.

### Impact Explanation
Because the growth is gated only by wall-clock expiry (up to `requestTimeout`, default 30s) and a 5-second sweep interval rather than a cap on the number of concurrent entries or a per-caller rate limit, an attacker who can sustain a sufficiently high request rate of unique-ID `MethodPublicKeyGet` calls can grow `h.activeRequests` unbounded (bounded only by attacker throughput and available memory) for as long as the cache remains unpopulated, and can also fan out real requests to all DON member nodes (`fanOutToVaultNodes`) for each entry, adding node-side load. This is a memory-consumption / availability degradation vector reachable from an unauthenticated network client, without requiring any valid allowlist entry, JWT, or key.

### Likelihood Explanation
The condition that gates this path — `cachedPublicKeyGetResponse == nil` — is guaranteed to be true for the entire duration between gateway handler start and the first successful `fetchVaultPublicKey` refresh (and again any time the periodic refresh transiently fails, e.g. due to node connectivity issues), which is an externally-observable and reasonably reproducible window. During that window the attack requires no credentials, no valid workflow owner, and no allowlist membership — only network access to the gateway's public HTTP endpoint, making likelihood moderate-to-high in any deployment where the vault DON periodically has connectivity hiccups or restarts.

### Recommendation
Apply a per-caller/per-IP rate limiter (or a global admission limiter, similar to `globalNodeRateLimiter`/`perNodeRateLimiters` used elsewhere in the gateway) to unauthenticated `MethodPublicKeyGet` requests before `newActiveRequest` is called, and/or bound the maximum size of `activeRequests` (rejecting new entries once a configurable cap is reached) so that memory consumption cannot grow unbounded purely as a function of attacker request rate during periods when the public-key cache is empty.

### Proof of Concept
1. Restart (or otherwise force `cachedPublicKeyGetResponse` to `nil` on) the Vault gateway handler so the public-key cache is empty.
2. From an unauthenticated client, issue a high-rate loop of HTTP POST requests to the gateway's public endpoint with JSON-RPC method `vaultcommon.MethodPublicKeyGet`, each using a distinct `id` field (e.g., a UUID) and no `Authorization` header.
3. Observe that each request reaches `HandleJSONRPCUserMessage` → `newActiveRequest` without any authorization check (per `core/services/gateway/handlers/vault/handler.go:404-420`), inserting a new entry into `h.activeRequests` and fanning the request out to every DON member node.
4. Sustain the request rate above ~ (map-entry count)/(`requestTimeout`≈30s) to keep `len(h.activeRequests)` growing faster than the 5-second cleanup ticker can reap expired entries, observing increasing gateway process memory (RSS) proportional to the sustained request rate.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L44-46)
```go
	defaultCleanUpPeriod                    = 5 * time.Second
	defaultPublicKeyGetCacheDurationSeconds = 300
)
```

**File:** core/services/gateway/handlers/vault/handler.go (L217-219)
```go
	if cfg.RequestTimeoutSec == 0 {
		cfg.RequestTimeoutSec = 30
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L360-384)
```go
// removeExpiredRequests removes expired requests from the pending requests map
func (h *handler) removeExpiredRequests(ctx context.Context) {
	h.mu.RLock()
	var expiredRequests []*activeRequest
	now := h.clock.Now()
	for _, userRequest := range h.activeRequests {
		if now.Sub(userRequest.createdAt) > h.requestTimeout {
			expiredRequests = append(expiredRequests, userRequest)
		}
	}
	h.mu.RUnlock()

	for _, er := range expiredRequests {
		responses := er.copiedResponses()
		var nodeResponses strings.Builder
		for nodeKey, nodeResponse := range responses {
			_, _ = fmt.Fprintf(&nodeResponses, "%s ---::: %v               ", nodeKey, nodeResponse)
		}
		nodeResponsesStr := nodeResponses.String()
		err := h.sendResponse(ctx, er, h.errorResponse(er.req, api.RequestTimeoutError, errors.New("request expired without getting quorum of responses from nodes. Available responses: "+nodeResponsesStr), []byte(nodeResponsesStr)))
		if err != nil {
			h.lggr.Errorw("error sending response to user", "requestID", er.req.ID, "error", err)
		}
	}
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-420)
```go
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L457-472)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/gateway.go (L221-279)
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
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}
```
