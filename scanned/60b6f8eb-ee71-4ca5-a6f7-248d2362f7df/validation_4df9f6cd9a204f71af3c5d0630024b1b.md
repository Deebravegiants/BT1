### Title
Unauthenticated `MethodPublicKeyGet` requests allow unbounded growth of the Vault gateway handler's `activeRequests` map, causing memory exhaustion and lock-contention DoS - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The Vault gateway handler's `HandleJSONRPCUserMessage` explicitly bypasses authorization and rate-limiting for `vaulttypes.MethodPublicKeyGet` requests, and unconditionally inserts a new entry into the shared `h.activeRequests` map (keyed by attacker-controlled `req.ID`) whenever the public key is not already cached. An unauthenticated, unprivileged internet-facing client can flood this endpoint with unique request IDs, growing `activeRequests` without bound, similar in spirit to the reported unbounded-array iteration DoS pattern, except here the vector is an unbounded map fed continuously by unauthenticated requests and periodically swept under a shared mutex that also guards all other request processing (including legitimate, authorized secret operations).

### Finding Description
`HandleJSONRPCUserMessage` short-circuits authorization for public key requests: [1](#0-0) 

When the public key is not cached, it calls `h.newActiveRequest(req, callback)` directly, with no authorization check, no per-caller rate limiting, and only a size check on `req.ID` (`len(req.ID) > 200`), which does not bound the number of distinct IDs an attacker can send: [2](#0-1) 

`newActiveRequest` takes the handler-wide lock and inserts unconditionally as long as the `req.ID` is not a duplicate that is still pending: [3](#0-2) 

Because `req.ID` is attacker-controlled and easily made unique per call, this insertion path admits unbounded numbers of entries into `h.activeRequests` bounded only by the periodic sweep's timeout window (`requestTimeout`), not by any cap on total pending entries or by identity/authorization of the caller.

The sweep function that reclaims expired entries is O(n) over the entire map and is invoked periodically while holding `h.mu`: [4](#0-3) 

`h.mu` is the same lock guarding every other operation on the handler — `newActiveRequest` (`Lock`), `getActiveRequest` (`RLock`), and `HandleNodeMessage`'s active-request lookups for *all* users, including legitimate authorized secret Create/Update/Delete/List operations: [5](#0-4) 

If an attacker keeps `activeRequests` large (by sustaining a flood of unique unauthenticated `PublicKeyGet` requests faster than the timeout drains them), every periodic sweep becomes increasingly expensive while holding the shared mutex, and the growing map itself increases memory pressure. Both effects degrade or block processing of legitimate authorized Vault requests from other users/workflows on the same gateway/DON, which is the core denial-of-service pattern highlighted in the reported bug class (an unbounded, attacker-influenced collection iterated/processed in a way that can exhaust resources and halt normal operation) — here mapped onto the internet-facing gateway's caches/handlers rather than an on-chain array.

### Impact Explanation
This is reachable by any unauthenticated actor able to reach the gateway's Vault JSON-RPC endpoint, since `PublicKeyGet` is explicitly exempted from authorization. Sustained abuse can:
- Exhaust gateway node memory via unbounded `activeRequests` growth.
- Cause lock contention on `h.mu` during the periodic `removeExpiredRequests` sweep, delaying or blocking legitimate authorized users' `HandleJSONRPCUserMessage`/`HandleNodeMessage` calls that also need `h.mu`.
- Degrade service availability for the entire Vault handler instance (shared across all authorized workflow owners on that DON), not just the attacker.

This does not directly leak secrets or bypass authorization for secret data — it is a service-availability issue confined to the Vault gateway handler.

### Likelihood Explanation
Likelihood is moderate-to-high: no authentication, no per-request-ID limiting beyond a 200-character length check, and no apparent additional gateway-level per-IP/per-connection rate limiter was found guarding this specific handler path in the reviewed files. The only natural bound is the periodic expiry sweep (`requestTimeout`), which an attacker can outpace with a sufficiently fast request rate.

### Recommendation
- Apply a rate limiter (per-IP/per-connection, similar to `nodeRateLimiter` used elsewhere in the handler) to inbound `HandleJSONRPCUserMessage` calls, including `PublicKeyGet`, before any `activeRequests` insertion.
- Enforce a maximum size on `h.activeRequests` (reject or shed new unauthenticated requests once a cap is reached).
- Avoid taking a global lock shared with authorized-request processing for the periodic sweep of unauthenticated public-key requests; consider isolating unauthenticated request bookkeeping from the authorized request path, or use a separate/sharded lock and cache with its own bounded queue for `PublicKeyGet` misses.

### Proof of Concept
1. Attacker sends repeated JSON-RPC `PublicKeyGet` requests to the gateway's Vault handler, each with a unique `req.ID` (e.g., random UUID), while the handler's cached public key is empty or invalidated.
2. Each call reaches `HandleJSONRPCUserMessage` → since `req.Method == vaulttypes.MethodPublicKeyGet` and no cached key is available, `h.newActiveRequest(req, callback)` is invoked without authorization.
3. Each unique `req.ID` creates a new entry in `h.activeRequests`; repeating rapidly (faster than `requestTimeout`) grows the map without bound.
4. Concurrently, `removeExpiredRequests` (invoked periodically) must scan the entire growing map under `h.mu.RLock()`, and any legitimate authorized request calling `newActiveRequest`/`getActiveRequest`/`HandleNodeMessage` contends on the same `h.mu`, causing increasing latency/availability degradation for all users of that Vault gateway handler instance.

*Note: I was unable to verify from the indexed files whether an additional connection-level or IP-based rate limiter exists upstream in the gateway's HTTP/WS transport layer (outside the handler package) that might mitigate this before requests reach `HandleJSONRPCUserMessage`. If such a limiter exists and is sufficiently strict, it would reduce the practical severity of this finding. Confirming this would require inspecting the full gateway connection/transport code, which is recommended before treating this as fully exploitable in production configuration.*

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L134-160)
```go
type handler struct {
	services.StateMachine
	methodConfig     Config
	donConfig        *config.DONConfig
	don              gwhandlers.DON
	lggr             logger.Logger
	codec            api.JSONRPCCodec
	mu               sync.RWMutex
	stopCh           services.StopChan
	authorizer       vaultcap.Authorizer
	jwtAuth          services.Service
	requestProcessor *vaultcap.GatewayVaultRequestProcessor

	nodeRateLimiter *ratelimit.RateLimiter
	requestTimeout  time.Duration

	writeMethodsEnabled limits.GateLimiter
	activeRequests      map[string]*activeRequest
	metrics             *metrics

	aggregator aggregator

	cachedPublicKeyGetResponse []byte
	cachedPublicKeyObject      *tdh2easy.PublicKey

	clock clockwork.Clock
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
