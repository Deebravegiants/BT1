### Title
Unbounded `activeRequests` map growth on the gateway's Vault user-facing handler allows unprivileged clients to exhaust node memory - (File: core/services/gateway/handlers/vault/handler.go)

### Summary
The gateway's Vault `handler` accepts JSON-RPC requests from unprivileged end users via `HandleJSONRPCUserMessage` and, for every accepted request, inserts an entry into an in-memory `activeRequests` map keyed by request ID [1](#0-0) . Unlike the DON-facing `RequestCache` used elsewhere in the gateway, which enforces an explicit `maxCacheSize` and rejects new entries once full [2](#0-1) , this `activeRequests` map has no size cap. Entries are only removed lazily by a periodic `removeExpiredRequests` sweep once `requestTimeout` (default 30s) has elapsed [3](#0-2) [4](#0-3) .

### Finding Description
This is analogous to the OPC UA CVE-2022-29864 class of bug: unbounded per-request state accumulation triggered by unauthenticated/unprivileged client traffic, leading to memory exhaustion (CWE-400).

`HandleJSONRPCUserMessage` performs only lightweight validation before allocating an `activeRequest` object: it checks `req.ID` is non-empty and ≤200 chars, and rejects duplicate IDs, but does not bound the total number of concurrently pending requests [5](#0-4) . For `MethodPublicKeyGet`, which requires no authorization at all, an entry is created directly whenever the public key isn't already cached [6](#0-5) . For the other secrets methods, authorization/validation happens first, but a rejected/failed request never reaches `newActiveRequest` — however, an unprivileged caller can still trivially generate large volumes of *authorized-looking* or *public-key-get* requests (unique random IDs, `MethodPublicKeyGet` needs no auth) that each add a live entry to `activeRequests`, held in memory for the full `requestTimeout` window.

Because `newActiveRequest` only rejects when the *same* ID already exists [1](#0-0) , an attacker simply generates a large number of unique IDs (≤200 chars) to defeat that check. There is no global rate limiter protecting the user-facing path in this handler — only a `nodeRateLimiter` guarding node→gateway responses is present in the struct [7](#0-6) ; the request-validator/limits factory referenced (`RequestValidatorFromLimitsFactory`) bounds request *shape* (e.g., payload/list sizes) but not the count of concurrently pending user requests held in `activeRequests`.

### Impact Explanation
Each `activeRequest` retains the full request object, a responses map, and a callback channel for up to `requestTimeout` seconds (default 30s) [8](#0-7) [4](#0-3) . A high-rate stream of user JSON-RPC requests with unique IDs can grow this map without bound between cleanup passes, consuming gateway-node memory and potentially causing an OOM/crash of the gateway service — a direct availability impact from an unprivileged, internet-facing client, matching the "uncontrolled resource consumption" class of the referenced advisory.

### Likelihood Explanation
The Vault gateway's user-facing HTTP endpoint is designed to accept requests from external/unprivileged clients (that's its purpose), and `MethodPublicKeyGet` needs no authorization while other methods only need a valid allowlist entry/JWT (not attacker-exclusive secrets). Generating unique 200-char-max IDs is trivial, so this requires no special privilege beyond normal client access — the perimeter defenses (`MaxRequestBytes`, per-request field validation) constrain individual message size but do not limit request throughput/pending-count at this handler.

### Recommendation
Add an explicit maximum size check on `h.activeRequests` (mirroring `requestCache.maxCacheSize` in `core/services/gateway/handlers/common/requestcache.go`) inside `newActiveRequest`, rejecting new requests once the cap is reached, and/or add a global/per-sender rate limiter to the user-facing entry point (`HandleJSONRPCUserMessage`) similar to the `NodeRateLimiter` already used for node traffic.

### Proof of Concept
1. Point an unauthenticated/unprivileged client at the gateway's Vault user endpoint.
2. Repeatedly send `MethodPublicKeyGet` (or any allowlisted-but-cheap) JSON-RPC requests, each with a freshly generated unique `ID` (≤200 chars), faster than `requestTimeout` (default 30s) allows cleanup.
3. Observe `handler.activeRequests` grow unbounded in the gateway process, increasing memory usage proportionally to request volume until resource exhaustion/OOM.

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

**File:** core/services/gateway/handlers/vault/handler.go (L394-441)
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

	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
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
