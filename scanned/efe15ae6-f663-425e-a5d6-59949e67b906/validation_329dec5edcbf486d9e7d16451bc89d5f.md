### Title
Unbounded `activeRequests` map allows unauthenticated quota bypass and memory-exhaustion DoS - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The gateway vault handler's `newActiveRequest` inserts every incoming request into an in-memory map keyed by request ID with no upper bound (`maxCacheSize`) check, unlike the sibling `RequestCache` implementation elsewhere in the gateway package which explicitly enforces `maxCacheSize`. Critically, the `vaulttypes.MethodPublicKeyGet` path can reach `newActiveRequest` **before** authorization is performed, making this reachable by unprivileged/unauthenticated callers.

### Finding Description
`newActiveRequest` unconditionally adds an entry to `h.activeRequests` for every unique request ID, with no size limit: [1](#0-0) 

Contrast this with the general-purpose `RequestCache` in the same gateway codebase, which explicitly guards against unbounded growth: [2](#0-1) 

The vault handler's `HandleJSONRPCUserMessage` routes `MethodPublicKeyGet` requests to `newActiveRequest` whenever the public key is not currently cached — this branch runs before any authorization/authentication check: [3](#0-2) 

An unprivileged/unauthenticated client only needs to supply a unique `req.ID` (bounded to 200 chars, but otherwise attacker-controlled) for each `MethodPublicKeyGet` request: [4](#0-3) 

Each accepted request allocates a new `activeRequest` struct plus a `responses` map sized for the DON member count, retained in memory until `removeExpiredRequests` runs on its periodic tick (`defaultCleanUpPeriod` = 5s): [5](#0-4) [6](#0-5) 

This mirrors the CVE-2019-10723 bug class: an attacker-influenced size/count value (here, the number of concurrently-tracked unique request IDs) is not validated against any upper bound before memory is allocated and retained, enabling resource exhaustion.

### Impact Explanation
An unauthenticated caller can flood the gateway's `/user` HTTP endpoint with `MethodPublicKeyGet` requests using unique IDs faster than the 5-second cleanup tick, causing unbounded growth of the `activeRequests` map and associated per-request state. This can exhaust gateway node memory, resulting in denial of service for the vault gateway path (and potentially co-located handlers sharing gateway process memory).

### Likelihood Explanation
Reachability requires no authentication for the `MethodPublicKeyGet` branch, only a distinct request ID under 200 characters per request; other gateway request-size/byte limits (e.g., `MaxRequestBytes`) do not bound the *count* of concurrent tracked requests. This makes exploitation straightforward for any external client with network access to the gateway's user-facing HTTP endpoint.

### Recommendation
Add an explicit upper bound (`maxCacheSize`/`maxActiveRequests`) check in `newActiveRequest`, rejecting new entries once the map reaches a configured limit — following the same pattern already used by `requestCache.NewRequest` in `core/services/gateway/handlers/common/requestcache.go`. Additionally, consider requiring the public-key cache-miss path to be gated behind the existing per-sender/global rate limiters before an `activeRequest` entry is created.

### Proof of Concept
1. Ensure the vault gateway's public-key cache is empty/expired (e.g., immediately after handler restart, or race with cache TTL expiry).
2. From an unauthenticated client, rapidly send many JSON-RPC requests to the gateway's `/user` endpoint with `method: "vault_publicKeyGet"` and a unique `id` on each request (e.g., incrementing counter, staying under 200 chars), at a rate exceeding one request per 5 seconds (the cleanup tick interval).
3. Observe `activeRequests` map size and gateway process memory grow unbounded as long as the flood continues, since no `newActiveRequest` call is rejected for exceeding a size limit.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L83-90)
```go
type activeRequest struct {
	req       jsonrpc.Request[json.RawMessage]
	responses map[string]*jsonrpc.Response[json.RawMessage]
	mu        sync.Mutex

	createdAt time.Time
	gwhandlers.Callback
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
