### Title
Unauthenticated flooding of `MethodPublicKeyGet` requests causes unbounded growth of the gateway vault handler's `activeRequests` map - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The Vault gateway handler's `HandleJSONRPCUserMessage` explicitly skips authorization for `vaulttypes.MethodPublicKeyGet` requests and, whenever the public key is not currently cached, calls `newActiveRequest` to insert a new entry into the handler's `activeRequests` map keyed by the attacker-supplied `req.ID` before any authentication or rate limiting is applied. This mirrors the reported Grafana OAuth DoS pattern: an unauthenticated caller can repeatedly submit unique request IDs to grow server-side memory without bound, potentially exhausting node memory.

### Finding Description
In `HandleJSONRPCUserMessage`: [1](#0-0) 

the code explicitly documents that `MethodPublicKeyGet` "don't require authorization" and relies solely on caching to avoid DoS ("Note we cache this value quite aggressively so don't need to worry about DoS"). However, the fallback path — reached whenever `getCachedPublicKey()` returns `nil` (e.g., before the first successful key fetch, immediately after a node restart, or if `fetchVaultPublicKey` continues to fail/be delayed) — calls: [2](#0-1) 

which inserts a brand-new map entry keyed by the caller-controlled `req.ID` via `newActiveRequest`: [3](#0-2) 

The only pre-insertion validation is a length check on `req.ID` (≤200 chars) and emptiness check: [4](#0-3) 

No authentication, authorization, or rate limiting gates this insertion — `req.Auth` is never checked for this method, and there is no per-caller/per-IP quota applied before the map write. Cleanup only happens periodically via `removeExpiredRequests`, gated by `requestTimeout` (default 30s) and running on a fixed ticker (`defaultCleanUpPeriod`): [5](#0-4) [6](#0-5) 

Because each `activeRequest` also allocates a `responses` map and holds a reference to the caller's `callback`, an attacker who submits requests faster than the cleanup ticker reaps them (or with IDs designed to sit just under the 30s timeout window, submitted continuously) can sustain unbounded growth of `h.activeRequests`, consuming memory proportional to the number of unique request IDs supplied. This is structurally identical to the reported OAuth login DoS: an unauthenticated, unbounded, per-request server-side state accumulation keyed by attacker-controlled unique values.

Notably, other constructs in the same codebase (e.g., `RequestReplayGuard`, `GatewayVaultRequestProcessor`, `ValidateCiphertextSizes`) explicitly call out and guard against "unauthenticated callers creating unbounded ... tenants" as a known bug class: [7](#0-6) [8](#0-7) 
but the `MethodPublicKeyGet` fast path in `handler.go` was not brought under this same protection — it was assumed safe purely because of caching, without considering the pre-cache-population window or cache-fetch failure window.

### Impact Explanation
An unauthenticated party with network access to the gateway's Vault JSON-RPC endpoint can trigger unbounded server-side memory allocation with no authentication and minimal cost per request (just a unique string up to 200 bytes plus map/struct overhead). Sustained flooding can exhaust gateway node memory, causing degraded performance or a crash — a denial of service against the gateway component, which is explicitly in the internet-facing gateway attack surface named in scope (handlers/caches).

### Likelihood Explanation
The window in which `getCachedPublicKey()` returns `nil` is not merely a narrow race: it exists on every gateway startup before the first successful `fetchVaultPublicKey` call (1-minute refresh ticker means the first cache population depends on that path succeeding), and can be re-triggered indefinitely if the public-key fetch from nodes fails or times out (10s deadline) — during any such window, every user request reaches the unauthenticated map-insertion path. An attacker needs no credentials, no valid workflow owner, and no JWT — they only need to reach the gateway's JSON-RPC listener and vary `req.ID`. This makes exploitation straightforward and repeatable.

### Recommendation
- Apply rate limiting (e.g. per-IP or per-connection, similar to `WebServer.RateLimit.Unauthenticated`) to unauthenticated `MethodPublicKeyGet` requests before they reach `newActiveRequest`.
- Cap the number of concurrently outstanding unauthenticated `activeRequests` entries (or dedicate a bounded, separate structure for public-key-get bookkeeping instead of the general `activeRequests` map).
- Consider serving `MethodPublicKeyGet` for concurrent unauthenticated callers via a single in-flight coalesced fetch (similar to `singleflight.Group`, as already used in `core/services/gateway/handlers/capabilities/v2/response_cache.go`) rather than creating one `activeRequest` per caller.
- Revisit the comment/assumption in `HandleJSONRPCUserMessage` that caching alone prevents DoS; explicitly handle the "cache not yet populated" and "cache fetch failing" windows.

### Proof of Concept
1. Start (or observe) a gateway Vault handler instance where `cachedMasterPublicKey` is not yet populated (e.g., immediately after startup, or force repeated failures in `fetchVaultPublicKey` by making the node's `secretsService.GetPublicKey` unreachable).
2. As an unauthenticated client, repeatedly send JSON-RPC requests to the gateway with:
```json
{"jsonrpc":"2.0","id":"<unique-value-N>","method":"secrets_getPublicKey","params":{}}
```
varying `<unique-value-N>` on every request (up to 200 chars, e.g., random UUIDs), at a rate exceeding the handler's cleanup ticker (`defaultCleanUpPeriod`) and faster than entries expire (default `requestTimeout` = 30s).
3. Each request enters `HandleJSONRPCUserMessage`, finds `cachedPublicKey == nil`, and calls `newActiveRequest`, adding an entry to `h.activeRequests` with no authentication check.
4. Observe unbounded growth of `h.activeRequests` and associated per-request `responses` maps/callbacks in the gateway process's memory as requests accumulate faster than the reaper removes them.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L280-296)
```go
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L30-34)
```go
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
```

**File:** core/capabilities/vault/validator.go (L123-129)
```go
// ValidateCiphertextSizes checks the owner-scoped ciphertext-size limit for each
// encrypted secret in a write request that already passed structure validation
// (ValidateEncryptedSecretsStructure). It must only be called after
// authorization, with the authorized workflow owner: checking the scoped
// limiter registers a per-owner tenant that spawns a persistent background
// updater, so running it pre-auth would let unauthenticated callers create
// unbounded limiter tenants.
```
