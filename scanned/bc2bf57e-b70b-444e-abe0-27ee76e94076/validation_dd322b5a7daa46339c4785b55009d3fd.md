### Title
Unbounded `activeRequests` map growth in Vault/ConfidentialRelay gateway handlers enables memory-exhaustion DoS from unprivileged gateway clients - ([File: core/services/gateway/handlers/vault/handler.go])

### Summary
The gateway's Vault and ConfidentialRelay JSON-RPC handlers register a new in-memory `activeRequest` entry for every incoming user request, keyed by attacker-supplied `req.ID`, with **no maximum count or aggregate-size check** at insertion time — the only cleanup mechanism is a periodic, time-based reaper. This mirrors the Wazuh `div_msg_box` root cause: fragments/entries accumulate under attacker-chosen keys with no bound on count or aggregate size, relying solely on time-based expiry rather than an admission limit.

### Finding Description
`newActiveRequest` in the Vault gateway handler inserts a new map entry for every unique `req.ID` supplied by the calling client, guarded only by a duplicate-ID check — not a cache-size limit: [1](#0-0) 

The identical unbounded pattern exists in the ConfidentialRelay gateway handler: [2](#0-1) 

The only mitigation is a periodic sweep that removes entries older than `requestTimeout`: [3](#0-2) [4](#0-3) 

This is the same bug class as the Wazuh CVE: `div_msg_box`/`in_str` accumulate attacker-controlled entries with no maximum count/aggregate-size limit, relying only on eventual timeout/expiration for cleanup — during the window before expiry, an attacker can register requests faster than the timeout clears them, growing the map (and each `activeRequest.responses` map, `req.Params json.RawMessage`, and associated `Callback`) without bound.

By contrast, the sibling `RequestCache` used by the WebAPI/Capabilities handler explicitly enforces a `maxCacheSize` at admission time before inserting into the map: [5](#0-4) 

This shows the codebase's own established mitigation pattern (admission-time size cap) is not applied consistently to the Vault and ConfidentialRelay handlers' `activeRequests` maps.

### Impact Explanation
An unprivileged/authenticated gateway client can call `HandleJSONRPCUserMessage` repeatedly with distinct request IDs faster than `requestTimeout` elapses (default `defaultCleanUpPeriod` cadence for the reaper, with a longer per-request timeout window), causing `h.activeRequests` to grow unbounded in memory. Each entry retains the full JSON-RPC request payload and a `Callback`, so with enough concurrent/rapid submissions this can exhaust gateway memory, disrupting the Vault/ConfidentialRelay JSON-RPC service and potentially the whole gateway process, affecting all DON members and users relying on it — a availability impact analogous to the Wazuh cluster master DoS.

### Likelihood Explanation
The `HandleJSONRPCUserMessage` entrypoint is the standard gateway-facing route for external client requests (not a privileged/node-only path), and request-ID uniqueness plus timeout windows are entirely attacker-controlled. There is no per-client quota or global cap on `len(activeRequests)`, only per-node rate limiting on the *node response* path — the *client request admission* path (`newActiveRequest`) has no such gate visible in the reviewed code.

### Recommendation
Add an admission-time maximum size check (mirroring `requestCache.NewRequest`'s `len(c.cache) >= int(c.maxCacheSize)` guard) to `newActiveRequest` in both `core/services/gateway/handlers/vault/handler.go` and `core/services/gateway/handlers/confidentialrelay/handler.go`, rejecting new requests once a configurable maximum pending-request count (and/or aggregate payload byte budget) is reached, in addition to the existing TTL-based reaper.

### Proof of Concept
1. An authenticated gateway client repeatedly calls the Vault (or ConfidentialRelay) JSON-RPC endpoint with unique `req.ID` values (e.g., UUIDs) at a rate exceeding what `removeExpiredRequests` can reap within `requestTimeout`.
2. Each call reaches `newActiveRequest`, which unconditionally inserts into `h.activeRequests` since there is no size check comparable to `requestCache.maxCacheSize`. [1](#0-0) 
3. Sustained submission accumulates a large number of live entries (each holding request payload + response map + callback) until the reaper's `requestTimeout` window elapses, growing gateway process memory in proportion to submission rate, eventually causing memory pressure/OOM on the gateway node.

### Citations

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

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L337-369)
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
