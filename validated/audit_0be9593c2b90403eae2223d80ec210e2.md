## Title
Unauthenticated exposure of LOOP-plugin debug/pprof and metrics endpoints, bypassing the authentication enforced on the node's own equivalent debug routes - (File: core/web/router.go, core/web/loop_registry.go)

## Summary

### Finding Description
The chainlink node's HTTP router applies authentication inconsistently to functionally equivalent debug/profiling endpoints. The node's own pprof/debug endpoints are gated behind session authentication: `debugRoutes` wraps `/debug/vars` in `auth.Authenticate(..., auth.AuthenticateBySession)` [1](#0-0) , and the `/v2/debug/pprof/*` routes registered by `metricRoutes` are nested inside the `authv2` group, which requires token or session authentication [2](#0-1) .

However, `loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the top-level `api` group, which only carries rate limiting and session-cookie middleware — no `auth.Authenticate` call at all [3](#0-2) . This `api` group is passed unmodified into `loopRoutes(app, api)` from `NewRouter` [4](#0-3) .

These handlers proxy requests to the internal LOOP plugin's own debug/pprof and Prometheus endpoints, forwarding `debug`, `gc`, and `seconds` query parameters and the response body verbatim to the caller [5](#0-4) [6](#0-5) . This is directly analogous to the SiYuan report's core bug class: a route serving the same class of sensitive data (debug/profiling information) as an already access-controlled REST route, but registered with a weaker or absent guard.

### Impact Explanation
An unauthenticated remote client that can reach the node's HTTP API port can:
- Enumerate all registered LOOP plugins and their internal Prometheus scrape targets via `/discovery` [7](#0-6) .
- Pull raw Prometheus metrics for any named plugin via `/plugins/:name/metrics`, which may include internal operational/telemetry data [6](#0-5) .
- Trigger arbitrary pprof profile collection (heap, goroutine, cpu profile via `seconds`, trace) against the internal plugin process via `/plugins/:name/debug/pprof/*profile`, potentially leaking process memory contents, stack traces, and internal state of the LOOP plugin [5](#0-4) .
- Cause resource consumption / DoS by requesting long-duration CPU profiles or traces (`seconds` parameter is attacker-controlled and used to extend the request timeout) [8](#0-7) .

This is confidentiality (and secondarily availability) impact without requiring any credentials, in contrast to the equivalent node-level `/debug/pprof/*` routes which correctly require authentication.

### Likelihood Explanation
High — these routes are registered unconditionally on the main HTTP router with no auth middleware, feature flag, or admin-role check, so any client capable of sending HTTP requests to the node's web server port can reach them directly.

### Recommendation
Wrap `loopRoutes` registrations in the same authentication requirement used elsewhere for debug/pprof endpoints (e.g., `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, ideally combined with `auth.RequiresAdminRole`, mirroring how `metricRoutes(authv2)` and `debugRoutes` are gated), so that `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` are not reachable by unauthenticated callers.

### Proof of Concept
Against a running node with LOOP plugins registered, on the exposed WebServer port:
```
GET http://<node>:<port>/discovery
→ 200, list of plugin names and internal scrape targets (no auth required)

GET http://<node>:<port>/plugins/<plugin-name>/metrics
→ 200, raw Prometheus metrics for the plugin (no auth required)

GET http://<node>:<port>/plugins/<plugin-name>/debug/pprof/heap
→ 200, pprof heap profile of the internal plugin process (no auth required)
```
Compare to the equivalent node-level route, which correctly requires a session/token:
```
GET http://<node>:<port>/v2/debug/pprof/heap
→ 401 Unauthorized (auth.Authenticate enforced via authv2 group)
```

### Citations

**File:** core/web/router.go (L86-93)
```go

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

**File:** core/web/loop_registry.go (L132-148)
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
