### Title
Unauthenticated exposure of LOOP plugin debug/pprof and metrics endpoints - (File: core/web/router.go, core/web/loop_registry.go)

### Summary
The chainlink node's `/plugins/:name/debug/pprof/*profile`, `/plugins/:name/debug/pprof/symbol`, `/plugins/:name/metrics`, and `/discovery` routes are mounted on the top-level, unauthenticated `api` router group, unlike the node's own `/debug/pprof/*` and `/debug/vars` routes which are explicitly gated behind session/token authentication. This mirrors the SimpleSAMLphp `phpinfo()` bug class: a debug/diagnostic endpoint intended for operators is reachable without any authentication check, disclosing internal runtime and host information to any unprivileged network client.

### Finding Description
`NewRouter` builds an `api` route group protected only by rate limiting and cookie session middleware (no authentication check), and mounts `loopRoutes` directly on it: [1](#0-0) 

`loopRoutes` registers plugin discovery, metrics, and pprof-forwarding endpoints with no auth middleware at all: [2](#0-1) 

By contrast, the node's own `/debug/pprof` routes (`metricRoutes`) are deliberately placed inside `authv2`, which requires `auth.Authenticate` with token/session credentials: [3](#0-2) [4](#0-3) 

The plugin pprof handler forwards attacker-controlled query parameters (`debug`, `gc`, `seconds`) directly to an internal LOOP plugin's `/debug/pprof/<profile>` and `/debug/pprof/symbol` endpoints and streams the raw response back to the caller, with no authentication check performed on the incoming gin request: [5](#0-4) [6](#0-5) 

Similarly, `pluginMetricHandler` and `discoveryHandler` expose plugin names, ports, and metrics without authentication: [7](#0-6) [8](#0-7) 

### Impact Explanation
An unauthenticated attacker who can reach the node's HTTP API can pull heap dumps, goroutine stacks, CPU/allocation/block/mutex profiles, and symbol tables from any registered LOOP plugin, as well as enumerate registered plugin names/ports via `/discovery` and `/plugins/:name/metrics`. pprof heap/goroutine dumps can leak process memory contents (potential secrets, keys, internal addresses) and internal topology information, aiding further attacks — directly analogous to the `phpinfo()` information disclosure in the reported CVE, though the specific data exposed differs (plugin runtime internals vs. PHP host info).

### Likelihood Explanation
This is reachable by any unprivileged client capable of sending unauthenticated HTTP GET/POST requests to the node's web server — no credentials, tokens, or special network position are required, and the affected routes are always registered when `loopRoutes` runs (it is unconditionally called in `NewRouter`), not gated behind any feature flag.

### Recommendation
Move `loopRoutes` registration to an authenticated (and ideally admin-only) router group, consistent with `metricRoutes`, e.g. wrap it with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` and `auth.RequiresAdminRole` before exposing `/discovery`, `/plugins/:name/metrics`, and the pprof-forwarding routes.

### Proof of Concept
1. Start a chainlink node with at least one LOOP plugin registered (e.g. a Solana/EVM LOOPP).
2. Without any session cookie or API token, send: `GET http://<node>:<port>/discovery` — receive plugin names/ports.
3. Send: `GET http://<node>:<port>/plugins/<name>/debug/pprof/heap?debug=1` — receive a full heap dump of the plugin process without authentication, whereas `GET /debug/pprof/heap` (node's own profile) correctly returns 401 Unauthorized as shown in `TestShell_Profile_Unauthenticated`-style tests.

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

**File:** core/web/router.go (L180-199)
```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", expvar.Handler())
}

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
