Found the analog: `pluginPPROFHandler` builds a backend request URL by directly string-concatenating an unsanitized route parameter (`gc.Param("profile")`) into the request path, on a route mounted without any authentication middleware — structurally the same bug class as the IDURAR CVE (unauthenticated user input appended to a path/join without validation, allowing directory-structure escape).

### Title
Unauthenticated path/URL injection via unsanitized `profile` parameter in LOOP pprof proxy - (File: core/web/loop_registry.go)

### Summary
`loopRoutes` registers `/plugins/:name/debug/pprof/*profile` on the top-level `api` router group, which only has rate-limiting and session middleware — no `auth.Authenticate*` wrapper is applied, unlike almost every other `/v2/*` route in `core/web/router.go`. The handler `pluginPPROFHandler` takes the wildcard `profile` parameter straight from the URL and concatenates it, unsanitized, into the outbound backend URL string with `fmt.Sprintf`.

### Finding Description
In `core/web/router.go`:
```go
func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
}
``` [1](#0-0) 

This is invoked from `NewRouter` on the `api` group, which is only wrapped with the authenticated rate limiter and session middleware — it never passes through `auth.Authenticate(...)`:
```go
debugRoutes(app, api)
healthRoutes(app, api)
sessionRoutes(app, api)
v2Routes(app, api)
loopRoutes(app, api)
``` [2](#0-1) 

Inside the handler, the wildcard `profile` param is directly formatted into the backend request path with no sanitization, validation, or allowlist of expected pprof endpoint names:
```go
func (l *LoopRegistryServer) pluginPPROFHandler(gc *gin.Context) {
	pluginName := gc.Param("name")
	p, ok := l.registry.Get(pluginName)
	if !ok {
		...
	}
	pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), l.loopHostName, p.EnvCfg.PrometheusPort)
	...
	l.doRequest(gc, "GET", pluginURL, nil, timeout, pluginName)
}
``` [3](#0-2) 

Because `*profile` is a gin wildcard segment, it can carry arbitrary path segments including `../` sequences and query-string injection characters (`?`, `#`, `&`). Since the value is substituted directly into a `fmt.Sprintf` format/URL string (note it is even used as the *format string* itself, `"http://%s:%d/debug/pprof/"+gc.Param("profile")`, compounding the risk of format-string-style surprises if `%` sequences are included), an unauthenticated caller controls the full suffix of the proxied backend URL sent from the node to the internal LOOP plugin's HTTP server on `loopHostName:PrometheusPort`. This is analogous to the IDURAR vulnerability where an unauthenticated public route directly joined user input into a path used for a backend file/resource lookup with no validation, letting the attacker "escape" the intended subpath.

### Impact Explanation
An unauthenticated network client that can reach the node's web server can:
- Freely choose the backend HTTP path/query sent to the internal LOOP process (`.../debug/pprof/<anything>`), enabling access to any endpoint exposed by that internal HTTP listener beyond the intended pprof surface (e.g. arbitrary paths, or injected query parameters via `?`/`#` characters in the wildcard), since there is zero validation of `profile`.
- Potentially pivot requests to unintended internal endpoints of the LOOP's HTTP server (SSRF-like path confusion within the trusted internal segment), and exfiltrate whatever those endpoints return, since the whole flow requires no authentication (`/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and the POST `symbol` route are all unauthenticated).
- This also violates the codebase's own stated intent ("unlike discovery, this endpoint is internal btw the node and plugin") — the code comment indicates the authors assumed this was internal-only traffic, but the route registration does not enforce that assumption with any auth middleware.

### Likelihood Explanation
High reachability: the route is registered on the public API router with no authentication check, and is trivially reachable by any network client that can send HTTP requests to the node's configured web server port. No credentials, tokens, or session are required — this matches the "unauthenticated" precondition explicitly required by the report's analog rules.

### Recommendation
- Require authentication (`auth.Authenticate(...)` with at minimum `AuthenticateByToken`/`AuthenticateBySession`) on the `loopRoutes` group, consistent with nearly every other operational/debug endpoint in `core/web/router.go` (e.g. `debugRoutes`, most of `v2Routes`).
- Validate/allowlist the `profile` wildcard value against the known set of Go pprof sub-paths (`cmdline`, `profile`, `symbol`, `trace`, `goroutine`, `heap`, `allocs`, `block`, `mutex`, `threadcreate`) instead of directly concatenating user input into the backend URL.
- Avoid using untrusted input as (or within) a `fmt.Sprintf` format string; construct the URL via `url.URL{Path: path.Join(...)}` with explicit escaping instead of string concatenation.

### Proof of Concept
1. Ensure a LOOP plugin is registered on the node (e.g., a configured EVM/relayer LOOP with `PrometheusPort` set).
2. As an unauthenticated client, send:
   ```
   GET /plugins/<registered-plugin-name>/debug/pprof/../../../some/internal/endpoint?extra=1 HTTP/1.1
   Host: <node-host>:<web-port>
   ```
3. Observe that `pluginPPROFHandler` forwards the raw, attacker-controlled suffix to `http://<loopHostName>:<PrometheusPort>/debug/pprof/<attacker suffix>` without any authentication check on the incoming request or validation of the suffix, and returns the backend response to the unauthenticated caller via `gc.Data(http.StatusOK, "text/plain", b)`. [3](#0-2) [2](#0-1) [1](#0-0)

### Citations

**File:** core/web/router.go (L87-91)
```go
	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)
```

**File:** core/web/router.go (L230-236)
```go
func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
}
```

**File:** core/web/loop_registry.go (L150-166)
```go
func (l *LoopRegistryServer) pluginPPROFHandler(gc *gin.Context) {
	pluginName := gc.Param("name")
	p, ok := l.registry.Get(pluginName)
	if !ok {
		gc.Data(http.StatusNotFound, "text/plain", fmt.Appendf(nil, "plugin %q does not exist", html.EscapeString(pluginName)))
		return
	}

	// unlike discovery, this endpoint is internal btw the node and plugin
	pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), l.loopHostName, p.EnvCfg.PrometheusPort)
	urlVals, timeout := pprofURLVals(gc)
	if s := urlVals.Encode(); s != "" {
		pluginURL += "?" + s
	}
	l.logger.Infow("Forwarding plugin pprof request", "plugin", pluginName, "url", pluginURL)
	l.doRequest(gc, "GET", pluginURL, nil, timeout, pluginName)
}
```
