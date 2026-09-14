### Title
Outbound HTTP header denylist bypass via underscore/hyphen header-name conflation - ([File: core/services/gateway/network/httpclient.go])

### Summary
The chainlink gateway's outbound HTTP client enforces a security-critical header denylist (`defaultBlockedHeaders`) intended to prevent workflow-controlled requests from spoofing trust-sensitive headers such as `Host`, `X-Forwarded-For`, `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Real-IP`, `Content-Length`, and `Transfer-Encoding`. The enforcement in `validateHeaderNames` does an exact, case-insensitive string match against this denylist, but never normalizes underscore (`_`) vs. hyphen (`-`) variants of a header name. Because HTTP header semantics on many downstream servers/proxies (the same bug class as the Django ASGI advisory) treat `X-Forwarded-For` and `X_Forwarded_For` as equivalent, an unprivileged workflow author can trivially bypass the denylist by substituting underscores for hyphens in a blocked header name.

### Finding Description
`defaultBlockedHeaders` explicitly documents the intent to block spoofing-relevant headers: [1](#0-0) 

The check that enforces this list only lower-cases the header name and does an exact map lookup — it never strips or normalizes `_`/`-`: [2](#0-1) 

This validation is invoked unconditionally on every outbound `Send`, before the headers are attached to the outgoing `http.Request`: [3](#0-2) [4](#0-3) 

The headers ultimately originate from an `OutboundHTTPRequest` supplied by a workflow node (an unprivileged, gateway-mediated actor) and are forwarded verbatim into the `network.HTTPRequest.Headers`/`MultiHeaders` fields without any additional sanitization: [5](#0-4) 

Because `validateHeaderNames` (and the corresponding `validateHeaders`/`validateMultiHeaders` wrappers) compares header names as exact strings after `strings.ToLower`, a header submitted as `X_Forwarded_For`, `X_Forwarded_Host`, `X_Real_IP`, `Content_Length`, or `Transfer_Encoding` will not match any entry in `blockedSet` and therefore passes validation, even though it is semantically equivalent (per RFC ambiguity / common server/CGI-style underscore-hyphen conflation) to the blocked hyphenated header. The header is then added directly to the outgoing `http.Request` via `Header.Add`, which canonicalizes case but does not convert `_` to `-`. If the receiving/downstream service conflates the two forms (the exact bug class described in the Django ASGI advisory), this allows a workflow author to smuggle a spoofed trust header past a control specifically designed to stop that class of attack.

### Impact Explanation
This defeats the security control that exists specifically to stop IP/host/protocol spoofing and connection-manipulation headers (per the code comments themselves) in requests the gateway makes to third-party targets on behalf of workflows. An unprivileged workflow author can inject headers the gateway's own policy explicitly disallows (`Host`, `X-Forwarded-For`, `X-Forwarded-Proto`, `Content-Length`, `Transfer-Encoding`), enabling request impersonation/spoofing against downstream systems that rely on the gateway's denylist as a trust boundary. This is a concrete allowlist/denylist bypass in the internet-facing gateway's HTTP handling path.

### Likelihood Explanation
Likelihood is high: any workflow author capable of constructing an `OutboundHTTPRequest` (a normal, expected capability of the HTTP Action) can trivially craft a header name variant with underscores instead of hyphens with zero additional privilege, and the bypass requires no race condition, timing, or unusual environment — it's a straightforward string-matching gap.

### Recommendation
Normalize header names before denylist comparison in `validateHeaderNames` — e.g., replace `_` with `-` (and vice versa, or check both), or reject header names containing `_` entirely, before performing the case-insensitive blocklist lookup. Apply the same normalization consistently to both `validateHeaders` and `validateMultiHeaders`.

### Proof of Concept
1. A workflow (unprivileged actor) issues an HTTP Action request with `MultiHeaders: {"X_Forwarded_For": ["10.0.0.1"]}` via the gateway's HTTP capability handler (`makeOutgoingRequest`).
2. The gateway calls `httpClient.Send`, which invokes `validateMultiHeaders` → `validateHeaderNames`.
3. `strings.ToLower("X_Forwarded_For")` = `"x_forwarded_for"`, which is absent from `blockedSet` (which only contains `"x-forwarded-for"`), so validation passes.
4. The header is added to the outgoing `http.Request` and sent to the target host, bypassing the intended "prevents IP spoofing" control.

### Citations

**File:** core/services/gateway/network/httpclient.go (L116-131)
```go
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

**File:** core/services/gateway/network/httpclient.go (L411-431)
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

func (c *httpClient) validateHeaders(headers map[string]string) error {
	return c.validateHeaderNames(slices.Collect(maps.Keys(headers)))
}

func (c *httpClient) validateMultiHeaders(multiHeaders map[string][]string) error {
	return c.validateHeaderNames(slices.Collect(maps.Keys(multiHeaders)))
}
```

**File:** core/services/gateway/network/httpclient.go (L436-446)
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
```

**File:** core/services/gateway/network/httpclient.go (L471-475)
```go
	for k, values := range requestToNetHeader(req) {
		for _, v := range values {
			r.Header.Add(k, v)
		}
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
