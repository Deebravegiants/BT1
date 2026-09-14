## Finding

### Title
Unauthenticated LOOP plugin pprof/metrics proxy with unsanitized path forwarding enables internal endpoint traversal - (File: core/web/loop_registry.go)

### Summary
The `loopRoutes` group is mounted directly on the top-level `api` router group, which only applies rate-limiting and session middleware — it is never wrapped by `auth.Authenticate(...)`, unlike every other sensitive route group (`debugRoutes`, `authv2`, etc.) in the same file. Combined with this, `pluginPPROFHandler` builds the outbound proxy URL by directly concatenating the unsanitized wildcard route parameter `*profile` into a request path, without validating or cleaning it. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`NewRouter` builds an `api` group that only has rate limiting and cookie-session middleware attached, then calls `loopRoutes(app, api)`, which registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` with **no authentication middleware at all**: [4](#0-3) 

This is in contrast to `debugRoutes`, which explicitly wraps its `/debug/vars` endpoint in `auth.Authenticate(...)`: [5](#0-4) 

`pluginPPROFHandler` takes the gin wildcard capture `gc.Param("profile")` (matched via the `*profile` catch-all route segment) and directly appends it via `fmt.Sprintf` into the proxied URL string, without any path cleaning, character allow-listing, or rejection of `..`/encoded traversal sequences: [6](#0-5) 

Because gin's router does not resolve `../` segments in wildcard (`*param`) captures the way `filepath.Clean` or an HTTP proxy normally would, an unauthenticated caller can manipulate `profile` to redirect the outbound request to arbitrary paths on the internal LOOP plugin's HTTP listener (`loopHost:PrometheusPort`) — reaching endpoints beyond the intended `/debug/pprof/*` surface on that internal service. This mirrors the CVE-2023-34409 bug class: an internet-facing/unauthenticated route uses attacker-controlled path data without proper normalization/validation to reach functionality that was intended to require authorization scoping, leading to information disclosure and unauthorized access to internal APIs.

### Impact Explanation
An unauthenticated remote client with network access to the chainlink node's web server can:
- Enumerate registered LOOP plugins and pull Prometheus metrics and full Go `pprof` profiles (goroutine stacks, heap dumps, cmdline, profile/trace) without any credentials, which is itself a serious information-disclosure vector (memory contents, internal state, potentially secrets held in memory).
- Abuse the unsanitized `profile` wildcard to attempt to pivot the proxied request to other paths served on the internal LOOP plugin's HTTP port, beyond the intended `/debug/pprof/` namespace, since the concatenation performs no path canonicalization or containment check.

### Likelihood Explanation
The route is reachable without authentication as soon as the HTTP API port is network-accessible — no special privilege or valid session/token is required, and the request is a single unauthenticated GET/POST to a documented route pattern (`/plugins/:name/debug/pprof/*profile`).

### Recommendation
- Wrap `loopRoutes` (or at minimum the `pluginMetricHandler`/`pluginPPROFHandler`/`pluginPPROFPOSTSymbolHandler` group) with the same `auth.Authenticate(...)` + role-check middleware used elsewhere (e.g., matching `debugRoutes`).
- Sanitize/validate `gc.Param("profile")` before use: reject any value containing `..`, encoded traversal sequences, or characters outside an allow-list of known pprof sub-paths (`profile`, `heap`, `goroutine`, `block`, `mutex`, `threadcreate`, `trace`, `cmdline`, `symbol`), instead of directly interpolating it into the proxied URL.

### Proof of Concept
1. Identify a chainlink node with the web server reachable and at least one registered LOOP plugin (`name`).
2. Without any session cookie or API token, issue:
   `GET /plugins/<name>/debug/pprof/goroutine?debug=2`
   This succeeds and returns full pprof data because `loopRoutes` has no auth middleware.
3. Attempt path pivoting: `GET /plugins/<name>/debug/pprof/../otherpath` — the value of `otherpath` (i.e., everything captured by the `*profile` wildcard) is concatenated verbatim into `http://<loopHost>:<PrometheusPort>/debug/pprof/../otherpath`, sent unauthenticated to the internal plugin listener, demonstrating that the node performs no normalization/containment on attacker-supplied path data before proxying it internally.

### Citations

**File:** core/web/router.go (L76-93)
```go
	engine.Use(helmet.Default())
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

	guiAssetRoutes(engine, config.Insecure().DisableRateLimiting(), app.GetLogger())
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
