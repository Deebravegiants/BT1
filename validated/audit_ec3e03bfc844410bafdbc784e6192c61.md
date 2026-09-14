Confirming the analysis: the confidential relay gateway handler's `activeRequests` map has no size cap, unlike the sibling `requestCache[T]` in `core/services/gateway/handlers/common/requestcache.go` which explicitly enforces `maxCacheSize`. This matches the Netty `HttpPostRequestDecoder` bug class: an unbounded, unprivileged-client-controlled accumulation structure that grows without a hard limit until periodic (not synchronous) cleanup runs.

### Title
Unbounded accumulation of per-request state in confidential relay gateway handler enables memory-exhaustion DoS - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
The confidential relay gateway's `HandleJSONRPCUserMessage` path creates an entry in `h.activeRequests` for every distinct incoming JSON-RPC request ID, with no cap on the number of concurrently tracked requests, mirroring the netty-http-codec class of bug where a decoder accumulates unbounded per-request state (fields/list entries) supplied by an unprivileged client.

### Finding Description
`HandleJSONRPCUserMessage` calls `h.newActiveRequest`, which only rejects a request if its exact `req.ID` already exists in the map — it enforces no bound on the total number of entries in `h.activeRequests`: [1](#0-0) 

Each accepted request stays in the map until either the periodic cleanup goroutine — which only runs once per `defaultCleanUpPeriod` (1 second) and removes entries only after `requestTimeout` (default 30 seconds) has elapsed — sweeps it, or the request completes: [2](#0-1) [3](#0-2) 

An unprivileged caller sends requests through the gateway HTTP server, which only bounds the size of a single request body (`MaxRequestBytesLimiter`/`MaxBytesReader`), not the number of distinct requests or resulting server-side state: [4](#0-3) 

Each `activeRequest` additionally holds a `responses map[string]*jsonrpc.Response[json.RawMessage]` that is populated as DON nodes reply, so per-entry memory grows with `len(donConfig.Members)` as well: [5](#0-4) 

This is architecturally inconsistent with the sibling generic request-tracking primitive `requestCache[T]` used by other gateway handlers, which explicitly enforces `maxCacheSize` and rejects new entries once full: [6](#0-5) 

No equivalent `maxCacheSize`/count-based rejection exists for `h.activeRequests` in the confidential relay handler.

### Impact Explanation
Since each unique JSON-RPC request ID from an unprivileged (but otherwise authenticated-per-request, JWT/signature model aside) client creates a new heap-resident `activeRequest` entry that survives for up to `RequestTimeoutSec` (default 30s) regardless of size limits, a caller able to submit many distinct requests within that window (bounded only by HTTP throughput, not by the handler) can drive unbounded growth of `h.activeRequests`, consuming gateway node memory and potentially causing OOM/availability loss for the gateway process — consistent with CWE-770 (Allocation of Resources Without Limits or Throttling), matching the bug class in the reported netty advisory (unbounded accumulation of decoder state driven by attacker-controlled request volume).

### Likelihood Explanation
The gateway HTTP server enforces per-request body size limits but not a limit on the number of concurrently in-flight/tracked requests reaching this handler; there is no visible global concurrency cap or per-sender rate limiter gating entry into `newActiveRequest` before the map insert. Reaching this path requires only sending well-formed JSON-RPC requests with unique IDs to the confidential relay methods (`MethodSecretsGet`, `MethodCapabilityExec`) faster than the 30-second timeout clears them, which is realistic for a scripted client and does not require any privileged role.

### Recommendation
Add an explicit maximum-size guard to `h.activeRequests` (analogous to `requestCache[T].maxCacheSize`) and reject new requests with a clear error (e.g., `429`/`RequestTimeoutError`) once the cap is reached, and/or apply a global or per-sender rate limiter ahead of `newActiveRequest` to bound the rate at which new tracked requests can be created.

### Proof of Concept
1. Configure a confidential relay handler with `RequestTimeoutSec` at or near its default (30s).
2. As an unprivileged client, repeatedly submit `HandleJSONRPCUserMessage`-routed JSON-RPC requests (e.g., `MethodSecretsGet`) with distinct, randomly generated request IDs, faster than the 1-second cleanup tick can expire them relative to the 30-second timeout.
3. Observe `h.activeRequests` (and its nested `responses` maps) grow without bound in proportion to request volume, since `newActiveRequest` only rejects duplicate IDs, never a size cap — driving increasing gateway memory usage until resource exhaustion.

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L110-126)
```go
type activeRequest struct {
	req       jsonrpc.Request[json.RawMessage]
	labels    requestLabels
	responses map[string]*jsonrpc.Response[json.RawMessage]
	mu        sync.Mutex
	completed atomic.Bool

	// graceStarted is set the first time the request holds F+1 signed responses, so
	// the grace deadline is armed once per request rather than moved forward by every
	// later response. graceDeadline is guarded by mu and is only meaningful once
	// graceStarted is set.
	graceStarted  atomic.Bool
	graceDeadline time.Time

	createdAt time.Time
	gwhandlers.Callback
}
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
