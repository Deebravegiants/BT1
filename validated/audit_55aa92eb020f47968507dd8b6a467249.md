Confirmed: the code matches the claim exactly. `newActiveRequest` in `core/services/gateway/handlers/vault/handler.go` inserts unconditionally into `h.activeRequests` with no size cap, and the `MethodPublicKeyGet` branch in `HandleJSONRPCUserMessage` reaches it before any authorization check runs (auth only applies to the `IsGatewaySecretsMethod` branch below). The HTTP layer (`core/services/gateway/network/httpserver.go`) only enforces `MaxRequestBytesLimiter` (per-request body size), not a cap on the *number* of concurrent distinct request IDs, and there's no per-sender/global request-count rate limiter gating this cache-miss path before the map insert. This is a genuine, uncapped growth path reachable by an unauthenticated client. The sibling `requestCache.NewRequest` in `handlers/common/requestcache.go` does enforce `maxCacheSize`, confirming the asymmetry.

Audit Report

## Title
Unbounded `activeRequests` map in vault gateway handler allows unauthenticated memory-exhaustion DoS - (File: core/services/gateway/handlers/vault/handler.go)

## Summary
`newActiveRequest` in the vault gateway handler inserts every incoming request into `h.activeRequests` keyed by attacker-controlled `req.ID`, with no maximum-size check, unlike the sibling `requestCache.NewRequest` in `core/services/gateway/handlers/common/requestcache.go` which enforces `maxCacheSize`. The `vaulttypes.MethodPublicKeyGet` path reaches `newActiveRequest` on cache miss before any authorization check, so an unauthenticated caller can flood the map with unique request IDs faster than the 5-second `removeExpiredRequests` cleanup tick, growing gateway memory usage without bound.

## Finding Description
`newActiveRequest` unconditionally adds an entry to `h.activeRequests` for every unique `req.ID`, allocating an `activeRequest` struct with a `responses` map, with no upper bound check: [1](#0-0) 

`HandleJSONRPCUserMessage` routes `MethodPublicKeyGet` requests to `newActiveRequest` on cache miss, before the authorization/`requestProcessor.ProcessRequest` call that gates the other vault methods (`MethodSecretsCreate/Update/Delete/List`) further down: [2](#0-1) 

The only per-request validation is a 200-character cap on `req.ID`, which does not limit the *count* of concurrently tracked unique IDs: [3](#0-2) 

Entries are only removed on a periodic 5-second tick via `removeExpiredRequests`, and only once `h.requestTimeout` (default 30s) has elapsed since `createdAt`: [4](#0-3) [5](#0-4) 

By contrast, the general-purpose `requestCache` in the same gateway codebase explicitly rejects new requests once `len(c.cache) >= int(c.maxCacheSize)`: [6](#0-5) 

At the HTTP layer, `core/services/gateway/network/httpserver.go`'s `handleRequest` enforces only a per-request body-size cap via `MaxRequestBytesLimiter`/`http.MaxBytesReader`; there is no limiter bounding the number of distinct concurrent requests accepted before `ProcessRequest`/`HandleJSONRPCUserMessage` is invoked: [7](#0-6) . Thus no existing check — auth, size limit, or rate limiter — bounds the number of live `activeRequest` entries an unauthenticated client can create via the public-key-get cache-miss path.

## Impact Explanation
This maps to a resource-exhaustion / denial-of-service class impact: an unauthenticated actor can grow the gateway process's memory by creating many long-lived `activeRequest` entries (each holding a `responses` map and captured request data) tied to unique attacker-chosen IDs, degrading or crashing the gateway node and disrupting the vault capability (and potentially other gateway traffic sharing the process). It is a genuine defense-in-depth gap given the codebase's own established pattern (`requestCache.maxCacheSize`) for bounding exactly this kind of map.

## Likelihood Explanation
Exploitation requires no credentials: the `MethodPublicKeyGet` cache-miss branch is explicitly documented in-code as not requiring authorization, and is reachable directly via the gateway's public `/user` HTTP endpoint. The only precondition is that the public key cache be empty/stale (true at startup, and after any TTL/cache-miss window), during which every distinct `req.ID` under 200 characters used within a `MethodPublicKeyGet` request creates a new tracked entry. Repeating this faster than the 5-second cleanup tick (and before the 30s `requestTimeout` expiry) causes accumulation. This is straightforward to automate and repeat indefinitely.

## Recommendation
Add an explicit upper bound (e.g., `maxActiveRequests`) check in `newActiveRequest`, rejecting new entries once `len(h.activeRequests)` reaches a configured limit, mirroring `requestCache.NewRequest`'s `len(c.cache) >= int(c.maxCacheSize)` check in `core/services/gateway/handlers/common/requestcache.go`. Additionally, consider gating the public-key cache-miss path behind a lightweight per-sender/global rate limiter (independent of the heavier vault authorization flow) before an `activeRequest` entry is allocated.

## Proof of Concept
1. Start the vault gateway handler with an empty/expired public-key cache (e.g., immediately after handler start, before `fetchVaultPublicKey`'s first successful cache population, or by restarting to invalidate the cache).
2. From an unauthenticated HTTP client, POST JSON-RPC requests to the gateway's `/user` endpoint with `method: "vault_publicKeyGet"`, using a unique `id` per request (e.g., an incrementing counter kept under 200 characters), at a rate exceeding one request per 5 seconds.
3. Observe (via added instrumentation or a Go unit test directly calling `handler.newActiveRequest` in a loop with unique IDs, checking `len(h.activeRequests)`) that the map grows without any rejection, and that entries persist until `h.requestTimeout` (default 30s) elapses and the next `removeExpiredRequests` tick runs — demonstrating unbounded growth is possible when the flood rate exceeds the cleanup rate.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L271-300)
```go
func (h *handler) Start(_ context.Context) error {
	return h.StartOnce("VaultHandler", func() error {
		h.lggr.Debug("starting vault handler")
		if h.jwtAuth != nil {
			if err := h.jwtAuth.Start(context.Background()); err != nil {
				return fmt.Errorf("failed to start JWTBasedAuth: %w", err)
			}
		}
		go func() {
			ctx, cancel := h.stopCh.NewCtx()
			defer cancel()
			ticker := h.clock.NewTicker(defaultCleanUpPeriod)
			tickerVaultPublicKeyRefresh := h.clock.NewTicker(1 * time.Minute)
			defer ticker.Stop()
			defer tickerVaultPublicKeyRefresh.Stop()
			for {
				select {
				case <-ticker.Chan():
					h.removeExpiredRequests(ctx)
				case <-tickerVaultPublicKeyRefresh.Chan():
					// periodically, fetch vault public key, so we can cache it
					h.fetchVaultPublicKey(ctx)
				case <-h.stopCh:
					return
				}
			}
		}()
		return nil
	})
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

**File:** core/services/gateway/handlers/vault/handler.go (L394-420)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
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

**File:** core/services/gateway/handlers/common/requestcache.go (L50-66)
```go
func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
```

**File:** core/services/gateway/network/httpserver.go (L211-234)
```go
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
```
