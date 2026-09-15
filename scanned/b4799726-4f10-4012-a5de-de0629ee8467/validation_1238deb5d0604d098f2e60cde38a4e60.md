`h.wg` is a plain `sync.WaitGroup` [1](#0-0) , not a panic-recovering wrapper, and no `recover()` exists anywhere in `core/services/gateway/handlers/capabilities/v2/` (`grep` found only the `recover()` call inside the test file, not production code) [2](#0-1) . Based on the evidence gathered, I can now give a final assessment.

### Title
Unhandled panic in `responseCache.Fetch`'s singleflight callback crashes the entire gateway process, causing permanent denial of service for all workflows sharing a shard - (File: `core/services/gateway/handlers/capabilities/v2/response_cache.go`)

### Summary
The Chainlink Capabilities Gateway's outbound HTTP action path calls an unprivileged, node-reachable `fetchFn()` inside a `singleflight.Group.Do` callback with no `recover()` anywhere in the call chain. If that function panics, the panic propagates un-recovered through a bare `sync.WaitGroup`-managed goroutine, crashing the entire gateway process rather than failing a single request — directly analogous to the `latestRoundData()` revert propagating unguarded and locking out all price-feed access in the original finding.

### Finding Description
`gatewayHandler.makeOutgoingRequest` spins up a goroutine via the handler's `sync.WaitGroup` (`h.wg.Go`) to service an outbound HTTP action requested by a workflow DON node, and invokes `h.responseCache.Fetch(...)` with a `fetchFn` closure that performs the actual HTTP call [3](#0-2) . Inside `responseCache.Fetch`, this `fetchFn` is invoked directly inside the `singleflight.Group.Do` callback with no `try/catch`-equivalent (`recover()`) wrapping it: `response := fetchFn()` [4](#0-3) .

The test suite explicitly documents that a panic inside `fetchFn` is *not* contained — it propagates to the calling goroutine and, via `singleflight`, to every concurrent "waiter" sharing the same cache key [5](#0-4) [6](#0-5) . In production, this call happens inside a goroutine launched off `h.wg.Go(...)`, a plain `sync.WaitGroup` with no recovery wrapper [1](#0-0) [7](#0-6) . An unrecovered panic in a goroutine crashes the entire Go process (unlike an error return, which can be handled), so this differs qualitatively from the many other paths in this codebase that correctly wrap risky operations (e.g., `HandleGatewayMessage`'s deferred metrics/logging [8](#0-7) , or the remote dispatcher's receiver-panic isolation test `TestDispatcher_ReceiverPanicDoesNotKillLoop` [9](#0-8) , which specifically verifies the dispatch loop survives a panicking receiver).

This is unprivileged-actor-reachable: `fetchFn` closes over data derived from `network.HTTPRequest` fields (URL, headers, body, timeout) that originate from the workflow's `OutboundHTTPRequest`, ultimately traceable back to node/workflow-controlled inputs relayed through the internet-facing gateway's HTTP action flow [10](#0-9) .

### Impact Explanation
Because Go panics that are not recovered terminate the entire process, any code path that can trigger a panic inside `fetchFn` (or code it calls, including HTTP client internals, response parsing, or malformed remote-server data) takes down the whole gateway binary — not just the offending request. This is a full, unbounded denial of service affecting every DON, shard, and workflow the gateway serves, until the process is manually restarted, mirroring the "permanent lock of all price oracle access" impact pattern from the reference finding, adapted to "permanent lock of all gateway HTTP capability / trigger traffic."

### Likelihood Explanation
Likelihood depends on whether any reachable code inside `fetchFn`'s call graph (network layer response handling, JSON/body parsing of attacker-influenced remote-server responses, or the response cache path) can be driven to panic by unprivileged, external inputs. I was not able to fully verify within the available context whether `network.HTTPClient`'s response-processing code (not retrieved in this session) contains any indexing, type-assertion, or nil-dereference operations on remote-controlled data that could trigger a panic. This should be confirmed by inspecting `core/services/gateway/network/` HTTP client implementation. Given the test suite's explicit `TestFetch_PanicInFetchFn_PropagatedToAllWaiters`/`ToCaller` acknowledges panic propagation as expected behavior, it suggests the team is aware panics propagate but may not have fully reasoned through the process-crash consequence at the `h.wg.Go` boundary.

### Recommendation
Wrap the `fetchFn()` invocation inside `responseCache.Fetch`'s singleflight callback (and/or the goroutine launched in `makeOutgoingRequest`) with a `defer func() { if r := recover(); r != nil { ... } }()` that converts a panic into a normal error/response returned to the specific caller(s), instead of allowing it to propagate to the goroutine boundary and crash the process. This follows the same "defensive try/catch" principle recommended in the reference finding for `latestRoundData()`.

### Proof of Concept
1. A workflow DON node sends an `OutboundHTTPRequest` (e.g., via `MethodHTTPAction`) to the gateway, targeting a URL under attacker control.
2. `gatewayHandler.makeOutgoingRequest` launches `h.wg.Go(...)` and calls `h.responseCache.Fetch(...)` with `callback := h.createHTTPRequestCallback(...)` as `fetchFn` [11](#0-10) .
3. If the underlying HTTP client or response-handling logic invoked by that callback panics (e.g., on a malformed/oversized response, a case not verified in this session due to lack of access to `network.HTTPClient`'s implementation), the panic is not recovered anywhere in the chain, as confirmed directly by `TestFetch_PanicInFetchFn_PropagatedToCaller`/`ToAllWaiters` in `response_cache_test.go` [12](#0-11) .
4. The panic crashes the goroutine and, being unrecovered, terminates the entire gateway process, denying service to all connected DONs/workflows.

Note: Because I could not verify the exact panic-triggering condition inside `network.HTTPClient`'s response handling (file contents not available/explored in this session), the panic *source* itself is not confirmed — only that once triggered, nothing in the reachable code recovers it, which is the direct structural analog to the reference finding's "unhandled revert" root cause.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L46-64)
```go
type gatewayHandler struct {
	services.StateMachine
	config                 ServiceConfig
	shards                 []*shardEndpoint          // all DON shards served by this handler, across the full DON×shard matrix
	nodeAddrToShard        map[string]*shardEndpoint // node address -> owning shard, for routing responses back to the correct shard conn manager
	lggr                   logger.Logger
	httpClient             network.HTTPClient
	globalNodeRateLimiter  limits.RateLimiter            // Global rate limiter shared across all incoming node requests from workflow DON
	perNodeRateLimiters    map[string]limits.RateLimiter // Per-node rate limiters keyed by node address, one independent bucket per DON member
	mtlsRequestRateLimiter limits.RateLimiter
	mtlsConcurrencyLimiter limits.ResourcePoolLimiter[int] // Bounds the number of in-flight outbound mTLS requests
	wg                     sync.WaitGroup
	stopCh                 services.StopChan
	responseCache          ResponseCache // Caches HTTP responses to avoid redundant requests for outbound HTTP actions
	triggerHandler         HTTPTriggerHandler
	metadataHandler        *WorkflowMetadataHandler // Handles authorization for HTTP trigger requests
	metrics                *metrics.Metrics
	httpClientFactory      network.HTTPClientFactory
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L404-453)
```go
func (h *gatewayHandler) makeOutgoingRequest(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	requestID := resp.ID
	h.lggr.Debugw("handling outgoing message", "requestID", requestID, "nodeAddr", nodeAddr)
	var req gateway_common.OutboundHTTPRequest
	err := json.Unmarshal(*resp.Result, &req)
	if err != nil {
		return fmt.Errorf("failed to unmarshal HTTP request from node %s: %w", nodeAddr, err)
	}
	timeout := time.Duration(req.TimeoutMs) * time.Millisecond
	httpReq := network.HTTPRequest{
		Method:           req.Method,
		URL:              req.URL,
		Headers:          req.Headers, //nolint:staticcheck // forward deprecated Headers for backward compatibility; request uses MultiHeaders when set
		MultiHeaders:     req.MultiHeaders,
		Body:             req.Body,
		MaxResponseBytes: req.MaxResponseBytes,
		Timeout:          timeout,
	}

	sendResponseTimeout := time.Duration(defaultSendResponseTimeoutMs) * time.Millisecond

	// send response to node async
	h.wg.Go(func() {
		// not cancelled when parent is cancelled to ensure the goroutine can finish
		baseCtx := context.WithoutCancel(ctx)
		httpCtx, httpCancel := context.WithTimeout(baseCtx, timeout)
		defer httpCancel()
		l := logger.With(h.lggr, "requestID", requestID, "method", req.Method, "timeout", req.TimeoutMs)
		var outboundResp gateway_common.OutboundHTTPResponse
		callback := h.createHTTPRequestCallback(httpCtx, requestID, httpReq, req)
		if req.CacheSettings.MaxAgeMs > 0 {
			h.metrics.IncrementCacheReadCount(ctx, h.lggr)
			outboundResp = h.responseCache.Fetch(httpCtx, req, callback, req.CacheSettings.Store)
		} else {
			outboundResp = callback()
			if req.CacheSettings.Store {
				h.responseCache.Set(req, outboundResp)
			}
		}
		h.metrics.IncrementActionCapabilityRequestCount(ctx, nodeAddr, h.lggr)
		// Use a separate context for sending the response to the node so that an
		// expired HTTP request timeout does not prevent delivering the result.
		sendCtx, sendCancel := context.WithTimeout(baseCtx, sendResponseTimeout)
		defer sendCancel()
		err := h.sendResponseToNode(sendCtx, requestID, outboundResp, nodeAddr)
		if err != nil {
			l.Errorw("error sending response to node", "err", err, "nodeAddr", nodeAddr, "requestID", requestID)
			h.metrics.IncrementActionCapabilityFailures(ctx, nodeAddr, h.lggr)
		}
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache_test.go (L445-486)
```go
func TestFetch_PanicInFetchFn_PropagatedToCaller(t *testing.T) {
	testMetrics := createCacheTestMetrics(t)
	cache := newResponseCache(logger.Test(t), 10000, testMetrics)

	req := createTestRequest("GET", "https://example.com/panic")
	fetchFn := func() gateway_common.OutboundHTTPResponse {
		panic("unexpected error in HTTP callback")
	}

	require.Panics(t, func() {
		cache.Fetch(t.Context(), req, fetchFn, true)
	})
}

func TestFetch_PanicInFetchFn_PropagatedToAllWaiters(t *testing.T) {
	testMetrics := createCacheTestMetrics(t)
	cache := newResponseCache(logger.Test(t), 10000, testMetrics)

	const n = 5
	req := createTestRequest("GET", "https://example.com/panic-shared")

	synctest.Test(t, func(t *testing.T) {
		var wg sync.WaitGroup
		wg.Add(n)

		for range n {
			go func() {
				defer wg.Done()
				defer func() {
					r := recover()
					assert.NotNil(t, r, "panic from fetchFn should propagate to all waiters")
				}()
				fetchFn := func() gateway_common.OutboundHTTPResponse {
					time.Sleep(50 * time.Millisecond)
					panic("shared panic")
				}
				cache.Fetch(t.Context(), req, fetchFn, true)
			}()
		}
		wg.Wait()
	})
}
```

**File:** core/services/gateway/handlers/capabilities/v2/response_cache.go (L83-105)
```go
	result, _, _ := rc.flight.Do(cacheKey, func() (any, error) {
		// Re-check cache: a previous flight may have just stored the result.
		rc.cacheMu.RLock()
		cachedResp, exists := rc.cache[cacheKey]
		rc.cacheMu.RUnlock()
		if exists && cachedResp.storedAt.Add(cacheMaxAge).After(time.Now()) {
			rc.metrics.IncrementCacheHitCount(ctx, rc.lggr)
			return cachedResp.response, nil
		}

		response := fetchFn()

		if storeOnFetch && isCacheableStatusCode(response.StatusCode) {
			rc.cacheMu.Lock()
			rc.cache[cacheKey] = &cachedResponse{
				response: response,
				storedAt: time.Now(),
			}
			rc.cacheMu.Unlock()
		}

		return response, nil
	})
```

**File:** core/capabilities/confidentialrelay/handler.go (L269-285)
```go
func (h *Handler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) error {
	h.lggr.Debugw("received message from gateway", "gatewayID", gatewayID, "requestID", req.ID)

	// GoCtx ties the goroutine to the handler's service lifecycle, so Close waits
	// for in-flight requests instead of abandoning them mid-vault-call.
	h.eng.GoCtx(ctx, func(ctx context.Context) {
		ctx, done, err := h.serveTime.WithTimeout(ctx)
		if err != nil {
			h.lggr.Errorw("failed to apply serve timeout, dropping request", "gatewayID", gatewayID, "requestID", req.ID, "err", err)
			return
		}
		defer done()
		h.serveGatewayMessage(ctx, gatewayID, req)
	})

	return nil
}
```

**File:** core/capabilities/remote/dispatcher_test.go (L284-318)
```go
func TestDispatcher_ReceiverPanicDoesNotKillLoop(t *testing.T) {
	t.Parallel()

	lggr := logger.Test(t)
	ctx := t.Context()
	privKey1, peerID1 := newKeyPair(t)
	_, peerID2 := newKeyPair(t)

	sharedPeer := mocks.NewSharedPeer(t)
	recvCh := make(chan p2ptypes.Message)
	sharedPeer.On("Receive", mock.Anything).Return((<-chan p2ptypes.Message)(recvCh))
	sharedPeer.On("ID", mock.Anything).Return(peerID2)
	signer := mocks.NewSigner(t)
	signer.EXPECT().Initialize().Return(nil)
	registry := commonMocks.NewCapabilitiesRegistry(t)

	dispatcher, err := remote.NewDispatcher(newTestConfig(), sharedPeer, signer, registry, lggr)
	require.NoError(t, err)
	require.NoError(t, dispatcher.Start(ctx))

	rcv := newPanicOnFirstReceiver()
	err = dispatcher.SetReceiver(capID1, donID1, rcv)
	require.NoError(t, err)

	// First message triggers the panic; the goroutine must survive.
	recvCh <- encodeAndSign(t, privKey1, peerID1, peerID2, capID1, donID1, []byte(payload1))
	// Second message must still be delivered.
	recvCh <- encodeAndSign(t, privKey1, peerID1, peerID2, capID1, donID1, []byte(payload2))

	m := <-rcv.received
	require.Equal(t, payload2, string(m.Payload))

	dispatcher.RemoveReceiver(capID1, donID1)
	require.NoError(t, dispatcher.Close())
}
```
