### Title
Missing `Vary: Origin` Header on Dynamic CORS Responses in Gateway HTTP Server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's `httpServer.handleRequest` function dynamically reflects the caller-supplied `Origin` header into `Access-Control-Allow-Origin` when the origin matches an allow-list entry, but never emits a `Vary: Origin` (or `Vary: *`) header on the response. This is the same root-cause bug class as CVE-2017-7674 (Apache Tomcat CORS filter): any shared/caching HTTP intermediary sitting in front of the Gateway's user-facing server will key cached entries only by URL, not by the varying `Origin`-dependent CORS headers, allowing a cached response generated for one origin to be served, with that origin's `Access-Control-Allow-Origin`, to a different requester/origin.

### Finding Description
`isAllowedOrigin` validates the request `Origin` against `s.config.CORSAllowedOrigins` [1](#0-0) , and `handleRequest` conditionally sets `Access-Control-Allow-Origin` to the exact reflected `origin` value when it is allowed [2](#0-1) . Because the value of `Access-Control-Allow-Origin` (and whether CORS headers are present at all) varies per-request based on the `Origin` header, RFC 7231/CORS best practice requires a `Vary: Origin` response header so caches do not conflate responses across different origins. No such header is set anywhere in this file — a repository-wide search for `Vary` in this server package returns no matches [2](#0-1) . This is exactly the CORS-filter defect described in GHSA-73rx-3f9r-x949/CVE-2017-7674, where Tomcat's CORS filter omitted the `Vary: Origin` header, enabling cache poisoning.

By contrast, the node's main web UI CORS handling in `core/web/router.go` uses the third-party `github.com/gin-contrib/cors` middleware [3](#0-2) , which is known to manage `Vary` headers internally, so that path is not implicated. The vulnerable code is specific to the custom, hand-rolled CORS logic in the Gateway's `network.httpServer`, which serves the internet-facing `UserServerConfig` endpoint (`Path = "/user"`) reachable by unauthenticated/unprivileged external clients [4](#0-3) .

### Impact Explanation
If the Gateway is deployed behind any shared caching layer (reverse proxy, CDN, or even a browser's shared cache/service worker) that caches by URL, a response computed for a legitimate allowed origin (including its `Access-Control-Allow-Origin` header) can be served to a subsequent request from a different origin. This enables cross-origin response confusion: an attacker-controlled page on a non-allowed origin could receive a cached response that carries a permissive `Access-Control-Allow-Origin` for a previously-cached allowed origin, letting the attacker's page read cross-origin response data that should have been blocked by CORS, or poisoning the cache so legitimate clients receive stale/incorrect CORS decisions.

### Likelihood Explanation
Exploitability is contingent on a caching intermediary being present in front of the Gateway's `UserServerConfig` HTTP endpoint. The Gateway server itself does not implement caching, so the intrinsic likelihood in a bare deployment is low, but this is precisely an "insufficient verification/insufficient header" class defect — any operator fronting the Gateway with a CDN or shared proxy cache (a common production pattern for internet-facing services) inherits the vulnerability without any code change, since the missing `Vary` header is the exact enabling condition for cache poisoning, matching the CVE analog closely.

### Recommendation
Set `w.Header().Set("Vary", "Origin")` unconditionally (or append to any existing `Vary` value) whenever `s.config.CORSEnabled` is true, before writing CORS headers in `handleRequest`, mirroring the fix applied upstream for CVE-2017-7674. This should be done regardless of whether the origin is ultimately allowed, since the decision to include or omit `Access-Control-Allow-Origin` itself varies by `Origin` and must be reflected to caches.

### Proof of Concept
1. Deploy the Gateway's `UserServerConfig` HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://good.example.com"]`, fronted by a caching reverse proxy that caches based on request URL/method only.
2. An authorized client at `https://good.example.com` sends a request; the proxy caches the response, which includes `Access-Control-Allow-Origin: https://good.example.com`.
3. An attacker page hosted at `https://evil.example.com` issues the same request (same URL/path); the caching proxy returns the cached response, including the `Access-Control-Allow-Origin: https://good.example.com` header, to the attacker's browser context.
4. Because the header value is now attacker-visible/cached and inconsistent with the requesting origin, the attacker can leverage cache behavior (e.g., forcing cache population, or exploiting shared-cache poisoning across users) to retrieve cross-origin response bodies that should have been denied by the CORS policy — the direct impact class described by CVE-2017-7674.

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-193)
```go
func (s *httpServer) isAllowedOrigin(origin string) bool {
	originScheme, originHost, originPort, err := s.splitURL(origin)
	if err != nil {
		s.lggr.Debug("error parsing origin URL", err)
		return false
	}
	for _, allowed := range s.config.CORSAllowedOrigins {
		// probably better to do this once when server starts and store it in a map
		// this is an easier solution so we don't have to apply more changes to the code
		// just need to be careful when specifying allowed origins in the config file
		allowedScheme, allowedHost, allowedPort, err := s.splitURL(allowed)
		if err != nil {
			s.lggr.Debug("error parsing allowed origin URL", err)
			continue
		}
		// skip if the scheme doesn't match at all
		if originScheme != allowedScheme {
			continue
		}
		// skip if the port doesn't match at all
		if originPort != allowedPort {
			continue
		}
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
	}
	return false
}
```

**File:** core/services/gateway/network/httpserver.go (L195-209)
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
```

**File:** core/web/router.go (L571-586)
```go
// Add CORS headers so UI can make api requests
func uiCorsHandler(ao string) gin.HandlerFunc {
	c := cors.Config{
		AllowMethods:     []string{"GET", "POST", "PATCH", "DELETE"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           math.MaxInt32,
	}
	if ao == "*" {
		c.AllowAllOrigins = true
	} else if allowOrigins := strings.Split(ao, ","); len(allowOrigins) > 0 {
		c.AllowOrigins = allowOrigins
	}
	return cors.New(c)
}
```

**File:** core/scripts/gateway/sample_config.toml (L1-10)
```text
[UserServerConfig]
Port = 8080
Path = "/user"
ContentTypeHeader = "application/jsonrpc"
ReadTimeoutMillis = 1000
WriteTimeoutMillis = 1000
RequestTimeoutMillis = 1000
MaxRequestBytes = 10_000
CORSEnabled = false
CORSAllowedOrigins = []
```
