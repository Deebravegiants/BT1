Audit Report

## Title
Unauthenticated access to LOOP plugin metrics and pprof profiling endpoints - (`core/web/router.go`)

## Summary
`NewRouter` registers `loopRoutes` on the plain `api` route group, which only carries rate-limiting and session-store middleware, not authentication. This exposes `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` to any unauthenticated network client, unlike every other debug/profiling surface in the router.

## Finding Description
In `core/web/router.go`, the `api` group is created with only rate limiting and cookie-session middleware: [1](#0-0) . `loopRoutes` is called directly on this group and registers its handlers with no `auth.Authenticate` wrapper: [2](#0-1) .

By contrast, the node's own `/debug/vars` route is explicitly wrapped in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`: [3](#0-2) , and the node's own `/debug/pprof/*` handlers (`metricRoutes`) are only mounted inside the `authv2` group, which requires token or session authentication: [4](#0-3)  together with the mounting call at line 445 area (`metricRoutes(authv2)`). This shows a clear inconsistency: the LOOP-plugin proxy routes bypass the same authentication pattern applied elsewhere in the same file.

The `pluginMetricHandler` proxies the plugin's Prometheus `/metrics` endpoint and returns the raw body to the unauthenticated caller: [5](#0-4) . The `pluginPPROFHandler` proxies arbitrary pprof profile paths (heap, goroutine, cpu, etc.), with the `seconds` query parameter directly influencing the request timeout: [6](#0-5) . Both are registered without any authentication guard.

## Impact Explanation
An unauthenticated actor with network access to the node's web server can retrieve heap/goroutine/CPU pprof profiles and Prometheus metrics for any registered LOOP plugin merely by knowing/guessing a plugin name. Heap and goroutine dumps can expose sensitive in-process data, and the discovery/metrics responses leak internal topology (plugin names, ports, hostnames) that should require credentials to access — this exceeds the SECURITY.md exclusion for "non-confidential information disclosure" (IPs/server names/stack traces), since profiling dumps can carry memory contents. This maps to an in-scope "node API authentication bypass" impact class, comparable to the CVE-2025-68435 bug class cited in the report.

## Likelihood Explanation
High. The affected paths are always registered on the base router with no additional precondition beyond network reachability to the node's web server — the same reachability assumption used for the rest of the `/v2/*` API, which is normally protected by `auth.Authenticate`. No credentials, session cookie, or token are needed to trigger the routes, matching the report's PoC of a bare `curl` request.

## Recommendation
Wrap the `loopRoutes` registration with the same authentication middleware used for `debugRoutes`/`metricRoutes(authv2)` — e.g., mount it on the `authv2` group or explicitly wrap with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` — so plugin metrics/pprof are gated the same way as the node's own debug/pprof endpoints.

## Proof of Concept
Against a running node with a registered LOOP plugin, with no `Cookie`/`X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` header supplied:
```
curl http://<node-host>:6688/discovery
curl http://<node-host>:6688/plugins/<plugin-name>/metrics
curl "http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/heap?debug=1"
curl "http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/goroutine?debug=2"
```
All requests succeed and return plugin data because `loopRoutes` (`core/web/router.go:230-236`) is registered directly on the unauthenticated `api` group, unlike `debugRoutes` and `metricRoutes(authv2)` which require authentication.

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

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/loop_registry.go (L96-128)
```go
func (l *LoopRegistryServer) pluginMetricHandler(gc *gin.Context) {
	pluginName := gc.Param("name")
	p, ok := l.registry.Get(pluginName)
	if !ok {
		gc.Data(http.StatusNotFound, "text/plain", fmt.Appendf(nil, "plugin %q does not exist", html.EscapeString(pluginName)))
		return
	}

	// unlike discovery, this endpoint is internal btw the node and plugin
	pluginURL := fmt.Sprintf("http://%s:%d/metrics", l.loopHostName, p.EnvCfg.PrometheusPort)
	req, err := http.NewRequestWithContext(gc.Request.Context(), http.MethodGet, pluginURL, nil)
	if err != nil {
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "error creating plugin metrics request: %s", err))
		return
	}
	res, err := l.promClient.Do(req)
	if err != nil {
		msg := "plugin metric handler failed to get plugin url " + html.EscapeString(pluginURL)
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}
	defer res.Body.Close()
	b, err := io.ReadAll(res.Body)
	if err != nil {
		msg := fmt.Sprintf("error reading plugin %q metrics", html.EscapeString(pluginName))
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}

	gc.Data(http.StatusOK, "text/plain", b)
}
```

**File:** core/web/loop_registry.go (L132-166)
```go
func pprofURLVals(gc *gin.Context) (urlVals url.Values, timeout time.Duration) {
	urlVals = make(url.Values)
	if db, ok := gc.GetQuery("debug"); ok {
		urlVals.Set("debug", db)
	}
	if gc, ok := gc.GetQuery("gc"); ok {
		urlVals.Set("gc", gc)
	}
	timeout = PPROFOverheadSeconds * time.Second
	if sec, ok := gc.GetQuery("seconds"); ok {
		urlVals.Set("seconds", sec)
		if i, err := strconv.Atoi(sec); err == nil {
			timeout = time.Duration(i+PPROFOverheadSeconds) * time.Second
		}
	}
	return urlVals, timeout
}

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
