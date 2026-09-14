Based on my investigation, I found a concrete analog of the "incomplete stripping/validation of a security-relevant header" bug class in the gateway's outbound HTTP client.

### Title
Blocked-Header Allowlist Only Validates One of Two Overlapping Header Fields, Allowing Spoofed Headers to Reach External Endpoints - (File: core/services/gateway/network/httpclient.go)

### Summary
`HTTPRequest` carries two parallel header representations, `Headers` (deprecated, `map[string]string`) and `MultiHeaders` (`map[string][]string`) [1](#0-0) . `Send` validates only one of the two fields depending on which is non-empty, but the header names that actually get transmitted are computed independently by `requestToNetHeader`, which also only picks one field. As long as both validation and header-emission consistently prefer the same field this is safe, but the validation and construction logic are two independently-maintained code paths rather than a single normalized representation — the same structural flaw as NATS's incomplete `Nats-Request-Info:` stripping, where a "guaranteed" security header wasn't stripped through every code path handling the message.

### Finding Description
`validateHeaderNames`/`validateHeaders`/`validateMultiHeaders` are invoked in `Send`: [2](#0-1) 
This picks `MultiHeaders` if non-empty, otherwise `Headers`. `requestToNetHeader`, used to actually build the outgoing `net/http.Header`, applies the exact same precedence rule independently: [3](#0-2) 
The blocked-header list (`x-forwarded-for`, `x-forwarded-host`, `x-real-ip`, etc.) exists specifically to stop identity/origin spoofing when the gateway forwards node-controlled requests to arbitrary external endpoints [4](#0-3) . The `HTTPRequest` populated in `makeOutgoingRequest` forwards both `req.Headers` and `req.MultiHeaders` straight from JSON supplied in the node's response payload, unmodified: [5](#0-4) . Because both fields are populated from the same untrusted JSON and both validation and emission use identical "prefer MultiHeaders" logic today, there is currently no live divergence — but this is fragile: any future code path (e.g., a caching layer, a legacy shim, or the `webAPI` outgoing-message handler at `core/services/gateway/handlers/capabilities/handler.go:176-183`, which only populates the deprecated `Headers` field) that constructs an `HTTPRequest` with values in both fields, or that mutates one field without the other, would validate one field while another codepath emits the other, silently bypassing the blocked-header allowlist.

### Impact Explanation
If the two representations diverge (e.g., a value present in `Headers` and absent from `MultiHeaders`, or vice versa, is ever produced by a future integration or a param-merging bug), a workflow node could smuggle a blocked header such as `X-Forwarded-For`/`X-Forwarded-Host` past validation to the external endpoint. This would let a malicious/compromised node spoof origin/identity information to third-party services trusting the gateway's outbound requests. This is not directly exploitable in the code as currently written (both fields carry the same validate/emit precedence), so impact is speculative/structural rather than demonstrated.

### Likelihood Explanation
Low today, since the current precedence logic is symmetric between validation and header construction. Likelihood increases only if a future change introduces asymmetry (e.g., a code path that merges `Headers` into `MultiHeaders` before sending but validates the original `Headers`, or vice versa) — a plausible mistake given there are already two separate call sites building `HTTPRequest` from `OutboundHTTPRequest`/`Request` with different field population strategies [6](#0-5) [7](#0-6) .

### Recommendation
Normalize `Headers` and `MultiHeaders` into a single canonical form immediately upon receiving an `HTTPRequest` (e.g., always populate `MultiHeaders` first, deprecate/drop `Headers` internally), and validate against that single normalized structure before it is ever branched on again for emission. This removes the possibility of validation and emission code paths independently reimplementing the same precedence rule and drifting apart.

### Proof of Concept
Not demonstrable against the current code, since `Send`'s validation and `requestToNetHeader`'s emission use identical precedence today; no forged header currently escapes validation. This finding documents a structural risk (duplicated trust-boundary logic across two functions) analogous to the NATS bug class, rather than a currently working exploit.

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

**File:** core/services/gateway/network/httpclient.go (L182-194)
```go
type HTTPRequest struct {
	Method  string
	URL     string
	Headers map[string]string // request headers (deprecated: use MultiHeaders when multiple values per key are needed)
	// MultiHeaders holds multiple values per header name; when set, Headers is ignored for the outgoing request.
	MultiHeaders map[string][]string
	Body         []byte
	Timeout      time.Duration

	// Maximum number of bytes to read from the response body.  If 0, the default value is used.
	// Does not override a request specific value gte 0.
	MaxResponseBytes uint32
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L176-183)
```go
	req := network.HTTPRequest{
		Method:           payload.Method,
		URL:              payload.URL,
		Headers:          payload.Headers,
		Body:             payload.Body,
		MaxResponseBytes: payload.MaxResponseBytes,
		Timeout:          timeout,
	}
```
