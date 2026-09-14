### Title
Unauthenticated DoS via `/plugins/:name/debug/pprof/*profile` proxy endpoint — ([File: core/web/router.go])

### Summary
The `loopRoutes` handler group, which exposes plugin profiling/metrics endpoints including a pprof proxy, is registered on the base `api` router group that only applies rate limiting and session middleware — not authentication. This mirrors the OpenChamber bug class: a sensitive/administrative HTTP endpoint reachable by an unauthenticated remote client because it was wired into the router before/outside the authentication middleware chain, enabling denial-of-service.

### Finding Description
In `NewRouter`, the top-level `api` group is created with only rate limiting and cookie session middleware attached: [1](#0-0) 

`loopRoutes(app, api)` is called directly on this unauthenticated `api` group, alongside `debugRoutes`, `healthRoutes`, `sessionRoutes`, and `v2Routes` — but unlike `debugRoutes` (which wraps its group with `auth.Authenticate(...)`) and `metricRoutes` (which is only mounted inside the authenticated `authv2` group), `loopRoutes` receives no auth wrapper at all: [2](#0-1) 

Compare this to the identical pprof handler set exposed via `metricRoutes`, which is deliberately nested inside the authenticated `authv2` group: [3](#0-2) 

The `loopRoutes` group exposes `pluginPPROFHandler`, which proxies attacker-controlled query parameters (`seconds`, `debug`, `gc`) directly to a LOOP plugin's `/debug/pprof/<profile>` endpoint and blocks the request goroutine for up to `seconds + 30` seconds: [4](#0-3) 

Because this route is unauthenticated, any unprivileged remote client can issue repeated `GET /plugins/:name/debug/pprof/profile?seconds=<large>` requests, causing sustained CPU-profiling load on the backing LOOP plugin process and holding open many long-lived server-side connections/goroutines — a resource-exhaustion analog to the OpenChamber shutdown-via-unauthenticated-route bug class.

### Impact Explanation
An unauthenticated attacker can force the node's plugin (LOOP) processes into sustained CPU/goroutine profiling load with attacker-chosen duration and repeat this without any credential, degrading LOOP plugin performance and potentially exhausting HTTP server resources/connections — a remote, unauthenticated availability impact (VA:H-style), consistent with the reported bug class even though the specific mechanism differs from the original `/api/system/shutdown` case.

### Likelihood Explanation
High: the route is reachable with a simple unauthenticated `GET` request to a known, statically-defined path (`/plugins/:name/debug/pprof/*profile`), requires no special network position, and the plugin name/profile type can be discovered via the equally unauthenticated `discoveryHandler` (`GET /discovery`), which enumerates all registered plugin names. [5](#0-4) 

### Recommendation
Wrap `loopRoutes` registration with the same `auth.Authenticate(...)` middleware used for `debugRoutes` and the authenticated `authv2` pprof routes, or otherwise gate access (e.g., require admin/edit role) before forwarding pprof requests to LOOP plugins, and apply a hard server-side cap on the proxied `seconds` parameter regardless of authentication status.

### Proof of Concept
1. Start a Chainlink node with at least one registered LOOP plugin.
2. Without any session cookie or API token, send: `GET /discovery` to enumerate plugin names.
3. Send repeated unauthenticated requests: `GET /plugins/<name>/debug/pprof/profile?seconds=60`.
4. Observe the request is served (no `401 Unauthorized`) and the backing plugin process is held busy profiling for the requested duration; repeating this from multiple concurrent connections degrades plugin/node responsiveness without any authentication.

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

**File:** core/web/router.go (L180-236)
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

func healthRoutes(app chainlink.Application, r *gin.RouterGroup) {
	hc := HealthController{app}
	r.GET("/readyz", hc.Readyz)
	r.GET("/public-readyz", hc.PublicReadyz)
	r.GET("/health", hc.Health)
	r.GET("/health.txt", func(context *gin.Context) {
		context.Request.Header.Set("Accept", gin.MIMEPlain)
	}, hc.Health)
}

func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
}
```

**File:** core/web/router.go (L441-447)
```go
		vault := VaultController{app}
		authv2.POST("/vault/dkg_results/verify", auth.RequiresEditRole(vault.VerifyDKGResult))
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
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

**File:** core/web/loop_registry.go (L130-166)
```go
const PPROFOverheadSeconds = 30

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
