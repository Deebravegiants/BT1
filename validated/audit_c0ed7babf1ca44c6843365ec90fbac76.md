### Title
Missing authentication on LOOP plugin discovery/metrics/pprof endpoints allows unauthenticated enumeration and debug-data disclosure - (File: core/web/router.go)

### Summary
The `loopRoutes` handler registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the top-level router group with **no authentication middleware**, unlike every other sensitive route in the same file (which is wrapped in `auth.Authenticate(...)`) and even unlike the structurally similar `/debug/vars` route, which explicitly requires session auth. [1](#0-0) [2](#0-1) 

### Finding Description
`NewRouter` wires up all route groups on the shared `api` group. Nearly every route group that exposes internal state is explicitly wrapped with `auth.Authenticate`, e.g. `debugRoutes` for `/debug/vars`: [1](#0-0) 

and the `authv2` group for keys/bridges/external initiators: [3](#0-2) 

However, `loopRoutes` is called with the bare `api` group and applies no `auth.Authenticate` wrapper at all: [4](#0-3) [2](#0-1) 

This exposes:
- `discoveryHandler`, which enumerates every registered LOOP plugin's name (an internal identifier, analogous to enumerating credential/config IDs in the Jenkins CVE) via `l.registry.List()`: [5](#0-4) 

- `pluginMetricHandler` and `pluginPPROFHandler`, which proxy to the plugin's internal Prometheus/pprof port using only the attacker-supplied `:name` param — no session/token check is performed before forwarding the request: [6](#0-5) [7](#0-6) 

- `pluginPPROFPOSTSymbolHandler`, which similarly forwards to the plugin's `/debug/pprof/symbol` without auth: [8](#0-7) 

Go's `net/http/pprof` handlers (including `heap`, `goroutine`, `profile`, `trace`) can expose live memory contents, stack traces, environment info, and other process internals — comparable in kind (though broader) to the "credentials/secret enumeration" impact class described in the CVE, and consistent with why `metricRoutes`'s identical pprof set is deliberately placed behind `authv2` (session/token auth) elsewhere in the same file: [9](#0-8) [10](#0-9) 

The existence of the authenticated `metricRoutes`/pprof group under `authv2` shows the codebase's own security model treats pprof/debug endpoints as requiring at least session/token authentication — yet the LOOP-registry equivalents bypass that control entirely.

### Impact Explanation
An unauthenticated network client that can reach the node's HTTP port can:
1. Enumerate all registered LOOP plugin names via `/discovery` without any credential.
2. Pull Prometheus metrics for any named plugin via `/plugins/:name/metrics`.
3. Trigger CPU/heap/goroutine profiling or pull `pprof` dumps for a named plugin via `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol`, all without authentication.

This matches CWE-862 (Missing Authorization): reachable, unprivileged, and previously undisclosed internal state (plugin identities, metrics, and profiling data) is exposed. It does not, by itself, disclose credentials in the same way the CVE's `doGetCredentialIds` endpoint did — this is the primary reason for flagging it as an analog rather than an exact match — but the bug class (endpoints omitted from the router's own authentication scheme) is directly analogous, and the pprof surface carries a real risk of leaking process-internal secrets (memory contents, symbol tables) to any network-reachable actor.

### Likelihood Explanation
Likelihood is high for reachability: these routes are registered unconditionally on the public web server whenever any LOOP plugin is enabled, requiring no special network position beyond reaching the node's HTTP port (which is already reachable by design for the authenticated `/v2/*` API). No credentials, tokens, or session cookies are needed to invoke any of these four endpoints.

### Recommendation
Wrap `loopRoutes` registrations in the same `auth.Authenticate` middleware used elsewhere (e.g., matching the pattern used for `/debug/vars` and `metricRoutes`), requiring at minimum session or token authentication before serving `/discovery`, `/plugins/:name/metrics`, and the pprof-forwarding endpoints. If the `/discovery` endpoint must remain reachable by an external unauthenticated Prometheus scraper, restrict it via network-level allowlisting/IP filtering rather than leaving it open to any web client, and gate the higher-risk pprof/symbol endpoints behind authentication unconditionally.

### Proof of Concept
```
# No cookie / API token supplied:
curl -i http://<node-host>:6688/discovery
curl -i http://<node-host>:6688/plugins/<plugin-name>/metrics
curl -i http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/heap
curl -i -X POST http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/symbol
```
Per `core/web/router.go` (`loopRoutes` at lines 230-236) and `NewRouter` (lines 87-91), these routes are registered without any `auth.Authenticate` wrapper, so all four requests are expected to succeed (HTTP 200, or 404 only if the plugin name is wrong) without any authentication header/cookie, in contrast to every other sensitive route in the file.

### Citations

**File:** core/web/router.go (L87-91)
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
