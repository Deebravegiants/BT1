### Title
Unauthenticated exposure of LOOP plugin discovery, metrics, and pprof debug endpoints - (File: core/web/router.go)

### Summary
The Chainlink node's HTTP router registers the LOOP plugin service-discovery, metrics, and `pprof` debug endpoints on the top-level `api` route group without any authentication middleware, unlike every other sensitive route in the router which is wrapped in `auth.Authenticate(...)`. This is directly analogous to the Bolt CMS `_profiler`/debug route exposure (CVE-2017-16754): a debug/profiling surface reachable by any unauthenticated client due to missing access-control wiring at route-registration time.

### Finding Description
In `NewRouter`, the top-level `api` group only carries rate limiting and cookie-session middleware — it does not carry `auth.Authenticate`: [1](#0-0) 

Each sub-route-setup function is individually responsible for adding its own auth. `debugRoutes` and `sessionRoutes` correctly create their own authenticated sub-groups, and `v2Routes` wraps its `authv2` group with `auth.Authenticate`: [2](#0-1) 

However, `loopRoutes` registers its handlers directly on the unauthenticated `api` group, with no `auth.Authenticate` wrapper at all: [3](#0-2) 

This exposes four handlers with no access control:
- `GET /discovery` → `discoveryHandler`, which returns Prometheus service-discovery data with plugin names and internal target addresses. [4](#0-3) 
- `GET /plugins/:name/metrics` → `pluginMetricHandler`, which proxies to the plugin's internal `/metrics` endpoint and returns the raw response body. [5](#0-4) 
- `GET /plugins/:name/debug/pprof/*profile` → `pluginPPROFHandler`, which proxies to the plugin's internal `net/http/pprof` endpoints (heap, goroutine, profile, trace, etc.) and returns them verbatim. [6](#0-5) 
- `POST /plugins/:name/debug/pprof/symbol` → `pluginPPROFPOSTSymbolHandler`, same proxying pattern for POST. [7](#0-6) 

The code comments ("unlike discovery, this endpoint is internal btw the node and plugin") indicate the intent was that these are meant to be internal/trusted-network-only, but there is no code-level enforcement of that assumption at the gin router layer — the same architectural mistake as the Bolt advisory, where `_profiler`/debug routes were reachable because the developer didn't attach the access-restriction listener/provider to those specific routes.

### Impact Explanation
An unprivileged, unauthenticated client with network access to the node's web server (which is the same listener serving the authenticated `/v2/*` API and the operator UI) can:
- Enumerate all registered LOOP plugins and their internal Prometheus target addresses via `/discovery`.
- Pull full Prometheus metrics for any named plugin via `/plugins/:name/metrics`, potentially leaking internal operational/telemetry data.
- Pull `pprof` heap dumps, goroutine stacks, and CPU/trace profiles for plugin processes via `/plugins/:name/debug/pprof/*`, which can leak sensitive in-memory data (e.g., addresses, internal state) and enables reconnaissance for further attacks.
- Trigger long-running profile collection (`?seconds=N`) requests against internal plugin processes with no authentication, which is a resource-consumption/DoS vector since these are proxied HTTP calls with attacker-controlled duration.

This matches CWE-732 (Improper Access Control on a debug/profiler-class route) and is reachable directly from an unprivileged HTTP request, without needing any valid session, API token, or role.

### Likelihood Explanation
Likelihood is high wherever the node's web server port is exposed to any network segment reachable by unprivileged actors (which is the same port serving the main authenticated API — there's no separate internal-only listener enforced in this router construction). No credentials, tokens, or special network position are required; a single unauthenticated HTTP GET is sufficient.

### Recommendation
Wrap `loopRoutes` registration in an authenticated (and ideally admin-role-restricted, consistent with `metricRoutes`'s handling under `authv2` at `core/web/router.go:445-446`) route group, e.g. register these on a group protected by `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` (optionally with `auth.RequiresAdminRole`), rather than directly on the unauthenticated `api` group. Alternatively, bind these debug/discovery endpoints to a separate internal-only listener that is not exposed alongside the public API/UI port.

### Proof of Concept
Against a running chainlink node with any registered LOOP plugin (e.g. a median/medianpoc LOOPP), issue unauthenticated requests:
```
curl http://<node-host>:<web-port>/discovery
curl http://<node-host>:<web-port>/plugins/<plugin-name>/metrics
curl http://<node-host>:<web-port>/plugins/<plugin-name>/debug/pprof/heap
curl "http://<node-host>:<web-port>/plugins/<plugin-name>/debug/pprof/profile?seconds=30"
```
No `Authorization`, session cookie, or API key/secret headers are required; all four endpoints return `200 OK` with plugin data because `loopRoutes` never attaches `auth.Authenticate` (contrast with `debugRoutes`/`v2Routes`, which do), as shown in [8](#0-7) .

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

**File:** core/web/router.go (L180-218)
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

func ginHandlerFromHTTP(h http.HandlerFunc) gin.HandlerFunc {
	return func(c *gin.Context) {
		h.ServeHTTP(c.Writer, c.Request)
	}
}

func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
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
