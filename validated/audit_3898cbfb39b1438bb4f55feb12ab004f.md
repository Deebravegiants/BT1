## Title
Unauthenticated LOOP Plugin Discovery/Metrics/pprof Endpoints Skip Session/Token Authentication - (File: core/web/router.go, core/web/loop_registry.go)

### Summary
`core/web/router.go`'s `NewRouter` wires `loopRoutes(app, api)` onto the top-level `api` route group, which only has rate-limiting and session-store middleware attached — no `auth.Authenticate()` call is present [1](#0-0) . `loopRoutes` then registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on that unauthenticated group [2](#0-1) . This is directly analogous to the OpenEMR bug: within the same route-registration file, sibling debug/pprof routes registered under the authenticated `authv2` group (`metricRoutes(authv2)` at the end of `v2Routes`) require `auth.Authenticate(..., auth.AuthenticateByToken, auth.AuthenticateBySession)`, but the LOOP-plugin equivalents skip that check entirely [3](#0-2) [4](#0-3) .

### Finding Description
`debugRoutes` (top-level `/debug/vars`) and the `/v2/debug/pprof/*` routes registered via `metricRoutes(authv2)` are both properly gated behind `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` / the authenticated `authv2` group [5](#0-4) . However `loopRoutes`, which exposes functionally equivalent debug/profiling data for LOOP plugins, is mounted on the bare `api` group that has no authentication middleware at all [6](#0-5) .

The handlers backing these routes — `discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, and `pluginPPROFPOSTSymbolHandler` — perform no additional authorization check themselves; they simply proxy the request to the internal LOOP plugin process based on the `:name` path parameter [7](#0-6) [8](#0-7) . `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` forward attacker-controlled `debug`, `gc`, and `seconds` query parameters straight into the internal pprof request URL and timeout calculation [9](#0-8) .

### Impact Explanation
Any unauthenticated client with network access to the node's HTTP API can:
- Enumerate internal plugin names, hostnames, and Prometheus ports via `/discovery` and `/plugins/:name/metrics`.
- Trigger CPU/heap/goroutine profiling dumps of internal LOOP plugin processes via `/plugins/:name/debug/pprof/*profile`, potentially leaking internal memory/state or causing resource exhaustion by supplying a large `seconds` value for CPU profiling.
- Reach internal-only plugin infrastructure that was intended to be accessible only "internal btw the node and plugin" per the code comments, bypassing the node's authentication boundary entirely.

This mirrors the OpenEMR CVE's impact class: authenticated/internal-only functionality reachable by an unprivileged actor because the authorization middleware applied to sibling routes was omitted for this route group.

### Likelihood Explanation
High — no authentication token, session, or role is required; the routes are reachable directly on the node's public HTTP listener alongside all other `/v2/*` API traffic, and the route registration omits the same `auth.Authenticate(...)` call used by the near-identical `/v2/debug/pprof/*` routes in the same file.

### Recommendation
Wrap `loopRoutes(app, api)` registration with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` middleware (and an appropriate role check, e.g. `auth.RequiresAdminRole`) that is already used for `metricRoutes(authv2)` and `debugRoutes`, so that `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` require the same authenticated session or API token as other debug endpoints.

### Proof of Concept
```
# No API key/session cookie required:
curl http://<node-host>:<port>/discovery
curl http://<node-host>:<port>/plugins/<plugin-name>/metrics
curl "http://<node-host>:<port>/plugins/<plugin-name>/debug/pprof/profile?seconds=60"
```
Each request succeeds without any `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret`, API token header, or session cookie, whereas the equivalent `/v2/debug/pprof/*` route under `authv2` returns `401 Unauthorized` without credentials [5](#0-4) .

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

**File:** core/web/router.go (L445-446)
```go
		// Debug routes accessible via authentication
		metricRoutes(authv2)
```

**File:** core/web/loop_registry.go (L52-93)
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

func pluginGroup(hostName string, port int, path string) *targetgroup.Group {
	return &targetgroup.Group{
		Targets: []model.LabelSet{
			// target address will be called by external prometheus
			{model.AddressLabel: model.LabelValue(fmt.Sprintf("%s:%d", hostName, port))},
		},
		Labels: map[model.LabelName]model.LabelValue{
			model.MetricsPathLabel: model.LabelValue(path),
		},
	}
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
