## Title
Missing Authorization on LOOP Plugin Discovery/Metrics/pprof Debug Routes - (File: `core/web/router.go`)

### Summary
The GeoServer advisory (CVE-2025-27505) describes a case where security filters were applied to the primary `rest` API paths but a whole class of sibling routes escaped the authorization layer entirely, exposing internal information to unauthenticated clients. Chainlink's node HTTP router has an analogous gap: the `loopRoutes` group, which exposes Prometheus service-discovery data and full pprof debug/profiling endpoints for LOOP plugins, is registered on the same public API engine with **no authentication middleware at all**, while the functionally equivalent node-level pprof endpoints are correctly gated behind session authentication.

### Finding Description
In `NewRouter`, the top-level route groups are wired up as: [1](#0-0) 

`debugRoutes` wraps `/debug/vars` in `auth.Authenticate(..., auth.AuthenticateBySession)`: [2](#0-1) 

Node-level pprof handlers under `/v2/...` are likewise gated by full session/token authentication via `metricRoutes(authv2)`, called only inside the authenticated `authv2` block: [3](#0-2) [4](#0-3) 

However, `loopRoutes` is registered directly on the unauthenticated `api` group (only rate-limiting/session-cookie middleware is applied, not credential checks), exposing four handlers with zero authorization: [5](#0-4) 

These handlers return real plugin metadata (`discoveryHandler`), proxy live Prometheus `/metrics` for arbitrary named plugins (`pluginMetricHandler`), and fully proxy `net/http/pprof` debug endpoints — including `heap`, `goroutine`, `trace`, `profile`, and `symbol` — to the LOOP plugin's internal HTTP server: [6](#0-5) [7](#0-6) [8](#0-7) 

Because these routes hang off the same `gin.Engine`/port used for the node's authenticated REST API, and are registered with no `auth.Authenticate(...)` wrapper (unlike every other sensitive route in `router.go`), any unauthenticated remote client can reach them directly by path, mirroring the GeoServer flaw where certain path variants bypassed the intended authorization filter.

### Impact Explanation
pprof endpoints (`heap`, `goroutine`, `profile`, `trace`) can leak runtime memory contents, stack traces, and internal state of LOOP plugin processes to any unauthenticated network client — this can include sensitive material handled by the plugin process and internal topology/service information via `/discovery`. This matches CWE-862 (Missing Authorization) and the "unauthenticated information disclosure via bypassed REST index/subpaths" pattern in the GeoServer advisory: unprivileged actors gain access to internal diagnostic/administrative surface that the rest of the router explicitly protects.

### Likelihood Explanation
High: no special conditions are needed — the routes are always registered on the main engine whenever a Chainlink node starts (`loopRoutes(app, api)` is called unconditionally in `NewRouter`), and reachability only requires network access to the standard node API port, identical to any other unauthenticated GET/POST request.

### Recommendation
Wrap the `loopRoutes` group with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` middleware used elsewhere (e.g., as done for `metricRoutes(authv2)`), or move these endpoints to an internal-only listener/port that is not exposed alongside the public API, consistent with the comment "this endpoint is internal btw the node and plugin" in `core/web/loop_registry.go`.

### Proof of Concept
1. Start a Chainlink node with any LOOP plugin registered.
2. Without any API key/session cookie, issue:
   - `GET /discovery` — returns plugin names/service-discovery targets.
   - `GET /plugins/<name>/debug/pprof/heap` — returns a full heap dump of the plugin process.
   - `GET /plugins/<name>/debug/pprof/goroutine?debug=2` — returns full goroutine stack traces.
3. All requests succeed with `200 OK` and no authentication challenge, unlike `/debug/vars` or `/v2/debug/pprof/*`, which return `401 Unauthorized` without valid credentials.

### Citations

**File:** core/web/router.go (L87-92)
```go
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

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/loop_registry.go (L52-81)
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

	b, err := l.jsonMarshalFn(groups)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		_, err = w.Write([]byte(err.Error()))
		if err != nil {
			l.logger.Error(err)
		}
		return
	}
	_, err = w.Write(b)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		l.logger.Error(err)
	}
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

**File:** core/web/loop_registry.go (L168-188)
```go
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
