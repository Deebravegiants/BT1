## Analysis

I found a plausible analog to CVE-2016-2179's bug class (unbounded queue entries from unauthenticated crafted requests causing memory exhaustion) in the gateway's Vault handler.

### Title
Unbounded, unauthenticated `activeRequests` map growth in gateway Vault handler enables memory-exhaustion DoS - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
`HandleJSONRPCUserMessage` in the gateway Vault handler creates an entry in the handler's `activeRequests` map for every incoming `MethodPublicKeyGet` request when the public key is not already cached — **before any authorization check** — keyed by the caller-supplied `req.ID`. There is no cap on the number of concurrent entries (unlike `core/services/gateway/handlers/common/requestcache.go`, which enforces a `maxCacheSize`), so a remote, unprivileged client can flood the gateway with distinct-ID `GetPublicKey` requests to grow this map without bound until the periodic 5-second sweep expires entries after `requestTimeout` (default 30s).

### Finding Description [1](#0-0)  shows that for `vaulttypes.MethodPublicKeyGet`, the handler explicitly documents that "Public key requests don't require authorization" and, on a cache miss, immediately calls `h.newActiveRequest(req, callback)` prior to any authorization or per-request quota check. [2](#0-1)  shows `newActiveRequest` only rejects a request if the exact same `req.ID` already exists; it never checks the total size of `h.activeRequests` before inserting a new entry, unlike the sibling `requestCache` type which has an explicit `maxCacheSize` bound ( [3](#0-2) ).

Cleanup only happens on a periodic ticker (`defaultCleanUpPeriod = 5 * time.Second`) that removes entries older than `h.requestTimeout` (default 30s) — [4](#0-3)  and [5](#0-4) . The only inbound guard is a request-ID length check of 200 characters ( [6](#0-5) ) — there is no rate limiter applied to incoming user messages (the only rate limiter present, `nodeRateLimiter`, governs node responses, not user requests).

This mirrors the CVE-2016-2179 bug class: an unauthenticated/unprivileged actor drives creation of server-side queue/tracking entries (DTLS out-of-order message queue ↔ gateway `activeRequests` map) whose lifetime is bounded only by a timeout, with no bound on the number of concurrently outstanding entries, allowing memory exhaustion via many crafted, cheap requests.

### Impact Explanation
Each `activeRequest` entry holds a `jsonrpc.Request`, a `responses` map, and a `Callback`. An attacker who can reach the gateway's public JSON-RPC endpoint (the vault handler explicitly allows this method without authorization) can generate a high rate of unique-ID `GetPublicKey` requests to accumulate many concurrent entries, each pinned for up to `requestTimeout` (default 30s), consuming heap memory and goroutine/callback resources proportional to attacker-controlled request volume. Sustained or bursty attack traffic could exhaust gateway memory, degrading or crashing the node process handling the gateway connector, denying service to legitimate DON members and users of the same gateway.

### Likelihood Explanation
The `MethodPublicKeyGet` path is reachable by any client able to submit a JSON-RPC user message to the gateway before authorization is checked, and no rate limiter or cache-size cap is applied to this specific pre-auth path. The only "protection" (aggressive public-key caching, per the comment "Note we cache this value quite aggressively so don't need to worry about DoS") is defeated on any cache miss (initial cold start, cache invalidation, or race at startup before the periodic 1-minute refresh populates the cache), and each request must use a distinct `req.ID` to avoid the "already exists" collision check, which is trivial for an attacker to satisfy.

### Recommendation
- Enforce a maximum size on `h.activeRequests` (mirroring `requestCache.maxCacheSize` in `core/services/gateway/handlers/common/requestcache.go`) and reject new entries once the limit is reached.
- Apply a per-sender/global rate limiter to incoming `HandleJSONRPCUserMessage` calls (especially for the unauthenticated `MethodPublicKeyGet` path) before an `activeRequest` is created.
- Consider deduplicating/coalescing concurrent in-flight `GetPublicKey` fetches (single-flight pattern) instead of creating a new tracked request per caller-supplied ID.

### Proof of Concept
1. Identify a gateway node's Vault-handler-exposed method endpoint that accepts unauthenticated `MethodPublicKeyGet` JSON-RPC requests (per `core/services/gateway/handlers/vault/handler.go:404-420`).
2. At a point where the cached public key is unset or invalidated (e.g., immediately after gateway startup, before `fetchVaultPublicKey`'s 1-minute refresh populates the cache, or during any transient cache-miss window), send a large number of `MethodPublicKeyGet` requests, each with a distinct `req.ID` (up to 200 chars) — no authentication header/token required.
3. Each request causes `newActiveRequest` to insert a new entry into `h.activeRequests`, held for up to `requestTimeout` (default 30s) before the 5-second sweep can expire it.
4. Repeat at a rate exceeding the expiry sweep's reclaim rate to grow `h.activeRequests` unbounded, observing increasing gateway process memory usage.

**Caveat / uncertainty:** I could not fully verify whether an upstream network-layer control (e.g., a reverse proxy, WAF, or an outer gateway-connector-level global rate limiter not visible in the files I inspected) mitigates this in production deployments; the vault handler code itself does not implement such a limit on this specific path. If such an external control exists in the actual deployment, the practical exploitability would be reduced.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L271-299)
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

**File:** core/services/gateway/handlers/common/requestcache.go (L27-66)
```go
type requestCache[T any] struct {
	cache        map[globalID]*pendingRequest[T]
	maxCacheSize uint32
	timeout      time.Duration
	mu           sync.Mutex
}

type globalID struct {
	sender string
	id     string
}

type pendingRequest[T any] struct {
	handlers.Callback
	responseData *T
	timeoutTimer *time.Timer
	mu           sync.Mutex
}

func NewRequestCache[T any](timeout time.Duration, maxCacheSize uint32) RequestCache[T] {
	return &requestCache[T]{cache: make(map[globalID]*pendingRequest[T]), timeout: timeout, maxCacheSize: maxCacheSize}
}

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
