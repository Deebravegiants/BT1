Audit Report

## Title
Unauthenticated LOOP plugin discovery, metrics, and pprof/profiling endpoints on the primary web server - ([File: core/web/router.go])

## Summary
`NewRouter` registers `loopRoutes` on the `api` route group, which only applies rate-limiting and session-cookie middleware, with no `auth.Authenticate` wrapper, unlike the functionally equivalent node-level `/v2/debug/pprof/*` routes registered under the `authv2` group. This allows an unauthenticated network client to hit `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` and trigger the node to proxy pprof/profiling and metrics requests to internal LOOP plugin processes without any credential.

## Finding Description
`NewRouter` builds `api := engine.Group(...)` with only `rateLimiter` and `sessions.Sessions` middleware, then calls `loopRoutes(app, api)` on it directly with no `auth.Authenticate` in the chain: [1](#0-0)  `loopRoutes` binds `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly to that group with no additional auth middleware on the routes themselves: [2](#0-1) 

By contrast, the node's own `pprof` endpoints (`metricRoutes`) are deliberately nested inside `authv2`, a group protected by `auth.Authenticate(..., auth.AuthenticateByToken, auth.AuthenticateBySession)`, with the comment "Debug routes accessible via authentication": [3](#0-2) [4](#0-3)  Similarly `/debug/vars` is wrapped in session auth via `debugRoutes`: [5](#0-4) 

The handlers themselves perform no internal authentication or authorization check: `discoveryHandler` reveals internal hostnames/ports for every registered plugin, `pluginMetricHandler` proxies to the plugin's `/metrics` endpoint, and `pluginPPROFHandler`/`pluginPPROFPOSTSymbolHandler` proxy arbitrary `net/http/pprof` calls (with attacker-controlled `debug`, `gc`, `seconds` params) to the plugin's debug port: [6](#0-5) [7](#0-6) [8](#0-7) 

The code base's own test suite confirms these routes work with a plain unauthenticated client (`app.NewHTTPClient(nil)`), receiving `200 OK` for `/discovery` and `/plugins/mockLoopImpl/metrics` without any credential.

## Impact Explanation
This is a genuine authentication-bypass inconsistency: functionally identical debug/profiling capability is protected for the node's own process (`/v2/debug/pprof` requires token/session auth) but left completely open for LOOP plugin processes reachable through the same externally-facing web server. Concrete impacts:
- Information disclosure of internal plugin topology (hostnames, ports, plugin names) via `/discovery`.
- Unauthenticated scraping of internal plugin `/metrics` via `/plugins/:name/metrics`.
- Unauthenticated triggering of CPU/heap/goroutine/trace profiling on plugin processes via `/plugins/:name/debug/pprof/*`, with attacker-controlled `seconds` duration, enabling resource exhaustion (DoS) against the plugin and potential disclosure of in-memory data captured in profiles.

This maps most closely to an authentication-bypass / unauthorized-disclosure class issue on the node's HTTP API. It does not, however, reach into fund movement, key/secret exfiltration, or job-run manipulation — the routes proxy to Prometheus metrics endpoints and Go's `pprof` debug output, which do not inherently expose private keys or secrets. The submitted report's own severity framing acknowledges this ("does not reach the severity of the Milvus CVE... no credential/API-key theft or fund movement").

## Likelihood Explanation
High reachability: whenever LOOP plugins are enabled, these routes are registered unconditionally on the main API group, require no special configuration, and are demonstrably reachable without any token or session cookie in the existing test suite (`TestLoopRegistry`, using `client := app.NewHTTPClient(nil)`).

## Recommendation
Wrap `loopRoutes` registration in an authenticated group (e.g., `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`), consistent with how `/v2/debug/pprof` and `/debug/vars` are protected, or restrict these endpoints to a separate internal-only listener not exposed on the public web server port.

## Proof of Concept
```
curl http://<node-host>:<webserver-port>/discovery
curl http://<node-host>:<webserver-port>/plugins/<pluginName>/metrics
curl "http://<node-host>:<webserver-port>/plugins/<pluginName>/debug/pprof/profile?seconds=60"
```
No `Authorization` header or session cookie is required; this matches the existing `TestLoopRegistry` test pattern using an unauthenticated `client.Get(...)` and receiving `200 OK`.

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

**File:** core/web/loop_registry.go (L52-65)
```go
// discoveryHandler implements service discovery of prom endpoints for LOOPs in the registry
func (l *LoopRegistryServer) discoveryHandler(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	groups := make([]*targetgroup.Group, 0, 1+len(l.registry.List()))

	// add node metrics to service discovery
	groups = append(groups, pluginGroup(l.discoveryHostName, l.exposedPromPort, "/metrics"))

	// add all the plugins
	for _, registeredPlugin := range l.registry.List() {
		group := pluginGroup(l.discoveryHostName, l.exposedPromPort, pluginMetricPath(registeredPlugin.Name))
		group.Labels[LabelMetaPluginName] = model.LabelValue(registeredPlugin.Name)
		groups = append(groups, group)
	}
```

**File:** core/web/loop_registry.go (L96-111)
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
