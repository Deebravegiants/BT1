### Title
CORS wildcard-origin suffix check allows hostname-confusion bypass in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's public HTTP server implements CORS origin validation with support for wildcard entries such as `*.example.com`. The wildcard match is implemented with a plain `strings.HasSuffix` check on the hostname without validating that the match occurs on a label (dot) boundary. This is the same bug class as CVE-2022-0722 (`parse-url` hostname confusion): a substring-based hostname comparison is used where a proper structural/domain comparison is required, letting an attacker-controlled hostname that merely ends with the allowed suffix be treated as trusted.

### Finding Description
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` parses the incoming `Origin` header and compares it against the configured `CORSAllowedOrigins` list [1](#0-0) . For wildcard entries, the code strips the `*.` prefix and does:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

`strings.HasSuffix` performs a raw string-suffix comparison, not a domain-label comparison. If an operator configures `CORSAllowedOrigins = ["https://*.example.com"]` (the pattern the code and its comment explicitly anticipate, e.g. `*.remix.com`) [3](#0-2) , then any origin whose hostname ends with the literal substring `example.com` — with no dot separator required — will be accepted. For example, an attacker-registered domain `evilexample.com` or `notexample.com` satisfies `strings.HasSuffix("evilexample.com", "example.com") == true`, even though it is not a subdomain of `example.com`.

When `isAllowedOrigin` returns true, the handler reflects the attacker's `Origin` value directly into `Access-Control-Allow-Origin` [4](#0-3) , allowing a page hosted on the attacker's confusable domain to make cross-origin browser requests to the Gateway and read the JSON-RPC responses returned by `ProcessRequest` [5](#0-4) .

This is directly analogous to the reported `parse-url` hostname-confusion advisory (CVE-2022-0722, CWE-200): both bugs stem from treating an unanchored substring/suffix match of a hostname as proof of trust relationship, enabling an unauthorized actor to be misclassified as a trusted origin.

### Impact Explanation
The Gateway HTTP server is the internet-facing entry point (`handleRequest`) that forwards data from CRE/workflow clients through `ProcessRequest` [6](#0-5) . If CORS is enabled with a wildcard entry (a supported and documented configuration pattern), an unprivileged remote attacker who registers a confusable domain (e.g. `evil<allowed-domain>`) can have their web page treated as an authorized origin. This allows the attacker's browser-hosted page, when a victim visits it, to issue authenticated/credentialed cross-origin requests to the Gateway and read back response bodies that would otherwise be restricted to genuinely allowed origins — a cross-user/cross-origin response confusion and information disclosure, matching CWE-200.

### Likelihood Explanation
Exploitability depends entirely on whether an operator's deployment enables CORS with at least one wildcard entry in `CORSAllowedOrigins`, which is an explicitly supported configuration path in this code (the comment even calls out `*.remix.com` as the intended usage) [7](#0-6) . Given that, the bypass requires no special privilege — only registering an attacker-controlled domain that ends with the allowed suffix and getting a victim's browser to visit it while it is interacting with the Gateway endpoint.

### Recommendation
Replace the raw suffix check with a proper domain-boundary comparison, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".example.com"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
i.e., require that the character immediately preceding the matched suffix be a `.` (or that `originHost` equals the base domain exactly), so `evilexample.com` no longer matches `*.example.com`.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.example.com"]`.
2. Attacker registers `https://evilexample.com` and sends a request/preflight to the Gateway with header `Origin: https://evilexample.com`.
3. `splitURL` extracts `originHost = "evilexample.com"`; the wildcard check computes `allowedHost = "example.com"` and `strings.HasSuffix("evilexample.com", "example.com")` returns `true` [8](#0-7) .
4. The server sets `Access-Control-Allow-Origin: https://evilexample.com`, permitting the attacker's page to read the Gateway's JSON-RPC responses via a browser fetch with credentials.

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-163)
```go
func (s *httpServer) isAllowedOrigin(origin string) bool {
	originScheme, originHost, originPort, err := s.splitURL(origin)
	if err != nil {
		s.lggr.Debug("error parsing origin URL", err)
		return false
	}
	for _, allowed := range s.config.CORSAllowedOrigins {
```

**File:** core/services/gateway/network/httpserver.go (L180-190)
```go
		// check for exact host match (e.g., remix.com)
		if originHost == allowedHost {
			return true
		}
		// check for wildcard host match (e.g., *.remix.com)
		if strings.HasPrefix(allowedHost, "*.") {
			allowedHost = allowedHost[2:]
			if strings.HasSuffix(originHost, allowedHost) {
				return true
			}
		}
```

**File:** core/services/gateway/network/httpserver.go (L195-241)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}

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

	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
	duration := time.Since(startTime)
	s.hMetrics.RecordRequestDuration(r.Context(), httpStatusCode, duration)
	s.hMetrics.RecordRequestCount(r.Context(), httpStatusCode)

	w.Header().Set("Content-Type", s.config.ContentTypeHeader)
	w.WriteHeader(httpStatusCode)
	_, err = w.Write(rawResponse) //nolint:gosec // G705: response body is written with an explicit Content-Type, not rendered as HTML
```
