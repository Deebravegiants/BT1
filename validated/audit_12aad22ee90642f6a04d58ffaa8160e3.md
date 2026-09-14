### Title
Unbounded per-request memory allocation in the internet-facing Confidential Relay gateway handler via unauthenticated `HandleJSONRPCUserMessage` - (File: core/services/gateway/handlers/confidentialrelay/handler.go)

### Summary
The Xen CVE-2022-42318 describes xenstored allowing unprivileged guests to exhaust memory by issuing requests/watches faster than the server bounds or reclaims them. The chainlink gateway's Confidential Relay handler has an analogous pattern: every JSON-RPC user request creates a new heap-resident `activeRequest` entry keyed by an attacker-chosen `req.ID`, with no rate limiter or authorization gate on entry creation and only a periodic (1s) time-based sweep as the sole reclamation mechanism.

### Finding Description
`HandleJSONRPCUserMessage` in the Confidential Relay handler is the entry point for gateway-facing (internet-facing, unauthenticated at this layer) user messages: [1](#0-0) 

For every request it accepts, it calls `newActiveRequest`, which locks the handler mutex and unconditionally inserts a new `*activeRequest` (containing a `responses` map and other fields) into `h.activeRequests`, keyed only by the caller-supplied `req.ID`: [2](#0-1) 

The only validation before insertion is that `req.ID` is non-empty and ≤200 characters: [3](#0-2) 

Critically, the `globalNodeRateLimiter` and `perNodeRateLimiters` that exist on this handler are only consulted in `HandleNodeMessage` (responses coming back from DON nodes), not in `HandleJSONRPCUserMessage` (the inbound user-facing path): [4](#0-3) 

Reclamation of these entries relies solely on a background goroutine that runs once per second and removes entries older than `requestTimeout` (default 30s): [5](#0-4) [6](#0-5) 

As long as an attacker submits requests with unique IDs faster than the 30-second timeout window drains them, `h.activeRequests` grows without any hard cap, each entry also triggering a `fanOutToNodes` fan-out goroutine per DON member via `errgroup`: [7](#0-6) 

This mirrors the Xen advisory's root cause: no limiter on the count of concurrent, memory-holding state entries created directly by an unprivileged caller, with only time-based (not count-based) eviction.

### Impact Explanation
An unauthenticated client of the gateway's JSON-RPC endpoint routed to the Confidential Relay handler can drive unbounded growth of `h.activeRequests` and concurrent per-request goroutines/timers by submitting a high rate of distinct request IDs, causing memory exhaustion and Denial of Service of the gateway process — consistent with the CVSS 3.1 `AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H` (availability-only, no privilege beyond an unprivileged request) profile of the analog.

### Likelihood Explanation
The gateway's `ProcessRequest` entry point performs only ID-length and structural checks before dispatching to the handler (`core/services/gateway/gateway.go`, seen in earlier context), and this handler's request-creation path has no per-caller/global rate limiter, no cap on `len(h.activeRequests)`, and no authentication requirement prior to state allocation. A remote, unauthenticated actor can trigger this with ordinary HTTP requests, making likelihood high assuming this handler is reachable without upstream mitigations (e.g., an external WAF or reverse-proxy rate limit) — I could not fully verify whether such infrastructure-level protections exist outside the repository, since that is outside the scope of the codebase.

### Recommendation
Add a per-caller and/or global rate limiter (or a bounded semaphore on `len(h.activeRequests)`) in `HandleJSONRPCUserMessage` before calling `newActiveRequest`, similar to the `globalNodeRateLimiter`/`perNodeRateLimiters` already used for node responses, and reject or backpressure requests once a configurable in-flight-request ceiling is reached.

### Proof of Concept
1. An unauthenticated client sends a rapid stream of valid JSON-RPC requests to the gateway's confidential-relay-routed endpoint, each with a unique `id` field (≤200 chars) and method `MethodSecretsGet`/`MethodCapabilityExec`.
2. Each request causes `HandleJSONRPCUserMessage` → `newActiveRequest` to allocate a new map entry plus spawn per-DON-member send goroutines in `fanOutToNodes`, all persisting for up to `requestTimeout` (default 30s).
3. If the attacker sustains a rate exceeding what the 1-second cleanup ticker can reclaim, `h.activeRequests` and associated goroutines grow unbounded, exhausting gateway memory/CPU and denying service to legitimate DON traffic.

Note: I could not verify from the indexed codebase whether an external layer (load balancer, ingress rate limiting, or the HTTP server config in `core/services/gateway/network/httpserver.go`) mitigates this at a level outside this handler; if such mitigations exist, they should be confirmed by a Devin session with full repository access, since index size limits may have excluded some relevant file contents.

### Citations

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L394-412)
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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L686-710)
```go
func (h *handler) fanOutToNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var (
		group      errgroup.Group
		nodeErrors atomic.Uint32
	)

	// Each send is bounded independently. A node whose websocket accepts no writes blocks
	// until its context is cancelled, and because the caller only reads the response callback
	// after this function returns, an unbounded send would hold the request open until the
	// client gives up, discarding a bundle that already reached quorum.
	sendCtx, cancel := context.WithTimeout(ctx, h.nodeSendTimeout)
	defer cancel()

	for _, node := range h.donConfig.Members {
		group.Go(func() error {
			err := h.don.SendToNode(sendCtx, node.Address, &ar.req)
			if err != nil {
				nodeErrors.Add(1)
				l.Errorw("error sending request to node", "node", node.Address, "error", err)
			}
			return nil
		})
	}

	_ = group.Wait()
```
