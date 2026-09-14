This confirms there is no `maxActiveRequests`/`maxCacheSize` guard anywhere in `core/services/gateway/handlers/vault/handler.go` — the `activeRequests` map has no bound, unlike the sibling `common.NewRequestCache` design which explicitly enforces `maxCacheSize`.

### Title
Unauthenticated `MethodPublicKeyGet` flood causes unbounded gateway memory growth via unlimited `activeRequests` map entries - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The Vault gateway handler's `HandleJSONRPCUserMessage` skips all authorization for `vaulttypes.MethodPublicKeyGet` requests and, whenever the public key is not yet cached, creates a new `activeRequest` entry keyed by the caller-supplied `req.ID` with no upper bound on the number of concurrent entries, unlike the sibling `common.NewRequestCache`, which explicitly enforces a `maxCacheSize`.

### Finding Description
`gateway.ProcessRequest` decodes an inbound HTTP JSON-RPC request and dispatches it to the matching handler's `HandleJSONRPCUserMessage` without requiring any prior authentication at the gateway layer [1](#0-0) . For the Vault handler, `MethodPublicKeyGet` explicitly bypasses the authorization/request-processor path: "Public key requests don't require authorization" [2](#0-1) .

Each such request, while the public key is not yet cached, is registered via `newActiveRequest`, which only rejects an exact duplicate `req.ID`; it never checks the total size of `h.activeRequests` before inserting: [3](#0-2) . The only bound on `req.ID` is a length cap (≤200 chars) and non-empty check [4](#0-3) , which does nothing to limit the *number* of distinct IDs an unauthenticated caller can submit.

Cleanup of these entries only happens on a fixed 5-second ticker (`defaultCleanUpPeriod`) and only expires requests older than `requestTimeout` (default 30s): [5](#0-4) [6](#0-5) . By contrast, the gateway's generic request cache used elsewhere in the codebase (`core/services/gateway/handlers/common/requestcache.go`) explicitly enforces `maxCacheSize` and rejects new entries once full [7](#0-6) ; the Vault handler's `activeRequests` map has no equivalent guard.

This mirrors the CVE-2016-8858 bug class: a pre-authentication handler accepts an unbounded volume of distinct, attacker-controlled protocol identifiers and accumulates per-request state (callback, request copy, response map) in memory, bounded only by a time-based reaper rather than a count-based limit — allowing an unprivileged remote caller to grow memory faster than it is reclaimed.

### Impact Explanation
An unauthenticated remote client can repeatedly send `MethodPublicKeyGet` requests with unique `req.ID` values (e.g., random 200-char strings) at a rate exceeding what the DON can respond to or what the 5-second/30-second reaper can clear. Each entry allocates an `activeRequest` struct, holds the full request, and a `responses` map that is filled in as node replies stream in. Sustained flooding can exhaust gateway memory, causing degraded service or crash (denial of service) for the whole gateway process, affecting all DONs/handlers hosted by it, not just Vault.

### Likelihood Explanation
This code path requires no authentication or allowlist membership at all — any HTTP client that can reach the gateway endpoint can invoke `MethodPublicKeyGet`. The condition "public key not yet cached" is guaranteed at node startup and after any refresh failure, and the vulnerability window can in principle be widened by resource exhaustion itself (slower node responses keep the cache from populating). Since there is no per-caller or global cap on `activeRequests` size in this handler, exploitation only requires generating many unique request IDs, which is trivial.

### Recommendation
Add a `maxActiveRequests` bound (analogous to `common.requestCache.maxCacheSize`) to the Vault handler's `newActiveRequest`, rejecting or rate-limiting new entries once the map reaches a configured ceiling. Additionally, consider requiring a lightweight per-source rate limit (similar to `nodeRateLimiter` but for inbound user requests) even for the unauthenticated `MethodPublicKeyGet` path, and/or shortening the cleanup interval relative to `requestTimeout` under load.

### Proof of Concept
1. Start a gateway with the Vault handler configured, before `cachedPublicKeyGetResponse` has been populated (e.g., immediately at startup, or force repeated `fetchVaultPublicKey` failures).
2. From an unauthenticated client, send a burst of JSON-RPC requests to the gateway HTTP endpoint with `method: "vault_publicKeyGet"` and a distinct random `id` (≤200 chars) on each request, faster than the ~5s cleanup ticker and DON response time.
3. Observe `handler.activeRequests` (or process RSS) grow unboundedly with the number of requests sent, since `newActiveRequest` only rejects exact ID collisions and enforces no total-count limit [3](#0-2) .

### Citations

**File:** core/services/gateway/gateway.go (L267-276)
```go
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

**File:** core/services/gateway/handlers/vault/handler.go (L394-401)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-419)
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

**File:** core/services/gateway/handlers/common/requestcache.go (L60-66)
```go
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
```
