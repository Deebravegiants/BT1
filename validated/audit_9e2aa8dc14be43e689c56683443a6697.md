### Title
Loop plugin pprof/metrics/discovery routes mounted without authentication middleware, exposing runtime profiling and metrics endpoints to unauthenticated network clients - ([File: core/web/router.go])

### Summary
`loopRoutes` is mounted directly on the base `api` router group in `core/web/router.go`, which only carries rate-limiting and session middleware — not authentication. This is the same class of bug as the reported free5GC issue: a route group (`UPI` there, `loopRoutes` here) is registered on a router group that lacks the `auth.Authenticate(...)` middleware applied to sibling groups (`nsmf-oam`/`authv2` in each codebase), so its handlers are reachable by any unauthenticated network client.

### Finding Description
`NewRouter` builds a base group `api` with only rate limiting and cookie-session middleware attached, no authentication: [1](#0-0) 

`v2Routes`, by contrast, explicitly wraps its group with `auth.Authenticate(...)` before registering business routes: [2](#0-1) 

`loopRoutes`, however, is called directly on the unauthenticated `api` group, with no analogous auth wrapper: [3](#0-2) 

The `loopRoutes` function registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` with no per-route auth middleware either: [4](#0-3) 

These handlers proxy live requests to internal LOOP plugin processes and return their raw responses to the caller, including full `net/http/pprof` profiling data (heap, goroutine, cmdline, profile, trace, symbol) and Prometheus metrics text: [5](#0-4) [6](#0-5) 

This mirrors the reported bug's root cause precisely: a sibling group (`debugRoutes`/`metricRoutes` invoked inside `authv2` at line 446) *is* wrapped with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`: [7](#0-6) 
while `loopRoutes` on the top-level `api` group has no such wrapper — a route-group-scoped omission, not a global config gap, just like the UPI-vs-OAM contrast in the advisory.

### Impact Explanation
Unauthenticated network access to `net/http/pprof` handlers (`heap`, `goroutine`, `profile`, `trace`, `cmdline`, `symbol`) allows any unprivileged client reaching SBI/API port to capture full memory heap dumps and goroutine stack traces of the running SMF/Chainlink node process. Heap and goroutine dumps routinely leak secrets held in process memory (API tokens, session data, private-key material staged in memory, internal addresses), and `/debug/pprof/profile` and `/trace` allow triggering CPU-intensive profiling on demand — a remote resource-exhaustion vector. The `/discovery` and `/plugins/:name/metrics` endpoints leak internal plugin topology (hostnames, ports, plugin names) that should only be visible to the node operator or trusted Prometheus scraper. This satisfies the "key/secret disclosure" and reconnaisance/DoS impact classes analogous to the reported CWE-306/862.

### Likelihood Explanation
Any client capable of reaching the Chainlink node's HTTP API port (the same network position as the reported `SMF` SBI exposure) can directly issue `GET /plugins/:name/debug/pprof/heap` or `/discovery` with no credentials, since the whole `loopRoutes` group inherits no auth middleware. This requires no special network position beyond what is already required to reach the general web API — matching the "network attacker" precondition of the reference advisory.

### Recommendation
Wrap `loopRoutes` registration with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` middleware used by `authv2` and `debugRoutes`, or move the `loopRoutes(app, api)` call to register on the `authv2` group instead of the unauthenticated base `api` group in `core/web/router.go`, consistent with how `metricRoutes` is already gated inside `authv2` at line 446.

### Proof of Concept
Against a running Chainlink node with LOOP plugins registered, an unauthenticated client can issue:
```
curl -i http://<node-host>:<port>/discovery
curl -i http://<node-host>:<port>/plugins/<plugin-name>/metrics
curl -i http://<node-host>:<port>/plugins/<plugin-name>/debug/pprof/heap
```
None of these require an `Authorization` header or session cookie, because the enclosing route group (`loopRoutes`, mounted on `api` in `core/web/router.go:91`) has no authentication middleware, unlike sibling authenticated groups (`authv2`, `debugRoutes`).

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
