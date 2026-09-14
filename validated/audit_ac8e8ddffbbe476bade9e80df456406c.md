Based on my investigation, I found a concrete unauthenticated pprof-proxy analog in the chainlink web router.

### Title
Unauthenticated pprof profiling of LOOP plugin processes via `/plugins/:name/debug/pprof/*` - (File: core/web/router.go)

### Summary
The chainlink node's main HTTP API router registers `/plugins/:name/debug/pprof/*profile` and `/plugins/:name/debug/pprof/symbol` routes on the top-level `api` group with no authentication middleware, unlike the sibling `/debug/vars` route which is explicitly wrapped in `auth.Authenticate`.

### Finding Description
`NewRouter` builds an `api` group with only rate-limiting and session-cookie middleware (no auth check) and calls `loopRoutes(app, api)` on it directly: [1](#0-0) 

`loopRoutes` registers the plugin pprof-forwarding endpoints on that unauthenticated group: [2](#0-1) 

Compare this to `debugRoutes`, which deliberately wraps `/debug/vars` in session authentication: [3](#0-2) 

The unauthenticated `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` construct a URL to the internal LOOP plugin's own `net/http/pprof` endpoint (`/debug/pprof/<profile>` including `heap`, `goroutine`, `profile`, `trace`) and proxy the request/response verbatim to the caller: [4](#0-3) [5](#0-4) 

This is the same bug class as the Tilt advisory: full `net/http/pprof` handler surface (heap/goroutine memory dumps, CPU `profile`, `trace`) reachable without authentication, here reached one hop through a proxy handler rather than a direct blank import, but with identical impact — an unauthenticated caller can dump plugin process memory or hold it under profiling/tracing for an attacker-chosen duration.

Note: I could not find where `metricRoutes` (which registers full pprof handlers `pprof.Index`, `pprof.Profile`, `pprof.Trace`, `pprof.Symbol`, etc. directly on `/debug/pprof`) is actually invoked — it is defined at [6](#0-5)  but is not called anywhere I could locate, including in `NewRouter`, so that particular direct-pprof-mount function appears to be dead code in this snapshot. My confirmed, reachable analog is the plugin pprof proxy in `loopRoutes`.

### Impact Explanation
Any network caller who can reach the node's main API listener can retrieve heap/goroutine memory dumps or hold a registered LOOP plugin process under CPU profiling/tracing without any credentials, exactly mirroring the CWE-200 memory-disclosure and availability-degradation impact described in the Tilt advisory. Depending on what the LOOP plugin process holds in memory (keys, internal state), this could leak sensitive data, and the `seconds`-controlled `/profile` and `/trace` calls can be used to degrade plugin performance.

### Likelihood Explanation
Likelihood depends on whether the node's web server is exposed beyond loopback (the same condition called out in the Tilt advisory). The `api` group is the node's primary public API surface (it also hosts `/health`, `/sessions`, `/v2/*`), so if the node's HTTP listener is reachable at all — which is the normal deployment case for chainlink nodes serving the operator UI/API — these unauthenticated plugin pprof endpoints are reachable by the same unprivileged caller with zero additional preconditions (only requiring at least one LOOP plugin to be registered, `l.registry.Get(pluginName)` returning true).

### Recommendation
Wrap `loopRoutes` (or at minimum the `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` routes) in the same `auth.Authenticate(...)` middleware used for `debugRoutes` and the `authv2` group, so pprof forwarding requires a valid session/token and appropriate role before proxying to a plugin's profiling endpoints.

### Proof of Concept
1. Start a chainlink node with at least one LOOP plugin registered (so `l.registry.Get(pluginName)` succeeds).
2. Without any session cookie or API token, send `GET /plugins/<pluginName>/debug/pprof/heap` to the node's HTTP API port.
3. The request is routed through `loopRoutes` → `pluginPPROFHandler` → proxied to the plugin's internal `/debug/pprof/heap`, and the raw heap dump is returned to the unauthenticated caller, as shown in [7](#0-6) .

### Citations

**File:** core/web/router.go (L78-91)
```go
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

**File:** core/web/loop_registry.go (L150-188)
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

func (l *LoopRegistryServer) pluginPPROFPOSTSymbolHandler(gc *gin.Context) {
	pluginName := gc.Param("name")
	p, ok := l.registry.Get(pluginName)
	if !ok {
		gc.Data(http.StatusNotFound, "text/plain", fmt.Appendf(nil, "plugin %q does not exist", html.EscapeString(pluginName)))
		return
	}

	// unlike discovery, this endpoint is internal btw the node and plugin
	pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/symbol", l.loopHostName, p.EnvCfg.PrometheusPort)
	urlVals, timeout := pprofURLVals(gc)
	if s := urlVals.Encode(); s != "" {
		pluginURL += "?" + s
	}
	body, err := io.ReadAll(gc.Request.Body)
	if err != nil {
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "error reading plugin pprof request body: %s", err))
		return
	}
	l.doRequest(gc, "POST", pluginURL, bytes.NewReader(body), timeout, pluginName)
}
```

**File:** core/web/loop_registry.go (L190-215)
```go
func (l *LoopRegistryServer) doRequest(gc *gin.Context, method, url string, body io.Reader, timeout time.Duration, pluginName string) {
	ctx, cancel := context.WithTimeout(gc.Request.Context(), timeout)
	defer cancel()
	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "error creating plugin pprof request: %s", err))
		return
	}
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		msg := "plugin pprof handler failed to post plugin url " + html.EscapeString(url)
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}
	defer res.Body.Close()
	b, err := io.ReadAll(res.Body)
	if err != nil {
		msg := fmt.Sprintf("error reading plugin %q pprof", html.EscapeString(pluginName))
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}

	gc.Data(http.StatusOK, "text/plain", b)
}
```
