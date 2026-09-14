### Title
Unauthenticated user-facing gateway request path lets any client exhaust memory via unbounded `activeRequests` accumulation - ([File: core/services/gateway/handlers/confidentialrelay/handler.go])

### Summary
The `ConfidentialRelayHandler.HandleJSONRPCUserMessage` and the Vault gateway handler's `MethodPublicKeyGet` path both create an in-memory `activeRequest` entry, keyed by the caller-supplied request ID, for every incoming user request — before any per-user rate limiting or (in the public-key case) any authentication at all. Entries are only cleaned up on a periodic sweep bounded by a fixed request timeout. An unprivileged client that submits many requests with unique IDs faster than the timeout/sweep interval can retire them can grow these maps without bound, exhausting gateway memory — the same accumulation-of-in-flight-object DoS pattern described in CVE-2020-14297.

### Finding Description
`gateway.ProcessRequest` decodes an incoming user JSON-RPC request and, for non-legacy requests, calls `h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)` directly [1](#0-0) . The only bound applied at this layer is a 200-character cap on the request ID string [2](#0-1) ; there is no per-caller or global request-creation rate limiter before the handler is invoked.

In `confidentialrelay/handler.go`, `HandleJSONRPCUserMessage` validates only the ID length, then unconditionally calls `h.newActiveRequest(req, labels, callback)`, which inserts a new `*activeRequest` into `h.activeRequests` keyed by the caller-supplied `req.ID` [3](#0-2) , [4](#0-3) . The `perNodeRateLimiters` / `globalNodeRateLimiter` fields on this handler only gate *node* responses in `HandleNodeMessage`, not the initial user request that creates the map entry [5](#0-4) . Cleanup only happens once per `defaultCleanUpPeriod` (1s) via `removeExpiredRequests`, which removes entries whose `createdAt` is older than `requestTimeout` (default 30s) [6](#0-5) , [7](#0-6) . Each request also fans out to every DON member (`h.fanOutToNodes`) before it can complete, so live entries also drive outbound network work to the relay DON while accumulating.

The Vault gateway handler exhibits an even more directly unauthenticated variant: `MethodPublicKeyGet` explicitly bypasses authorization ("Public key requests don't require authorization") and, on a cache miss, creates a new `activeRequest` and fans out to nodes with no rate limiting on the *creation* path [8](#0-7) . The comment "we cache this value quite aggressively so don't need to worry about DoS" assumes the cache is always warm; on a cold cache (startup, cache eviction, or if the cached-key check races), every request instead creates a fresh tracked object.

This mirrors the CVE-2020-14297 bug class: unprivileged, externally-reachable requests cause server-side objects (EJB transaction objects there; `activeRequest` entries here) to accumulate faster than they are reaped, exhausting memory/resources and degrading or crashing the service — a resource-exhaustion DoS reachable from an unauthenticated/unprivileged actor.

### Impact Explanation
An external, unauthenticated actor can call the gateway's user-facing HTTP port with a flood of JSON-RPC requests using unique `id` values (up to 200 chars, effectively unlimited cardinality) for `MethodSecretsGet`/`MethodCapabilityExec` (confidential relay) or `MethodPublicKeyGet` (vault, on cache miss). Each request allocates a map entry, a `sync.Mutex`, a `responses` map, and triggers a fan-out goroutine/write to every DON node, before any authorization or rate limiting applies to the request-creation step. Sustained above the 1-request-per-second sweep/30-second-TTL reclaim rate, this grows `activeRequests` unbounded, consuming gateway memory and node-write bandwidth, and can degrade or crash the gateway process — denial of service, matching CVSS availability impact (A:H) of the referenced advisory.

### Likelihood Explanation
High. The user-facing gateway endpoint is designed to be internet-facing; `ProcessRequest` performs essentially no admission control before invoking the handler, and the confidential-relay handler applies zero limiting on request creation (only on subsequent node responses). No credentials or special role are required to reach `HandleJSONRPCUserMessage`; the vault `MethodPublicKeyGet` path is explicitly documented as unauthenticated. Generating unique, valid-looking JSON-RPC IDs and firing requests faster than 1/sec (the default sweep rate) is trivial for a single unprivileged client.

### Recommendation
Add admission control at (or before) `HandleJSONRPCUserMessage`/`newActiveRequest` for both handlers: enforce a global and per-source cap/rate limit on the number of concurrently tracked `activeRequests` prior to allocation (not just on node responses), reject new requests once a configured ceiling is reached, and consider bounding by source IP/API key in addition to request count. For the Vault `MethodPublicKeyGet` path, apply a lightweight rate limiter on the cache-miss branch specifically, since it is reachable without authorization. Reduce `defaultCleanUpPeriod`/`requestTimeout` exposure or make the sweep proportional to load, and add a metric/alert on `len(activeRequests)` to detect abuse in production.

### Proof of Concept
1. Configure a gateway with the confidential-relay (or vault) handler enabled on its user-facing HTTP port.
2. From an unauthenticated client, send a tight loop of JSON-RPC requests to the gateway's user endpoint for `MethodSecretsGet` (or `MethodCapabilityExec`), each with a unique `id` (e.g., UUID) and otherwise arbitrary/garbage params — no auth token or DON-node credentials required to reach `HandleJSONRPCUserMessage`.
3. Send requests at a rate exceeding `1/defaultCleanUpPeriod` reclaim capacity (e.g., hundreds per second) for longer than `requestTimeout` (default 30s).
4. Observe `h.activeRequests` (confidentialrelay/handler.go) growing without bound in gateway memory/heap profiles, along with continuous fan-out writes to all DON members for each abandoned entry, degrading gateway responsiveness/availability. The same can be reproduced against the vault handler's `MethodPublicKeyGet` on a cold public-key cache.

Note: I could not fully verify whether an additional upstream HTTP-level rate limiter exists in `network/httpserver.go` that might mitigate this at the transport layer (that file was only partially inspected); if such a limiter is per-IP and sufficiently strict, it would reduce but likely not eliminate the exposure given how trivially requests can be distributed across source IPs or bursted before rate-limit windows engage.

### Citations

**File:** core/services/gateway/gateway.go (L231-234)
```go
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
```

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L337-370)
```go
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
		l := h.requestLogger(er.req, er.labels)
		l.Debugw("request expired, evaluating collected relay responses",
			"collected", len(responses),
			"nodes", len(h.donConfig.Members),
			"unanswered", len(h.donConfig.Members)-len(responses),
		)
		summary, err := h.bundler.Bundle(er.req, responses, l)
		if err != nil {
			l.Errorw("failed to build relay response bundle", "error", err)
			if sendErr := h.sendResponseAndClearRequest(ctx, er, h.constructErrorResponse(er.req, api.FatalError, err)); sendErr != nil {
				l.Errorw("error returning bundle failure on expiry", "error", sendErr)
			}
			continue
		}
		// Expiry makes further responses unavailable to this request. The common
		// readiness path forwards a viable partial bundle or returns a timeout.
		if err := h.forwardBundleOrTerminateIfReady(ctx, l, er, summary, 0, true); err != nil {
			l.Errorw("error forwarding bundle on expiry", "error", err)
		}
	}
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L438-453)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	l := logger.With(h.lggr, "method", resp.Method, "requestID", resp.ID, "nodeAddr", nodeAddr)
	l.Debugw("handling node response")

	nodeRateLimiter, ok := h.perNodeRateLimiters[nodeAddr]
	if !ok {
		return fmt.Errorf("received message from unexpected node %s", nodeAddr)
	}
	if !nodeRateLimiter.Allow(ctx) {
		l.Debugw("node is rate limited", "nodeAddr", nodeAddr)
		return nil
	}
	if !h.globalNodeRateLimiter.Allow(ctx) {
		l.Debug("global relay rate limit exceeded")
		return nil
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
