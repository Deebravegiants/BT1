The claim is fully verified against the actual code. Let me confirm the exact behavior is as described with no hidden mitigations.Audit Report

## Title
Unauthenticated Disclosure of Internal Node Info and Full pprof Debug Data via LOOP Registry Routes - (File: core/web/router.go, core/web/loop_registry.go)

## Summary
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the top-level `api` route group in `NewRouter`, with no authentication middleware applied, while every other sensitive route group (`debugRoutes`, `authv2` in `v2Routes`) is explicitly wrapped in `auth.Authenticate(...)`. This allows an unauthenticated remote client to enumerate registered LOOP plugins and pull their Prometheus metrics and full pprof debug data (heap, goroutine, profile, symbol) from any Chainlink node exposing its web server.

## Finding Description
In `core/web/router.go`, `NewRouter` creates the `api` gin group with only rate limiting and session middleware (no auth), then registers route groups on it: [1](#0-0) 

`debugRoutes` explicitly wraps `/debug/vars` with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`: [2](#0-1) 

`v2Routes` splits into an explicitly unauthenticated group (`unauthedv2`, only the webhook resume callback) and an authenticated group (`authv2`, protected by `auth.Authenticate` with token/session): [3](#0-2) 

`loopRoutes`, by contrast, registers all four handlers directly on the bare `r` (i.e., `api`) group passed into it, with no `auth.Authenticate` wrapper anywhere in the function body: [4](#0-3) 

The handlers behind these routes disclose real internal state: `discoveryHandler` returns the node's discovery hostname, exposed port, and names of all registered LOOP plugins: [5](#0-4) 

`pluginMetricHandler` proxies to a plugin's Prometheus `/metrics` endpoint and returns the raw body, with a comment noting this channel is meant to be "internal": [6](#0-5) 

`pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` proxy full Go pprof data (heap, goroutine, profile, symbol) from the plugin process, again commented as an "internal" channel between node and plugin: [7](#0-6) 

No auth, role, or token check exists anywhere in this call path — I confirmed by reading the full `router.go` and `loop_registry.go` files that there is no hidden middleware, IP allowlist, or network binding check applied to these specific routes; they are registered exactly as shown, directly on the shared `api` group alongside authenticated ones.

## Impact Explanation
This maps to unauthorized information disclosure of internal node state — plugin topology, internal hostnames/ports, and raw Prometheus metrics — and, more severely, full pprof profiling data (heap dumps, goroutine stacks, CPU profiles) which can contain process memory contents, internal source paths, and potentially sensitive values held in memory. This is a genuine authentication-bypass class issue: an endpoint intended to be reachable only by the node's own internal Prometheus/plugin communication is instead exposed on the public-facing web server without the authentication check applied to every structurally similar route (`/debug/vars`, all of `authv2`).

## Likelihood Explanation
High and directly reproducible from the code: no credentials, session cookie, or API token is required to reach any of these four routes. The plugin name required for `/plugins/:name/...` routes is discoverable from the unauthenticated `/discovery` endpoint itself, so no prior knowledge is needed. The only precondition is that the node's web server port is reachable by the attacker, which is the standard operating assumption for the Chainlink node API (the same precondition as every other unauthenticated-vs-authenticated route comparison made in the report).

## Recommendation
Wrap `loopRoutes`'s route registrations with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` (or token-based) middleware used by `debugRoutes` and `authv2`, e.g. by creating an authenticated sub-group inside `loopRoutes` analogous to `debugRoutes`. Alternatively, bind the LOOP registry/pprof proxy to an internal-only listener not reachable from the public API port.

## Proof of Concept
```
curl http://<node-host>:<web-port>/discovery
curl http://<node-host>:<web-port>/plugins/<plugin-name>/metrics
curl "http://<node-host>:<web-port>/plugins/<plugin-name>/debug/pprof/heap?debug=1"
```
Each request succeeds without any `Authorization` header or session cookie, because `loopRoutes` (unlike `debugRoutes` and `authv2`) is registered on the bare `api` group without any `auth.Authenticate` wrapper in `core/web/router.go`, as confirmed by direct inspection of the route registration code (`core/web/router.go` lines 230-236) versus the authenticated counterparts (lines 180-183, 238-248).

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

**File:** core/web/router.go (L238-248)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

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

**File:** core/web/loop_registry.go (L95-127)
```go
// pluginMetricHandlers routes from endpoints published in service discovery to the backing LOOP endpoint
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
