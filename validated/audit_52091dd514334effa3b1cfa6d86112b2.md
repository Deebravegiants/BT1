### Title
Unbounded in-memory `activeRequests` map in Gateway relay/vault handlers allows attacker-driven memory exhaustion DoS - (File: `core/services/gateway/handlers/confidentialrelay/handler.go`)

### Summary
The reported CKB bug class is: a P2P handler marks attacker-controlled identifiers (`tx_hashes`) in an in-memory map with no bound on the number of entries, so a remote peer can flood the node with unique random hashes and exhaust memory — a classic "cache with no size cap, keyed by attacker input" DoS. The same pattern is reproduced in Chainlink's Gateway `confidentialrelay` and `vault` handlers: every incoming user JSON-RPC request creates a new entry in an in-memory `activeRequests` map keyed by the caller-supplied `req.ID`, with no cap on the number of concurrent entries.

### Finding Description
`HandleJSONRPCUserMessage` accepts a caller-supplied request and immediately creates an `activeRequest` entry keyed by `req.ID`: [1](#0-0) 

`newActiveRequest` only checks that the ID isn't already in use — it enforces no limit on the total size of the map: [2](#0-1) 

The only cleanup mechanism is a periodic sweep (`removeExpiredRequests`) that runs once per `defaultCleanUpPeriod` (1s) and removes entries older than `h.requestTimeout` (default 30s): [3](#0-2) [4](#0-3) 

The identical pattern (map keyed by attacker-controlled `req.ID`, duplicate check only, no size cap) exists in the `vault` handler: [5](#0-4) 

This is contrasted with the codebase's own `RequestCache`, used elsewhere in the gateway, which explicitly enforces a `maxCacheSize` and rejects new entries once the cap is reached: [6](#0-5) 

Both `confidentialrelay` and `vault` handlers implement per-node/global rate limiting for *node* responses (`perNodeRateLimiters`, `globalNodeRateLimiter`), but there is no equivalent rate limiter or quota gating the creation of new `activeRequest` entries from the *user*-facing side (`HandleJSONRPCUserMessage`/`newActiveRequest`). A caller only needs to vary `req.ID` (max 200 chars, otherwise unconstrained) to create arbitrarily many concurrent map entries, each holding a copy of the request, per-DON-member response slots, and a mutex, until the 30s timeout sweep runs.

### Impact Explanation
An unprivileged client able to reach the Gateway's confidential-relay or vault JSON-RPC user endpoint can flood it with a high rate of requests using unique random IDs. Each request allocates and retains gateway state for up to the configured `requestTimeout` (default 30s) before the periodic sweep clears it. Sustained flooding can drive unbounded memory growth and increased lock contention on `h.mu`, degrading or crashing the Gateway process, which is shared infrastructure fanning out to DON nodes — affecting all workflows/DONs served by that Gateway instance.

### Likelihood Explanation
Likelihood is moderate-to-high: reaching `HandleJSONRPCUserMessage` requires only crafting a JSON-RPC request with a syntactically valid, unique ID (up to 200 characters) — no proof-of-work, DON quorum, or heavy computation needed to occupy a map slot. Whether upstream JWT/allowlist authentication gates access to these methods before `HandleJSONRPCUserMessage` is invoked was not fully confirmed in the code explored; if authentication is required, exploitation is limited to any already-authenticated but otherwise low-privilege caller (still an unprivileged-actor analog relative to Gateway/DON operators).

### Recommendation
Add a bound on `h.activeRequests` (and the vault handler's equivalent) analogous to `RequestCache.maxCacheSize`, rejecting or rate-limiting new request creation once a configurable cap is reached. Additionally, apply a per-sender/global rate limiter to the user-facing request path (mirroring the existing `perNodeRateLimiters`/`globalNodeRateLimiter` used for node responses) so that request creation, not just node-response processing, is throttled.

### Proof of Concept
1. Obtain (or reuse) valid access to the Gateway's confidential-relay or vault JSON-RPC user endpoint.
2. Send a high-rate stream of `MethodCapabilityExec`/`MethodSecretsGet` (or vault) requests, each with a freshly generated unique `req.ID` (≤200 chars) and never waiting for/consuming the response.
3. Each request creates a persistent `activeRequest` entry in `h.activeRequests` that lives for up to `requestTimeout` (default 30s) before cleanup.
4. Sending requests faster than the 1s sweep interval can reclaim them causes `h.activeRequests` to grow without bound, consuming memory and lock time proportional to attacker request rate — verifiable by observing gateway memory (`h.activeRequests` map length) growing under load in `core/services/gateway/handlers/confidentialrelay/handler.go` / `core/services/gateway/handlers/vault/handler.go`.

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L30-42)
```go
const (
	// defaultCleanUpPeriod is how often expired requests are swept and closed grace
	// windows are forwarded, so it also bounds how far past its deadline a grace
	// window can run.
	defaultCleanUpPeriod = time.Second

	defaultRequestTimeoutSec  = 30
	defaultNodeSendTimeoutSec = 10

	// defaultQuorumGraceMillis bounds the extra wait after quorum is reached. It must
	// stay well below the caller's own HTTP deadline, which is what actually cuts the
	// request short when the DON never produces 2F+1 signed responses.
	defaultQuorumGraceMillis = 10_000
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L300-320)
```go
func (h *handler) Start(_ context.Context) error {
	return h.StartOnce("ConfidentialRelayHandler", func() error {
		h.lggr.Info("starting confidential relay handler")
		go func() {
			ctx, cancel := h.stopCh.NewCtx()
			defer cancel()
			ticker := h.clock.NewTicker(defaultCleanUpPeriod)
			defer ticker.Stop()
			for {
				select {
				case <-ticker.Chan():
					h.forwardGracedRequests(ctx)
					h.removeExpiredRequests(ctx)
				case <-h.stopCh:
					return
				}
			}
		}()
		return nil
	})
}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-411)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	labels := h.extractRequestLabels(req)
	l := h.requestLogger(req, labels)
	l.Debugw("handling confidential relay request", "nodes", len(h.donConfig.Members), "f", h.donConfig.F)

	ar, err := h.newActiveRequest(req, labels, callback)
	if err != nil {
		return err
	}

	return h.fanOutToNodes(ctx, l, ar)
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-430)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		labels:    labels,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
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

**File:** core/services/gateway/handlers/common/requestcache.go (L46-76)
```go
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
	codec := api.JSONRPCCodec{}
	timer := time.AfterFunc(c.timeout, func() {
		err := c.deleteAndSendOnce(key, handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(request), ErrorCode: api.RequestTimeoutError})
		if err != nil {
			lggr.Errorw("failed to send timeout response", "error", err)
		}
	})
	c.cache[key] = &pendingRequest[T]{Callback: callback, responseData: responseData, timeoutTimer: timer}
	return nil
}
```
