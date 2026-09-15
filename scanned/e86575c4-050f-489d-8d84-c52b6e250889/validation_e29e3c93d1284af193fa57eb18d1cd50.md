This confirms it: `debugRoutes` explicitly requires session auth (`core/web/router.go:180-183`), and the node's own `/v2/debug/pprof/*` routes are gated behind `authv2` with session/token auth (`core/web/router.go:245-248,446`). The LOOP plugin equivalent, however, is wired up with no auth gate at all.

### Title
Unauthenticated disclosure of internal plugin names and Go runtime debug/pprof data via `/discovery` and `/plugins/:name/*` - (File: `core/web/loop_registry.go`)

### Summary
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the top-level `api` router group, which only carries a rate limiter and session-cookie middleware — no authentication check. [1](#0-0) [2](#0-1) 

Compare this to the node's own equivalent debug endpoints, which are explicitly gated: `/debug/vars` requires session auth, and `/v2/debug/pprof/*` sits under `authv2` requiring token or session auth. [3](#0-2) [4](#0-3) 

### Finding Description
`discoveryHandler` enumerates every LOOP plugin registered in `l.registry.List()` and returns their exact names in a Prometheus service-discovery JSON body to any caller, without checking session/token identity. [5](#0-4) 

Using a plugin name obtained from `/discovery` (or guessed, since plugin names are typically well-known, e.g. `median`, `mercury`, `ocr2keeper`), an unauthenticated caller can hit `/plugins/:name/debug/pprof/*profile`, which proxies straight to the plugin's internal `/debug/pprof/...` endpoint (heap dumps, goroutine stacks, 30-second CPU profiles, full symbol resolution via POST) with only an existence check on the plugin name (`l.registry.Get(pluginName)`) — no authentication or authorization gate. [6](#0-5) [7](#0-6) 

The same missing gate applies to `pluginMetricHandler`, which proxies to the plugin's internal `/metrics` endpoint. [8](#0-7) 

This is structurally the same bug class as the Concrete CMS report: an endpoint parameterized by an object identifier (here, plugin name instead of file ID) returns internal system data to any GET/POST request because the route was never placed behind the application's authentication middleware, unlike its sibling routes that perform the identical function.

### Impact Explanation
Goroutine dumps and heap profiles from LOOP plugins can leak internal state such as stack traces (revealing code paths, function arguments in some cases), memory contents, and configuration details (e.g., internal hostnames, ports via `EnvCfg.PrometheusPort`), all without any credentials. The `/discovery` endpoint itself telegraphs exactly which plugin names exist, removing any need to guess. CPU profiling (`/debug/pprof/profile?seconds=N`) can also be trivially abused as a low-cost denial-of-service/resource-exhaustion primitive since duration and timeout are attacker controlled. [9](#0-8) 

### Likelihood Explanation
High — the routes are registered on the web server's main listener with no auth middleware in the chain, requiring nothing beyond network reachability to the node's HTTP port (the same port/listener serving the authenticated `/v2` API). [10](#0-9) 

### Recommendation
Wrap `loopRoutes` registration in an authenticated group, consistent with `debugRoutes`/`metricRoutes`, e.g. `r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession))` before calling `loopRoutes(app, authGroup)`, or move it under the existing `authv2` group alongside `metricRoutes`.

### Proof of Concept
1. `GET http://<node>/discovery` (no credentials) → returns JSON listing every registered LOOP plugin name and its metrics path.
2. `GET http://<node>/plugins/<name>/debug/pprof/heap?debug=1` (no credentials) → returns a full heap profile of the plugin process.
3. `GET http://<node>/plugins/<name>/debug/pprof/profile?seconds=30` (no credentials) → forces a 30-second CPU profile capture, usable repeatedly for resource exhaustion.

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

**File:** core/web/loop_registry.go (L53-65)
```go
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
