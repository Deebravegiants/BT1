### Title
Missing Authentication on LOOP Plugin Discovery/Metrics/pprof Endpoints Leads to Internal Metadata Disclosure - (File: core/web/router.go)

### Summary
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the top-level `api` router group, which only carries a rate limiter and the gin session middleware — no authentication or authorization check is applied, unlike every other functional route group in the router (`authv2`, `debug`, GraphQL `/query`), all of which wrap `auth.Authenticate(...)`.

### Finding Description
In `core/web/router.go`, `NewRouter` builds the base group `api` with only rate limiting and session-store middleware: [1](#0-0) 

Every other route group is deliberately wrapped in an authentication middleware before being exposed — `debugRoutes` requires a session, `v2Routes` builds `authv2` with `auth.Authenticate(..., AuthenticateByToken, AuthenticateBySession)`, and `/query` requires `auth.AuthenticateGQL`: [2](#0-1) [3](#0-2) 

`loopRoutes`, however, is invoked with the unauthenticated `api` group directly and registers its handlers with no auth wrapper at all: [4](#0-3) [5](#0-4) 

The handlers themselves perform no session/token/role check either — `discoveryHandler` returns Prometheus service-discovery metadata (internal host, exposed port, and every registered LOOPP plugin name/path), and `pluginMetricHandler`/`pluginPPROFHandler`/`pluginPPROFPOSTSymbolHandler` proxy requests to the plugin's internal Prometheus/pprof endpoint and stream the response straight back to the caller: [6](#0-5) [7](#0-6) [8](#0-7) 

This is the same bug class as the DolphinScheduler DataSource API report: an internet-facing API endpoint that should require authenticated/role-checked access instead has no authorization gate at all, so an unprivileged/unauthenticated client can enumerate internal plugin/service metadata directly from the node's HTTP listener.

### Impact Explanation
Any unauthenticated client with network access to the Chainlink node's web server can:
- Enumerate all loaded LOOP plugin names and their internal Prometheus scrape targets/ports via `/discovery`.
- Pull full Prometheus metrics for any named plugin via `/plugins/:name/metrics`, which can reveal internal operational state, counts, labels, and configuration-derived metric names.
- Retrieve pprof profiles (`goroutine`, `heap`, `profile`, `trace`, etc.) for a plugin process via `/plugins/:name/debug/pprof/*`, which can leak stack traces, in-memory data, and internal function names — information that materially aids further attacks and can itself disclose sensitive runtime data.

This matches CWE-863 (missing authorization on a data-disclosing API) and directly maps to the "Critical" DolphinScheduler analog: unauthenticated metadata disclosure of internal service/plugin information via an API path that lacks the authorization checks applied everywhere else in the router.

### Likelihood Explanation
High. The route registration is unconditional (no feature flag or `build.IsDev()` gate as used elsewhere in `v2Routes`), and reaching it only requires an HTTP GET/POST to a known, static path (`/discovery`, `/plugins/<name>/metrics`, `/plugins/<name>/debug/pprof/<profile>`) on the node's already internet-facing web server. No credentials, tokens, or session cookies are needed.

### Recommendation
Wrap `loopRoutes` registration with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` middleware (and an appropriate minimum role, e.g. `auth.RequiresAdminRole` given the operational/debug sensitivity of pprof) used for `authv2`, or move these routes into the `authv2` group entirely, matching how `metricRoutes(authv2)` is already gated for the node's own pprof endpoints.

### Proof of Concept
1. Start a Chainlink node with at least one LOOP plugin registered.
2. Without any authentication, send:
   - `GET http://<node>/discovery` → returns JSON with internal host:port and all plugin names/paths.
   - `GET http://<node>/plugins/<plugin-name>/metrics` → returns the plugin's raw Prometheus metrics.
   - `GET http://<node>/plugins/<plugin-name>/debug/pprof/heap` → returns a heap profile of the plugin process.
3. Compare with any `/v2/...` route, which returns `401 Unauthorized` without valid session/token headers, confirming the `loopRoutes` group is missing the same authorization gate.

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
