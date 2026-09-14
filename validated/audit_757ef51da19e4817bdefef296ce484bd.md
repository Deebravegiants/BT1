### Title
Unauthenticated LOOP registry discovery, metrics-proxy, and pprof-proxy endpoints bypass Chainlink node API authentication - (File: core/web/router.go)

### Summary
The Chainlink node's HTTP API enforces Basic/API-token/session authentication for its `/v2/**` routes, but the LOOP (Local Out-Of-Process) plugin registry routes registered by `loopRoutes` are mounted on the same port without any authentication middleware, directly analogous to Kestra's unauthenticated Micronaut `/env` and `/loggers` actuator endpoints bypassing the API's basic-auth.

### Finding Description
`NewRouter` builds an `api` route group that only applies rate limiting and session-cookie support — no authentication: [1](#0-0) 

`loopRoutes` is registered directly on this unauthenticated `api` group: [2](#0-1) 

Compare this to `v2Routes`, where sensitive routes (including the node's own `metricRoutes`/pprof handlers) are explicitly wrapped in an authenticated sub-group before being registered: [3](#0-2) [4](#0-3) 

The handlers reachable without authentication include:
- `GET /discovery` — dumps Prometheus service-discovery JSON containing the node's internal hostnames and ports for every registered LOOP plugin. [5](#0-4) 
- `GET /plugins/:name/metrics` — proxies to the internal plugin's `/metrics` endpoint and returns the raw body to the caller. [6](#0-5) 
- `GET /plugins/:name/debug/pprof/*profile` and `POST /plugins/:name/debug/pprof/symbol` — proxy arbitrary pprof profile/symbol requests (including CPU/heap/goroutine dumps) to the internal plugin process and stream results back to the unauthenticated caller. [7](#0-6) 

This is the same bug class as the Kestra CVE: an internet-facing management/introspection surface is left open on the API-facing listener while the rest of the API enforces authentication, letting an unauthenticated client read internal configuration/topology data and force expensive or information-disclosing debug operations.

### Impact Explanation
An unauthenticated client with network access to the node's API port (6688 by default) can:
- Enumerate internal plugin hostnames/ports via `/discovery`, aiding further reconnaissance/pivoting.
- Pull raw Prometheus `/metrics` data from LOOP plugins, which can leak operational/internal state.
- Trigger CPU/heap/goroutine/trace pprof captures against LOOP plugin processes repeatedly, causing resource exhaustion (DoS) or leaking sensitive runtime data (stack traces, memory contents) — comparable in severity to Kestra's `/env` config disclosure and `/loggers` runtime tampering, since it is unauthenticated disclosure plus an operator-level control action (profiling) reachable by anyone.

### Likelihood Explanation
High: no special conditions are required — the routes are always mounted whenever `NewRouter` is constructed, since `loopRoutes(app, api)` is called unconditionally in `NewRouter`, and there is no build-tag/dev-only guard as exists for other sensitive routes (e.g., `build.IsDev()` gating `/execute_capability`). Any client that can reach the node's normal API port can hit these endpoints without credentials.

### Recommendation
Move `loopRoutes` registration under an authenticated route group (mirroring how `metricRoutes(authv2)` is protected), or explicitly wrap `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` with `auth.Authenticate(...)` (and appropriate role checks such as `auth.RequiresAdminRole`) before exposing them, consistent with how debug/pprof access is gated for the primary node.

### Proof of Concept
1. Start a Chainlink node with the default WebServer configuration and at least one LOOP plugin registered.
2. Without any session cookie or `X-API-KEY`/`X-API-SECRET` headers, issue:
   - `GET http://<node-host>:6688/discovery`
   - `GET http://<node-host>:6688/plugins/<plugin-name>/metrics`
   - `GET http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/heap`
3. Observe HTTP 200 responses with plugin discovery data, metrics, and pprof profile output, despite lacking any of the credentials required by the equivalent `/v2/**` routes.

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

**File:** core/web/router.go (L444-447)
```go

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

**File:** core/web/loop_registry.go (L95-128)
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
}
```

**File:** core/web/loop_registry.go (L150-215)
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

func (l *LoopRegistryServer) doRequest(gc *gin.Context, method, url string, body io.Reader, timeout time.Duration, pluginName string) {
	ctx, cancel := context.WithTimeout(gc.Request.Context(), timeout)
	defer cancel()
	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "error creating plugin pprof request: %s", err))
		return
	}
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		msg := "plugin pprof handler failed to post plugin url " + html.EscapeString(url)
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}
	defer res.Body.Close()
	b, err := io.ReadAll(res.Body)
	if err != nil {
		msg := fmt.Sprintf("error reading plugin %q pprof", html.EscapeString(pluginName))
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}

	gc.Data(http.StatusOK, "text/plain", b)
}
```
