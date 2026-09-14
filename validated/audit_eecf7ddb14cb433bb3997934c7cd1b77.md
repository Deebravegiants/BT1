### Title
Unbounded growth of gateway Vault handler's `activeRequests` map via unauthenticated `vault_publicKeyGet` requests - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The Nervos ckb advisory (CVE-2021-45699 / GHSA-2969-8hh9-57jc) describes an unprivileged remote actor causing unbounded growth of an in-memory `HashMap` (the misbehavior map), leading to memory-allocation failure/DoS. The analogous bug class in this codebase is the gateway Vault handler's `activeRequests` map, which is keyed by client-supplied request IDs and populated without any bound on the number of concurrently pending requests, reachable by an unauthenticated client through `vault_publicKeyGet`.

### Finding Description
`handler.activeRequests` is a plain `map[string]*activeRequest` with no maximum-size enforcement [1](#0-0) . Entries are inserted by `newActiveRequest`, which only checks for ID collision, never for total map size [2](#0-1) .

Critically, `HandleJSONRPCUserMessage` handles `vaulttypes.MethodPublicKeyGet` (`vault_publicKeyGet`) **before** any authorization check — the code comment explicitly states "Public key requests don't require authorization" — and, when the public key isn't already cached, calls `newActiveRequest` directly from unauthenticated user input: [3](#0-2) 

Only the request ID is checked for length (≤200 chars) and non-emptiness [4](#0-3) ; there is no rate limiter or cap on the number of distinct in-flight user requests tracked in `activeRequests`. Entries are only removed by a periodic cleanup goroutine that runs every `defaultCleanUpPeriod` (5s) and evicts entries older than `requestTimeout` (default 30s, configurable) [5](#0-4) [6](#0-5) .

An unauthenticated client can therefore submit an unbounded number of `vault_publicKeyGet` requests with distinct request IDs (up to 200 bytes each) faster than the 5-second sweep interval, causing `activeRequests` (and the corresponding `responses` sub-maps and callback state) to grow without bound for the duration of `requestTimeout`, consuming gateway memory. This mirrors the ckb bug class: unbounded allocation of a map driven by attacker-controlled keys with no throttling on insertion rate or map size.

### Impact Explanation
Unbounded memory growth on the gateway node from a purely unauthenticated, single-client request stream can exhaust gateway process memory, causing degraded performance or crash (OOM) of the gateway, which is a shared, internet-facing component serving multiple DONs/handlers. This is a resource-exhaustion / availability impact consistent with CWE-770 and the CVSS vector in the report (`C:N/I:N/A:H`).

### Likelihood Explanation
The `vault_publicKeyGet` path bypasses authorization by design, so the only friction for an attacker is generating unique, ≤200-character request IDs and sending them rapidly — a trivial, unprivileged, purely network-based action requiring no valid credentials, JWT, or allowlist membership. No node-side rate limiter is applied to user (as opposed to node) requests in this handler; the only rate limiter present (`nodeRateLimiter`) is applied to node-originated responses, not to incoming user requests [7](#0-6) .

### Recommendation
- Enforce a maximum size on `activeRequests` (as is already done via `maxCacheSize` in the generic `RequestCache` type used elsewhere) and reject/queue new requests once the limit is reached.
- Apply a per-sender/global rate limiter to `HandleJSONRPCUserMessage`, especially for the unauthenticated `vault_publicKeyGet` path, before calling `newActiveRequest`.
- Consider requiring the pre-existing cached-key fast path to be the only public entry point once a key has been fetched once, and bound the number of outstanding uncached public-key fetches (e.g., single-flight/dedupe similar to `responseCache.Fetch`'s `singleflight.Group` pattern already used in `core/services/gateway/handlers/capabilities/v2/response_cache.go`).

### Proof of Concept
1. Configure a Chainlink gateway node running the Vault handler (`core/services/gateway/handlers/vault/handler.go`) with the JWT/Auth0 authorizer optional (i.e., default config where `vault_publicKeyGet` is unauthenticated).
2. Ensure the gateway's cached public key is not yet populated (e.g., immediately after startup, before `fetchVaultPublicKey`'s periodic refresh runs, or by forcing cache misses).
3. From an unauthenticated client, send a high-rate burst of JSON-RPC requests to the gateway's user endpoint with method `vault_publicKeyGet`, each with a unique `id` (up to 200 characters), faster than one every 5 seconds (the cleanup ticker interval) and sustained for longer than `requestTimeoutSec` (default 30s).
4. Observe `handler.activeRequests` grow unbounded in the gateway process (verifiable via added metrics/logging or memory profiling), since no size cap or user-rate limiter is enforced in `HandleJSONRPCUserMessage`/`newActiveRequest`.
5. Continue sending requests to observe increasing gateway memory consumption, consistent with an allocation-without-limits condition.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L151-152)
```go
	activeRequests      map[string]*activeRequest
	metrics             *metrics
```

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

**File:** core/services/gateway/handlers/vault/handler.go (L480-487)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	l := logger.With(h.lggr, "method", resp.Method, "requestID", resp.ID, "nodeAddr", nodeAddr)
	l.Debugw("handling node response")

	if !h.nodeRateLimiter.Allow(nodeAddr) {
		l.Debugw("node is rate limited", "nodeAddr", nodeAddr)
		return nil
	}
```
