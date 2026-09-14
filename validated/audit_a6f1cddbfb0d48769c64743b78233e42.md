### Title
Missing permission checks on LOOP plugin discovery/metrics/pprof endpoints - (File: core/web/router.go)

### Summary
The `loopRoutes` function registers the LOOP-plugin discovery, metrics, and pprof-debug endpoints directly on the top-level `api` router group without any authentication or role-check middleware, unlike every other functional route group (`v2Routes`, `debugRoutes`, `sessionRoutes`) which explicitly wraps its handlers in `auth.Authenticate(...)` and often `auth.RequiresXRole(...)`.

### Finding Description
In `NewRouter`, the route groups are set up as: [1](#0-0) 

`debugRoutes` wraps its `/debug/vars` route in `auth.Authenticate(...)`: [2](#0-1) 

`v2Routes` splits routes explicitly into an unauthenticated group and an authenticated group with per-route role checks (`auth.RequiresAdminRole`, `auth.RequiresEditRole`, etc.): [3](#0-2) 

However, `loopRoutes` registers its handlers directly on `r` (the bare `api` group, which only has rate-limiting and a session middleware — no authentication requirement) with no `auth.Authenticate` wrapper at all: [4](#0-3) 

These handlers, implemented in `core/web/loop_registry.go`, expose:
- `discoveryHandler` — lists all registered LOOP plugin names and their scrape target/metrics paths. [5](#0-4) 
- `pluginMetricHandler` — proxies and returns the raw Prometheus `/metrics` output of an internal plugin process, given only its name. [6](#0-5) 
- `pluginPPROFHandler` / `pluginPPROFPOSTSymbolHandler` — proxy arbitrary Go `pprof` debug endpoints (heap, goroutine, profile, trace, symbol) of the internal plugin process to the caller. [7](#0-6) 

This is the same bug class as the Jenkins AppSpider issue: HTTP endpoints that disclose internal metadata (plugin/engine names, in this case) and, worse here, allow retrieval of internal metrics/profiling data — reachable from any unauthenticated request, since no permission check exists at all on this route group (stronger than the original report, which required only "Overall/Read").

### Impact Explanation
An unauthenticated network client can enumerate all registered LOOP plugins and pull their names via `/discovery`, fetch full Prometheus metrics dumps via `/plugins/:name/metrics`, and pull Go runtime `pprof` profiles/heap dumps/goroutine stacks via `/plugins/:name/debug/pprof/*`. This can leak internal topology, configuration, memory contents, and stack traces, and the pprof `profile`/`trace` endpoints can also be used to tie up node/plugin resources (CPU profiling with attacker-controlled `seconds` parameter) — an availability/DoS vector as well as an information-disclosure one. This matches CWE-862 (missing authorization) directly.

### Likelihood Explanation
High. These routes are registered on the default web server group with no additional network restriction implied by the code, and any client capable of reaching the node's HTTP API can hit `/discovery`, `/plugins/<name>/metrics`, or `/plugins/<name>/debug/pprof/<profile>` with a simple unauthenticated GET/POST request. The plugin name is guessable/discoverable via `/discovery` itself, making full exploitation trivial once the endpoint is reachable.

### Recommendation
Wrap `loopRoutes` handlers with the same authentication (and appropriate role) middleware used elsewhere in `core/web/router.go`, e.g. `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, and consider requiring at least `RequiresRunRole`/`RequiresAdminRole` given the sensitivity of pprof/metrics data, consistent with how `debugRoutes` and `authv2` groups are protected.

### Proof of Concept
Without any credentials:
```
GET /discovery HTTP/1.1
Host: <chainlink-node>
```
returns JSON listing all plugin names and their metrics scrape paths (per `discoveryHandler`), then:
```
GET /plugins/<plugin-name>/metrics HTTP/1.1
Host: <chainlink-node>
```
returns the plugin's raw Prometheus metrics, and:
```
GET /plugins/<plugin-name>/debug/pprof/heap HTTP/1.1
Host: <chainlink-node>
```
returns a full heap dump of the internal LOOP plugin process — all without ever passing through `auth.Authenticate`.

### Citations

**File:** core/web/router.go (L86-92)
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

**File:** core/web/router.go (L238-256)
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
	{
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
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
