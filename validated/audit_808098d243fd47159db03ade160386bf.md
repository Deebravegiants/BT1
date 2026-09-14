The scan confirms a concrete, reachable analog to CVE-2025-5605 in the node's internet-facing gateway routes.

### Title
Unauthenticated disclosure of plugin memory/profiling statistics via `/plugins/:name/debug/pprof/*` and `/plugins/:name/metrics` routes - (File: `core/web/router.go`)

### Summary
The Chainlink node's `NewRouter` wires `loopRoutes` directly onto the base `api` route group, which only carries rate-limiting and session-cookie middleware — it never applies the `auth.Authenticate(...)` middleware used by every other sensitive `/v2` and `/debug` route.

### Finding Description
In `core/web/router.go`, `NewRouter` builds the `api` group with only `sessions.Sessions` and a rate limiter, then registers routes: [1](#0-0) 

`loopRoutes` is called on this unauthenticated `api` group and exposes `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` with no auth middleware at all: [2](#0-1) 

Compare this to `debugRoutes`, which wraps the analogous `/debug/vars` endpoint in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`: [3](#0-2) 

and to `metricRoutes` (pprof for the node itself), which is only reachable inside the already-authenticated `authv2` group: [4](#0-3) 

The `pluginPPROFHandler` proxies arbitrary `net/http/pprof` profile names (`heap`, `goroutine`, `allocs`, `profile`, etc.) straight through to the internal LOOP plugin process, using the caller-supplied `profile` path param and query values with no authorization check: [5](#0-4) 

This is directly analogous to CVE-2025-5605: an unprivileged client can manipulate the request URI (`/plugins/<name>/debug/pprof/heap`) on the Management/Web Console-equivalent surface to bypass the intended authentication and retrieve memory statistics (heap profiles, goroutine dumps, allocation profiles) — the same class of "limited to memory statistics" partial information disclosure described in the advisory.

### Impact Explanation
Any unauthenticated network client that can reach the node's HTTP API can pull heap/goroutine/allocation profiles for each registered LOOP plugin, disclosing internal memory layout, running goroutine stacks, and potentially sensitive data referenced in memory (addresses, buffer contents, internal state) without any credentials — matching the CVSS 5.3 confidentiality-only impact of the reference CVE.

### Likelihood Explanation
High: the routes are registered unconditionally on every node that has LOOP plugins registered, require no special network position beyond reaching the node's already internet-facing web server, and need no valid session, API token, or role.

### Recommendation
Wrap `loopRoutes` (or at minimum the `/plugins/:name/metrics` and `/plugins/:name/debug/pprof/*` endpoints) with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` middleware used for `authv2`/`debugRoutes`, or move it under the `authv2` group like `metricRoutes`.

### Proof of Concept
```
GET /plugins/<registered-plugin-name>/debug/pprof/heap HTTP/1.1
Host: <node-host>:<port>
```
No `Cookie`, `X-Chainlink-*`, or session header required — the request is forwarded unauthenticated by `pluginPPROFHandler` to the internal LOOP process and the heap profile bytes are returned to the caller (`core/web/loop_registry.go:150-166`).

### Citations

**File:** core/web/router.go (L77-91)
```go
	rl := config.WebServer().RateLimit()
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)

	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)
```

**File:** core/web/router.go (L180-183)
```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", expvar.Handler())
}
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

**File:** core/web/router.go (L445-446)
```go
		// Debug routes accessible via authentication
		metricRoutes(authv2)
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
