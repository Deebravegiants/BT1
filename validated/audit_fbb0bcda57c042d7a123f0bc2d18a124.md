## Title
Quadratic-time PEM parsing of attacker-controlled mTLS credentials bypasses the gateway's mTLS rate limiter, enabling a CPU-amplification DoS - (File: `core/services/gateway/handlers/capabilities/v2/http_handler.go`)

### Summary
The Chainlink Gateway's outbound HTTP Action mTLS path parses attacker-supplied `Certificate`/`PrivateKey` bytes with `tls.X509KeyPair`, which internally relies on `encoding/pem.Decode`. The CVE hint (GO-2025-4009 / CVE-2025-61723) documents that some malformed PEM inputs make `pem.Decode` scale non-linearly (quadratically) with input size. In this codebase that parsing step runs **before** the dedicated `mtlsRequestRateLimiter` check, and a test explicitly documents/asserts that failed parses do not consume (or even check) that rate limiter — meaning the expensive parse itself is exempt from the quota control designed to bound this exact attack surface.

### Finding Description
`gatewayHandler.send` forwards the `Mtls` fields of an `OutboundHTTPRequest` — which the code comments themselves note come from "untrusted nodes" carrying user/workflow supplied data — directly into the HTTP client factory: [1](#0-0) 

`httpClientFactory` resolves to `network.NewHTTPClient`, which calls `tls.X509KeyPair(config.Mtls.Certificate, config.Mtls.PrivateKey)` synchronously, before any mTLS-specific throttling occurs: [2](#0-1) 

Critically, in `send`, `h.mtlsRequestRateLimiter.Allow(ctx)` is only reached **after** `h.httpClientFactory(...)` returns successfully; if parsing the attacker-supplied cert/key fails, the function returns from the `err != nil` branch before the rate limiter is ever consulted: [3](#0-2) 

This is confirmed by the test suite itself, which explicitly asserts that an invalid-cert request does **not** consume (and is not blocked by) the global mTLS token bucket: [4](#0-3) 

The only remaining throttle on this path is the generic per-node/global node-message rate limiter applied at the top of `HandleNodeMessage`, which limits overall message *count*, not per-call CPU cost: [5](#0-4) 

Because the mTLS-specific quota is bypassed precisely on the failure path that a malicious/invalid PEM payload would trigger, an attacker who can drive `OutboundHTTPRequest.Mtls` (e.g. via a workflow's HTTP Action capability configured with `Mtls`) can repeatedly submit crafted PEM blobs engineered to trigger `pem.Decode`'s non-linear parsing behavior, forcing the gateway to spend disproportionate CPU time on each request while evading the control that was specifically built to bound this cost.

### Impact Explanation
This is a quota/rate-limit bypass (the `mtlsRequestRateLimiter` control is documented and tested to skip invalid-cert requests) combined with a CPU-amplification primitive from the underlying PEM parser. Repeated exploitation can degrade or exhaust gateway worker resources handling `MethodHTTPAction` node messages, affecting availability for all workflows sharing that gateway/DON shard.

### Likelihood Explanation
Likelihood is bounded but non-trivial: the payload is still limited by the configured max request size (e.g. `MaxRequestBytes = 10_000` in `core/scripts/gateway/sample_config_tls.toml`) and by the generic per-node/global node-message rate limiters, so a single request cannot be arbitrarily large, and message throughput is still capped. However, since the parsing step is explicitly exempt from the mTLS-specific quota by design (per the cited test and code ordering), an attacker gets more "free" expensive parses than the mTLS control was intended to allow, amplifying achievable CPU cost per unit of throttled request budget.

### Recommendation
- Cap/validate the size and structure of `Mtls.Certificate`/`Mtls.PrivateKey` before calling `tls.X509KeyPair`, independent of the general `MaxRequestBytes` limit.
- Consume (or at least check) the `mtlsRequestRateLimiter` token before invoking the client factory/parsing step, not only after a successful parse, so malformed-cert requests are throttled like valid ones.
- Ensure the Go toolchain used to build Chainlink is >=1.25.2 (or otherwise unaffected) to pick up the upstream `encoding/pem` fix (GO-2025-4009).

### Proof of Concept
1. A workflow/node submits repeated `MethodHTTPAction` node messages with `OutboundHTTPRequest.Mtls.Certificate` / `PrivateKey` set to a crafted, malformed PEM payload sized to maximize `pem.Decode`'s non-linear cost within `MaxRequestBytes`.
2. Each request causes `gatewayHandler.send` → `httpClientFactory` → `tls.X509KeyPair` to run the expensive parse; since parsing fails, `mtlsRequestRateLimiter.Allow` is never reached/consumed (per `TestGatewayHandler_Send_InvalidMtlsCertDoesNotConsumeGlobalTokens`).
3. Only the coarse per-node/global node-message rate limiter in `HandleNodeMessage` bounds request frequency, allowing sustained CPU-costly parsing calls that the mTLS-specific quota was meant to prevent. [6](#0-5)

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L239-255)
```go
func (h *gatewayHandler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	if resp.ID == "" {
		return fmt.Errorf("received response with empty request ID from node %s", nodeAddr)
	}
	h.lggr.Debugw("handling incoming node message", "requestID", resp.ID, "nodeAddr", nodeAddr)
	nodeRateLimiter, ok := h.perNodeRateLimiters[nodeAddr]
	if !ok {
		return fmt.Errorf("received message from unexpected node %s", nodeAddr)
	}
	if !nodeRateLimiter.Allow(ctx) {
		h.metrics.IncrementCapabilityNodeThrottled(ctx, nodeAddr, h.lggr)
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
	if !h.globalNodeRateLimiter.Allow(ctx) {
		h.metrics.IncrementGlobalThrottled(ctx, h.lggr)
		return errors.New("global rate limit exceeded")
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L298-338)
```go
func (h *gatewayHandler) send(ctx context.Context, httpReq network.HTTPRequest, req gateway_common.OutboundHTTPRequest) (*network.HTTPResponse, error) {
	if req.Mtls == nil {
		return h.httpClient.Send(ctx, httpReq)
	}

	if h.httpClientFactory == nil {
		return nil, errors.New("nil http client factory, cannot make mtls request")
	}

	// Instantiate a throwaway HTTP client with the provided Mtls client certificate provided.
	// We do this to ensure that we don't accidentally leak auth'd connections to other users.
	// Note: this isn't a DOS vector because
	// a) we have a global rate limit above which limits abuse
	// b) we apply rate limits limiting the ability of sending nodes to spam requests
	// c) we apply per-owner rate limits in the action capability in the
	// workflow node limiting the ability of users to abuse this flow by spamming Mtls requests.
	// The client enforces the mtls concurrency limit internally (on the request's
	// capped-timeout context) before delegating to the underlying transport.
	client, err := h.httpClientFactory(network.HTTPClientConfig{
		Mtls: &gateway_common.MtlsAuth{
			PrivateKey:  req.Mtls.PrivateKey,
			Certificate: req.Mtls.Certificate,
		},
		ConcurrencyLimiter: h.mtlsConcurrencyLimiter,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to instantiate http client for mtls request: %w", err)
	}

	// We don't have access to the org here, so this will fall back to the environment default (=false).
	// That's appropriate because all fields set on the request come from untrusted nodes.
	// The capability separately applies an org-specific check.

	// Note: we intentionally consume the rate-limit after instantiating the client so that a malicious user
	// can't send requests with invalid mtls credentials and thus cheaply consume global tokens.
	if !h.mtlsRequestRateLimiter.Allow(ctx) {
		return nil, fmt.Errorf("global mtls request rate limit exceeded: %w", network.ErrBlockedRequest)
	}

	return client.Send(ctx, httpReq)
}
```

**File:** core/services/gateway/network/httpclient.go (L296-316)
```go
	if config.Mtls != nil {
		// Defence-in-depth protection against accidental reuse
		// of the HTTP client leading to auth'd connections leaking across
		// users.
		defaultTransport.DisableKeepAlives = true
		defaultTransport.TLSHandshakeTimeout = 10 * time.Second

		cert, err := tls.X509KeyPair(config.Mtls.Certificate, config.Mtls.PrivateKey)
		if err != nil {
			return nil, fmt.Errorf("failed to parse MtlsAuth into KeyPair: %w", err)
		}

		defaultTransport.TLSClientConfig = &tls.Config{
			Certificates: []tls.Certificate{cert},
			MinVersion:   tls.VersionTLS12,
		}
		safeConfigBuilder.SetTransport(defaultTransport)

		if config.ConcurrencyLimiter == nil {
			return nil, errors.New("mtls requires a ConcurrencyLimiter")
		}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler_test.go (L1082-1111)
```go
// TestGatewayHandler_Send_InvalidMtlsCertDoesNotConsumeGlobalTokens verifies that a
// request carrying invalid mTLS credentials does not consume a global rate-limit token.
// Otherwise a malicious user could cheaply drain the shared mtls token bucket by spamming
// requests with bogus certificates. It uses the real HTTP client factory so that the
// production code path is what rejects the certificate as invalid.
func TestGatewayHandler_Send_InvalidMtlsCertDoesNotConsumeGlobalTokens(t *testing.T) {
	handler := createTestHandler(t)
	// Burst of exactly 1: only a single mtls request may pass the rate limiter.
	handler.mtlsRequestRateLimiter = limits.GlobalRateLimiter(1, 1)
	handler.httpClientFactory = network.NewHTTPClientFactory(network.HTTPClientConfig{}, logger.Test(t))

	httpReq := network.HTTPRequest{Method: "GET", URL: "https://example.com/api"}
	outboundReq := gateway_common.OutboundHTTPRequest{
		Method: "GET",
		URL:    "https://example.com/api",
		Mtls:   &gateway_common.MtlsAuth{PrivateKey: []byte("not-a-key"), Certificate: []byte("not-a-cert")},
	}

	ctx := t.Context()
	resp, err := handler.send(ctx, httpReq, outboundReq)
	require.Error(t, err)
	require.Nil(t, resp)
	require.Contains(t, err.Error(), "failed to parse MtlsAuth into KeyPair",
		"the real client factory should reject the invalid certificate material")

	// The single available token must still be present: the failed request above must not
	// have consumed it.
	require.True(t, handler.mtlsRequestRateLimiter.Allow(ctx),
		"global mtls rate-limit token must not be consumed by a request with an invalid certificate")
}
```
