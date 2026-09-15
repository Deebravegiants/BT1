## Analysis

The CVE describes an HTTP header-stripping filter that is bypassed because it does exact/case-insensitive matching but does not normalize `_`↔`-`, while downstream consumers treat underscore and dash variants as equivalent. Chainlink's gateway HTTP client implements the exact same style of filter for the same class of headers (`X-Forwarded-For`, `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Real-IP`, `Host`, etc.), and it has the identical normalization gap.

### Title
Header allowlist/blocklist bypass via underscore-for-dash substitution in gateway outbound HTTP client - (`File: core/services/gateway/network/httpclient.go`)

### Summary
The gateway's outbound `httpClient.Send` strips a fixed list of security-sensitive headers (`host`, `x-forwarded-for`, `x-forwarded-host`, `x-forwarded-proto`, `x-real-ip`, `connection`, etc.) before proxying a workflow/action-capability-defined HTTP request to an external endpoint. The filter only lower-cases header names before comparison; it never normalizes `_` to `-`. A workflow author (an unprivileged actor who defines an HTTP capability call executed on their behalf by a DON node and relayed by the Gateway) can smuggle a functionally-equivalent header such as `X_Forwarded_For` or `Host_` past the blocklist, because it will not case-fold-match `x-forwarded-for` in the blocked set.

### Finding Description
`defaultBlockedHeaders` lists the header names that must never reach the destination server, explicitly including spoofing-prone headers: [1](#0-0) 

Validation is performed by `validateHeaderNames`, which lower-cases both the blocked-name set and the incoming header names, but does not translate underscores to dashes: [2](#0-1) 

`Send` calls this validator and, if it passes, forwards the headers unchanged via `requestToNetHeader`/`r.Header.Add`: [3](#0-2) 

`requestToNetHeader` simply copies whatever header name/value pairs were provided in `HTTPRequest.Headers`/`MultiHeaders`, with no additional canonicalization of the semantic header identity: [4](#0-3) 

These `HTTPRequest.Headers` originate from an `OutboundHTTPRequest` that is unmarshalled from a node/DON message representing a workflow's HTTP capability call, and is forwarded to `httpClient.Send` via `gatewayHandler.send`/`makeOutgoingRequest`: [5](#0-4) [6](#0-5) 

Because the header name a workflow specifies is fully attacker-controlled (it is user-authored workflow config, not something the gateway generates), a value like `X_Forwarded_For: 127.0.0.1` or `X-Forwarded_For` will not be caught by `validateHeaderNames` (no dash/underscore folding), yet many HTTP frameworks and reverse proxies treat `_`and `-` in header names as interchangeable when building trust-decision headers — exactly the underscore/dash normalization mismatch described in GHSA-vjrc-mh2v-45x6.

### Impact Explanation
The blocklist exists specifically to prevent workflow-controlled outbound requests from spoofing `Host`/`X-Forwarded-*`/`X-Real-IP` values toward third-party/back-end services (per the inline comments: "prevents IP spoofing", "prevents host header spoofing"). If the destination service (or an intermediate proxy in front of it) normalizes underscores to dashes — a common behavior in WSGI-based apps (Django/Flask/FastAPI) and various middlewares, as called out in the advisory — an unprivileged workflow author can bypass this Gateway-enforced protection and inject a spoofed trust header that the upstream service will honor. This can enable IP-based access-control bypass, log/audit falsification, or trust-header-based authorization bypass on the destination service, mirroring the "potential privilege escalation" impact described in the CVE, scoped here to whatever trust the destination places in these headers.

### Likelihood Explanation
Likelihood is moderate-to-high: constructing an HTTP capability/workflow definition with a custom header name is a normal, supported feature (`Headers`/`MultiHeaders` on `OutboundHTTPRequest`), requiring no special privilege beyond being able to author/run a workflow — an unprivileged capability already exposed through the gateway's HTTP action capability. The only additional requirement is a destination service that normalizes `_`/`-` in header names, which is common for WSGI-based backends and is explicitly the trigger condition named in the original advisory.

### Recommendation
Normalize header names in `validateHeaderNames` (and ideally in `requestToNetHeader`) the same way the OAuth2-Proxy patch does: fold both dashes and underscores (in addition to case) before comparing against `BlockedHeaders`, e.g. `strings.ReplaceAll(strings.ToLower(name), "_", "-")`. Apply the same normalization when building the outbound `http.Header` so that a header supplied with underscores cannot slip through as a different, unblocked "identity" than its dash-equivalent.

### Proof of Concept
1. Configure a workflow / action-capability HTTP request with `Headers: {"X_Forwarded_For": "127.0.0.1"}` (or `"X-Forwarded_For"`), targeting an external endpoint that trusts `X-Forwarded-For` when normalized from underscores.
2. `gatewayHandler.makeOutgoingRequest` unmarshals this into `network.HTTPRequest.Headers` and calls `h.httpClient.Send`.
3. `validateHeaderNames` lower-cases the name to `x_forwarded_for`, which does not match any entry in `defaultBlockedHeaders` (`x-forwarded-for`), so the header passes validation.
4. `requestToNetHeader`/`http.Request.Header.Add` forwards `X_Forwarded_For: 127.0.0.1` to the destination unmodified, where a backend normalizing underscores to dashes treats it as a trusted `X-Forwarded-For` header, defeating the Gateway's spoofing protection.

### Citations

**File:** core/services/gateway/network/httpclient.go (L112-131)
```go
var (
	defaultAllowedPorts   = []int{80, 443}
	defaultAllowedSchemes = []string{"http", "https"}
	defaultAllowedMethods = []string{"GET", "POST", "PUT", "PATCH", "DELETE"}
	defaultBlockedHeaders = []string{
		"host",              // target host is set in the http client
		"content-length",    // length is computed from actual body to ensure integrity
		"transfer-encoding", // http client manages encoding based on actual content
		"user-agent",        // gateway controls its own identification to backend services
		"upgrade",           // prevents protocol upgrade attacks
		"expect",            // prevents 100-continue exploitation
		"connection",        // external developers cannot control connection behavior or persistence
		"keep-alive",        // gateway manages its own connection pooling and timeouts
		"te",                // blocks attempts to manipulate how request bodies are processed
		"trailer",           // blocks delayed header injection after request body
		"x-forwarded-for",   // prevents IP spoofing
		"x-forwarded-host",  // prevents host header spoofing
		"x-forwarded-proto", // prevents protocol spoofing
		"x-real-ip",         // prevents IP address spoofing
	}
```

**File:** core/services/gateway/network/httpclient.go (L203-218)
```go
// requestToNetHeader builds net/http.Header from req. Uses MultiHeaders when set, otherwise Headers.
func requestToNetHeader(req HTTPRequest) http.Header {
	out := make(http.Header)
	if len(req.MultiHeaders) > 0 {
		for k, values := range req.MultiHeaders {
			for _, v := range values {
				out.Add(k, v)
			}
		}
		return out
	}
	for k, v := range req.Headers {
		out.Add(k, v)
	}
	return out
}
```

**File:** core/services/gateway/network/httpclient.go (L411-423)
```go
// validateHeaderNames checks that none of the given header names are in the blocked list (case-insensitive).
func (c *httpClient) validateHeaderNames(names []string) error {
	blockedSet := make(map[string]struct{}, len(c.config.BlockedHeaders))
	for _, b := range c.config.BlockedHeaders {
		blockedSet[strings.ToLower(b)] = struct{}{}
	}
	for _, name := range names {
		if _, blocked := blockedSet[strings.ToLower(name)]; blocked {
			return fmt.Errorf("%w: HTTP header not allowed: %s", ErrBlockedRequest, name)
		}
	}
	return nil
}
```

**File:** core/services/gateway/network/httpclient.go (L436-476)
```go
func (c *httpClient) Send(ctx context.Context, req HTTPRequest) (*HTTPResponse, error) {
	if err := c.validateMethod(req.Method); err != nil {
		return nil, err
	}
	if len(req.MultiHeaders) > 0 {
		if err := c.validateMultiHeaders(req.MultiHeaders); err != nil {
			return nil, err
		}
	} else if err := c.validateHeaders(req.Headers); err != nil {
		return nil, err
	}

	to := req.Timeout
	if to == 0 {
		to = c.config.DefaultTimeout
	}

	if to > c.config.maxRequestDuration {
		to = c.config.maxRequestDuration
	}

	c.lggr.Debugw("sending HTTP request with timeout", "request timeout", to)

	timeoutCtx, cancel := context.WithTimeout(ctx, to)
	defer cancel()

	requestStart := time.Now()
	trace, traceState := newClientTrace(ctx, req.Method, requestStart, c.metrics)
	timeoutCtx = httptrace.WithClientTrace(timeoutCtx, trace)

	r, err := http.NewRequestWithContext(timeoutCtx, req.Method, req.URL, bytes.NewBuffer(req.Body))
	if err != nil {
		c.metrics.recordTotal(ctx, req.Method, 0, false, false, time.Since(requestStart))
		return nil, err
	}
	for k, values := range requestToNetHeader(req) {
		for _, v := range values {
			r.Header.Add(k, v)
		}
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L404-421)
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
```
