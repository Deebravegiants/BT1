### Title
Header blocklist bypass via underscore-variant header names in Gateway outbound HTTP client - (`core/services/gateway/network/httpclient.go`)

### Summary
The Gateway's outbound HTTP client enforces a security-critical header blocklist (`X-Forwarded-For`, `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Real-Ip`, `Host`, `Connection`, `Transfer-Encoding`, etc.) to prevent workflow-controlled requests from spoofing trust-context or smuggling protocol-level headers to third-party endpoints. The check only lower-cases header names before comparing against the blocklist — it does not normalize `_` to `-` — so an underscore-variant of any blocked header (e.g. `X_Forwarded_For`, `Connection` → `Connection` is fine but `Transfer_Encoding`, `X_Real_Ip`, `X_Forwarded_Host`) bypasses the check and is forwarded to the external endpoint on the wire, unmodified, because Go's header canonicalization does not treat `_` as a word separator either. This is the same defect class as the underlying Traefik CVE: a security-relevant header-name comparison that fails to account for `_`/`-` equivalence.

### Finding Description
`validateHeaderNames` in `core/services/gateway/network/httpclient.go` builds a blocked-set of lower-cased header names and rejects any request header whose lower-cased name matches: [1](#0-0) 

The blocklist itself is dash-delimited and explicitly documents the security rationale for each entry (IP/host/proto spoofing prevention, protocol-abuse prevention): [2](#0-1) 

Because the comparison is `strings.ToLower(name)` only — with no `strings.ReplaceAll(name, "_", "-")` step, unlike the gold-standard `isManagedXHeader`-style primitive described in the analog report — a header such as `X_Forwarded_For` or `X_Real_Ip` does not match any entry in `blockedSet` and passes validation.

The header then flows unmodified into the outgoing `net/http.Request` via `requestToNetHeader`/`r.Header.Add`: [3](#0-2) [4](#0-3) 

Go's `textproto.CanonicalMIMEHeaderKey` (used internally by `Header.Add`) only treats `-` as a word boundary, so `X_Forwarded_For` is canonicalized to the literal key `X_forwarded_for` — distinct from `X-Forwarded-For` — and is sent to the destination server verbatim, alongside (not replacing) any legitimate value.

Reachability: these headers originate from the workflow/DON node's `OutboundHTTPRequest` and are routed by the gateway's HTTP Action handler directly into the `network.HTTPClient.Send` call without any additional underscore-aware filtering: [5](#0-4) 

This confirms the header set is attacker/workflow-controlled and reaches the blocklist check described above before being dispatched to an arbitrary external endpoint (the HTTP Action capability's whole purpose per its README):



### Impact Explanation
A workflow (an unprivileged actor relative to the Gateway operator) can smuggle otherwise-blocked headers to any external HTTP endpoint the Gateway is instructed to call on its behalf, using the underscore-variant bypass:
- `X_Forwarded_For` / `X_Real_Ip` / `X_Forwarded_Host` / `X_Forwarded_Proto`: spoof trust context (client IP, host, scheme) toward the destination server. If that destination normalizes `_`/`-` equivalently (many WSGI/CGI/nginx-with-underscores/Java servlet backends do, per the analog report), the spoofed value can influence IP-based ACLs or trust decisions on the far end, i.e., request impersonation via header injection through Chainlink's own gateway egress path.
- `Transfer_Encoding` / `Connection` / `Keep_Alive` / `Te` / `Trailer`: reach the wire as literal non-hop-by-hop-recognized keys, potentially enabling protocol confusion/smuggling against the destination if it (or an intermediary proxy in front of it) also normalizes underscores.

This does not break Chainlink node authentication directly, but it is a concrete allowlist/blocklist bypass in the Gateway's internet-facing HTTP Action egress path — the exact class of defect the CVE targets (CWE-178: improper handling of alternate header-name forms in a security check).

### Likelihood Explanation
High reachability, moderate exploitation complexity: any party able to register/run a workflow whose HTTP Action capability is executed by a DON node can set arbitrary `Headers`/`MultiHeaders` on the `OutboundHTTPRequest`. No special privilege beyond normal workflow authoring is required; the bypass is a single header-name transformation (`-` → `_`), directly analogous to the PoC in the source report (`curl -H "X_Auth_User: ..."`).

### Recommendation
Extend `validateHeaderNames` in `core/services/gateway/network/httpclient.go` to normalize `_` to `-` (in addition to lower-casing) before comparing against `blockedSet`, mirroring the `_`↔`-` equivalence primitive used elsewhere in the codebase for the `X-Forwarded-*` family. Apply the same normalization to both `validateHeaders` and `validateMultiHeaders` call paths, and consider stripping/rejecting *all* headers containing underscores by default for the outbound HTTP Action client, consistent with the referenced advisory's recommended mitigation (`allowHeadersWithUnderscores: false`-style behavior).

### Proof of Concept
1. A workflow issues an `OutboundHTTPRequest` (HTTP Action capability) with `MultiHeaders: {"X_Forwarded_For": ["10.0.0.1"]}` targeting an internal-trust-aware third-party API.
2. `makeOutgoingRequest` (`core/services/gateway/handlers/capabilities/v2/http_handler.go:404-421`) builds `network.HTTPRequest{MultiHeaders: ...}` unchanged and calls `httpClient.Send`.
3. `validateMultiHeaders` → `validateHeaderNames` (`core/services/gateway/network/httpclient.go:411-431`) lower-cases `"X_Forwarded_For"` to `"x_forwarded_for"`, which is absent from `blockedSet` (`{"x-forwarded-for", ...}`), so validation passes.
4. `requestToNetHeader` + `r.Header.Add` (`httpclient.go:203-218, 466-475`) add the header using Go's canonicalization, producing literal key `X_forwarded_for`.
5. The outbound request reaches the destination server carrying `X_forwarded_for: 10.0.0.1`, bypassing the Gateway's IP-spoofing protection for that header class.

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

**File:** core/services/gateway/network/httpclient.go (L466-475)
```go
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
