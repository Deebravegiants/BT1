This confirms the code behavior as claimed: there is no per-request-count cap in the HTTP server layer (`MaxRequestBytesLimiter` only limits payload size per request) [1](#0-0) , and the `activeRequests` map in the Vault handler grows unbounded, only cleaned up lazily by the timeout sweep.

Audit Report

## Title
Unbounded `activeRequests` map growth on the gateway's Vault user-facing handler allows unprivileged clients to exhaust node memory - (File: core/services/gateway/handlers/vault/handler.go)

## Summary
The gateway's Vault `handler.HandleJSONRPCUserMessage` accepts JSON-RPC requests from unprivileged end users and, for every accepted request (including unauthenticated `MethodPublicKeyGet` calls), inserts an entry into an in-memory `activeRequests` map keyed by request ID via `newActiveRequest`. [2](#0-1) [3](#0-2)  Unlike `requestCache` in `common/requestcache.go`, which enforces `maxCacheSize` and rejects new entries once full, `handler.activeRequests` has no such cap and entries live for the full `requestTimeout` (default 30s) until the periodic `removeExpiredRequests` sweep runs. [4](#0-3) [5](#0-4) 

## Finding Description
`newActiveRequest` only rejects an insert if the exact same `req.ID` already exists in the map; it performs no check on the total number of entries in `h.activeRequests` before adding a new one. [3](#0-2)  `HandleJSONRPCUserMessage` validates only that `req.ID` is non-empty and ≤200 characters and rejects duplicates — it does not bound request throughput or the number of concurrently pending requests. [6](#0-5)  For `MethodPublicKeyGet`, which requires no authorization at all, a new `activeRequest` is created whenever the public key is not already cached. [7](#0-6)  I confirmed the HTTP transport layer (`network/httpserver.go`) only enforces a per-request payload size limit (`MaxRequestBytesLimiter`/`MaxBytesReader`) and a per-request processing timeout — there is no per-sender or global rate limiter or connection-count cap protecting this endpoint. [1](#0-0)  The only rate limiter present in the handler struct, `nodeRateLimiter`, guards node→gateway traffic, not the user-facing path. [8](#0-7)  This confirms the claim: an unprivileged client can generate unique IDs (trivial, since only duplicates are rejected) to add unbounded live entries to `activeRequests`, each retaining a full request, a responses map, and a callback for up to 30 seconds by default. [9](#0-8) [10](#0-9) 

## Impact Explanation
This is an uncontrolled resource consumption issue (CWE-400): a high-rate stream of user JSON-RPC requests with unique IDs can grow the gateway's in-memory `activeRequests` map without bound between cleanup passes, potentially exhausting gateway memory and crashing/degrading the service. This maps to an in-scope Chainlink impact category as a denial-of-service against the gateway process, degrading availability of the Vault capability for all users of the DON served by that gateway.

## Likelihood Explanation
The Vault gateway's user-facing HTTP endpoint is explicitly designed to accept requests from external/unprivileged clients, and `MethodPublicKeyGet` requires zero authorization while other Vault methods only need a valid allowlist/JWT credential (not attacker-exclusive secrets). Generating unique ≤200-character IDs is trivial and requires no special privilege. The HTTP-layer defenses (`MaxRequestBytesLimiter`) bound only individual message size, not request throughput or pending-request count, so the attack is straightforward and repeatable using ordinary client access to the gateway's public endpoint.

## Recommendation
Add an explicit maximum size check on `h.activeRequests` (mirroring `requestCache.maxCacheSize` in `core/services/gateway/handlers/common/requestcache.go`) inside `newActiveRequest`, rejecting new requests once the cap is reached. Additionally, consider adding a global or per-sender rate limiter on the user-facing entry point (`HandleJSONRPCUserMessage`), analogous to the existing `nodeRateLimiter` used for node-to-gateway traffic.

## Proof of Concept
1. Point an unauthenticated/unprivileged client at the gateway's Vault user HTTP endpoint (`network.HTTPServerConfig.Path` routed to `handler.HandleJSONRPCUserMessage`).
2. Repeatedly send `MethodPublicKeyGet` JSON-RPC requests (no auth required), each with a freshly generated unique `ID` (≤200 chars), at a rate exceeding what `removeExpiredRequests` can clean up within the `requestTimeout` window (default 30s).
3. Instrument/observe `handler.activeRequests` (e.g., via a Go unit test directly calling `newActiveRequest` in a loop with unique IDs and asserting `len(h.activeRequests)` grows without bound) to demonstrate unbounded memory growth proportional to request volume.

### Citations

**File:** core/services/gateway/network/httpserver.go (L211-224)
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
```

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

**File:** core/services/gateway/handlers/vault/handler.go (L147-148)
```go
	nodeRateLimiter *ratelimit.RateLimiter
	requestTimeout  time.Duration
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
