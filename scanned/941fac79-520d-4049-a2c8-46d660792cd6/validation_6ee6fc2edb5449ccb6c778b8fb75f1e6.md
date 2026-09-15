## Analysis

The reported bug class — an unbounded per-user request list/map that is populated without a size cap, then iterated by cleanup/liquidation-like logic, enabling DoS — has a concrete analog in the gateway Vault handler's `activeRequests` map.

### Root Cause

`handler.activeRequests` is a plain `map[string]*activeRequest` with **no maximum-size check**, unlike the generic gateway request cache which explicitly enforces `maxCacheSize`: [1](#0-0) 

By contrast, the Vault handler inserts unconditionally in `newActiveRequest`: [2](#0-1) 

Critically, `MethodPublicKeyGet` requests skip the authorization/`requestProcessor.ProcessRequest` path entirely and go straight to `newActiveRequest` on a cache miss: [3](#0-2) 

So an unauthenticated caller hitting the gateway's HTTP endpoint for `HandleJSONRPCUserMessage` can submit an unbounded number of `MethodPublicKeyGet` requests, each with a unique `req.ID` (only constrained to be non-empty and ≤200 chars): [4](#0-3) 

Each such request adds a persistent entry to `activeRequests` that survives until the periodic 5-second cleanup ticker's `removeExpiredRequests` sweep (bounded by `requestTimeout`, default 30s), giving an attacker a sizeable window to accumulate many concurrent entries with no admission-control limit: [5](#0-4) [6](#0-5) 

This is the same shape as the reported issue: an unbounded, unauthenticated-reachable collection grown without a size gate, then linearly scanned by maintenance logic, degrading the whole handler (and hence the vault gateway path) for all users of that DON as the map grows.

### Title
Unbounded growth of the Vault gateway `activeRequests` map via unauthenticated `MethodPublicKeyGet` requests can DoS the handler - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The Vault gateway handler's `HandleJSONRPCUserMessage` allows `MethodPublicKeyGet` requests to bypass authorization entirely on a cache miss, and `newActiveRequest` inserts into the `activeRequests` map with no maximum-size enforcement, unlike the generic `common.requestCache` which explicitly caps `maxCacheSize`.

### Finding Description
`MethodPublicKeyGet` requests are processed before any authorization check when the cached public key is unavailable, directly calling `h.newActiveRequest(req, callback)` [3](#0-2) . `newActiveRequest` only rejects duplicate IDs, never a full map, so an attacker submitting requests with unique IDs (only length-capped at 200 chars) can grow `activeRequests` without bound between cleanup cycles [2](#0-1) . Entries persist for up to `requestTimeout` (default 30s) before `removeExpiredRequests` (run every 5s) reclaims them [6](#0-5) .

### Impact Explanation
Sustained flooding keeps the map large, increasing memory consumption and the cost of the periodic `removeExpiredRequests` scan and lock contention (`h.mu`), degrading processing of legitimate vault gateway requests (secrets create/update/delete/list) for all callers of that DON — a protocol/service-level DoS analogous to the reported `partyAPendingQuotes` growth issue, though scoped to gateway node availability rather than fund-affecting liquidation logic.

### Likelihood Explanation
Reachable by any unprivileged/unauthenticated network client able to reach the gateway's user-message endpoint, requiring no special role, key, or prior state — only sending many `MethodPublicKeyGet` requests with distinct IDs faster than the 5s/30s cleanup cadence can reclaim them.

### Recommendation
Enforce a maximum size on `activeRequests` (mirroring `common.requestCache.maxCacheSize`) and reject/rate-limit new entries once the limit is reached, or apply a per-caller/global rate limiter to unauthenticated `MethodPublicKeyGet` traffic before it reaches `newActiveRequest`.

### Proof of Concept
1. An unauthenticated client sends many JSON-RPC requests with `Method: vaulttypes.MethodPublicKeyGet` and unique `ID`s to the gateway's Vault handler faster than the cache/cleanup interval.
2. Each request misses the cached public key path in `HandleJSONRPCUserMessage` [3](#0-2)  and calls `newActiveRequest`, which unconditionally inserts into `h.activeRequests` [2](#0-1) .
3. Entries accumulate until `removeExpiredRequests` runs, allowing the attacker to sustain a large `activeRequests` map, increasing lock hold time and memory pressure that impacts other legitimate vault requests handled by the same handler instance.

### Citations

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

**File:** core/services/gateway/handlers/vault/handler.go (L279-299)
```go
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

**File:** core/services/gateway/handlers/vault/handler.go (L360-383)
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
