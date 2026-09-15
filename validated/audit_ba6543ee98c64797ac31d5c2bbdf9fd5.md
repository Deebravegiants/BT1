The claim is confirmed by direct code inspection.

Audit Report

## Title
Unauthenticated pprof/metrics debug endpoints reachable via `loopRoutes`, bypassing the authentication constraints applied to the equivalent `/v2/debug/pprof` endpoints - (File: `core/web/router.go`)

## Summary
`NewRouter` mounts `loopRoutes(app, api)` directly on the base `api` group, which only has rate-limiting and session-cookie middleware attached and no authentication requirement, whereas the equivalent built-in Go pprof endpoints registered by `metricRoutes` are only reachable through the `authv2` group gated by `auth.Authenticate(... AuthenticateByToken, AuthenticateBySession)`. This allows any unauthenticated network client that can reach the node's HTTP listener to enumerate LOOP plugins and pull their metrics/pprof profiling data with no credentials.

## Finding Description
The base `api` group is constructed with only rate limiting and session middleware, no auth requirement: [1](#0-0) 

`loopRoutes` is called directly on this unauthenticated group, alongside other route groups that internally construct their own authenticated sub-groups: [2](#0-1) 

`loopRoutes` itself registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` with no auth middleware: [3](#0-2) 

In contrast, the standard Go pprof endpoints registered by `metricRoutes` are only reachable via the `authv2` group, which requires token or session authentication: [4](#0-3) [5](#0-4) [6](#0-5) 

The plugin pprof handlers forward arbitrary pprof requests (including `debug`, `gc`, and `seconds` query parameters) to the internal LOOP plugin process and return the raw response body, with no ownership/role check anywhere in the call chain: [7](#0-6) [8](#0-7) 

I confirmed via `grep_search` and commit history that this is the current, unmodified state of the code (single "Initial commit", no subsequent fix), and `SECURITY.md` contains no exclusion specific to this endpoint class.

## Impact Explanation
An unauthenticated client reaching the node's web server can enumerate loaded LOOP plugins via `/discovery`, pull runtime metrics via `/plugins/:name/metrics`, and pull full pprof profiles (heap, goroutine, CPU profile, trace) via `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` — the same class of sensitive debug data that is explicitly authenticated when exposed through `/v2/debug/pprof/*`. This is an authentication bypass for a security control class (profiling/debug data protection) applied inconsistently across two equivalent code paths, matching the CWE-288 "Authentication Bypass Using an Alternate Path or Channel" pattern. It can leak internal memory/state of plugin processes and enable resource exhaustion via attacker-controlled `seconds` on CPU profiling.

## Likelihood Explanation
High for any deployment where the node's HTTP listener (the same one serving `/v2` API and UI) is network-reachable, since no token or session cookie is required — only a plugin name, itself discoverable via the equally unauthenticated `/discovery` endpoint.

## Recommendation
Register `loopRoutes` behind the same authentication middleware used for `metricRoutes`/`authv2` (e.g., `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`), or move the route registration inside an authenticated group, so plugin metrics/pprof-forwarding endpoints require the same credentials as the built-in `/v2/debug/pprof` endpoints.

## Proof of Concept
1. Start a chainlink node with at least one LOOP plugin registered.
2. Without any session cookie or API token: `curl http://<node>:<port>/discovery` — returns plugin names/ports.
3. Using a discovered plugin name: `curl http://<node>:<port>/plugins/<name>/debug/pprof/heap?debug=1` — `pluginPPROFHandler` (core/web/loop_registry.go:150-166) forwards the request to the plugin's debug pprof endpoint and returns profile data with no authentication check anywhere in `loopRoutes` → `pluginPPROFHandler` → `doRequest`.

### Citations

**File:** core/web/router.go (L78-85)
```go
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)
```

**File:** core/web/router.go (L87-91)
```go
	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)
```

**File:** core/web/router.go (L185-199)
```go
func metricRoutes(r *gin.RouterGroup) {
	pprofGroup := r.Group("/debug/pprof")
	pprofGroup.GET("/", ginHandlerFromHTTP(pprof.Index))
	pprofGroup.GET("/cmdline", ginHandlerFromHTTP(pprof.Cmdline))
	pprofGroup.GET("/profile", ginHandlerFromHTTP(pprof.Profile))
	pprofGroup.POST("/symbol", ginHandlerFromHTTP(pprof.Symbol))
	pprofGroup.GET("/symbol", ginHandlerFromHTTP(pprof.Symbol))
	pprofGroup.GET("/trace", ginHandlerFromHTTP(pprof.Trace))
	pprofGroup.GET("/allocs", ginHandlerFromHTTP(pprof.Handler("allocs").ServeHTTP))
	pprofGroup.GET("/block", ginHandlerFromHTTP(pprof.Handler("block").ServeHTTP))
	pprofGroup.GET("/goroutine", ginHandlerFromHTTP(pprof.Handler("goroutine").ServeHTTP))
	pprofGroup.GET("/heap", ginHandlerFromHTTP(pprof.Handler("heap").ServeHTTP))
	pprofGroup.GET("/mutex", ginHandlerFromHTTP(pprof.Handler("mutex").ServeHTTP))
	pprofGroup.GET("/threadcreate", ginHandlerFromHTTP(pprof.Handler("threadcreate").ServeHTTP))
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

**File:** core/web/router.go (L445-446)
```go
		// Debug routes accessible via authentication
		metricRoutes(authv2)
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
