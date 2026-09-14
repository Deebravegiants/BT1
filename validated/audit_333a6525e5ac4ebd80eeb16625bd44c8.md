## Analysis

I found a concrete unauthenticated-endpoint disclosure analog matching the DolphinScheduler CVE class (exposed management/debug endpoints leaking sensitive data without auth).

### Title
Unauthenticated exposure of LOOP plugin `/metrics` and `/debug/pprof` endpoints allows sensitive information disclosure - (File: core/web/router.go)

### Summary
Chainlink's web router mounts the LOOP-plugin metrics/pprof proxy routes on the top-level `api` route group, which only has rate-limiting and session-cookie middleware applied — not the `auth.Authenticate` middleware that protects the rest of the API. This is directly analogous to the DolphinScheduler CVE, where Spring Boot Actuator management endpoints were exposed without authentication and could leak sensitive information (including credentials).

### Finding Description
In `NewRouter`, the `api` group is created with only rate limiting and session middleware — no authentication requirement: [1](#0-0) 

`debugRoutes` explicitly wraps its `/debug` group with `auth.Authenticate(...)` before exposing `expvar`: [2](#0-1) 

But `loopRoutes`, also mounted directly on the unauthenticated `api` group, registers the plugin metrics and pprof proxy endpoints with no auth middleware at all: [3](#0-2) 

These handlers proxy directly to a plugin's internal `/metrics` and `/debug/pprof/*` endpoints (heap, goroutine, cmdline, profile, trace, etc.) and return the raw response body to the caller: [4](#0-3) [5](#0-4) 

Notably, the project's own documentation warns that pprof heap dumps "may potentially expose sensitive data e.g. private key components": [6](#0-5) 

Since these routes bypass `auth.Authenticate` entirely (unlike every other sensitive route in the router, e.g. `/debug/vars`, `/v2/*`), any unauthenticated network client that can reach the node's web server can hit `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/heap`, `/plugins/:name/debug/pprof/profile`, etc.

### Impact Explanation
An unauthenticated actor reaching the Chainlink node's HTTP API can retrieve heap dumps, goroutine stacks, CPU profiles, and Prometheus metrics from any running LOOP plugin (e.g. Median, Solana, Starknet relayers). Heap/goroutine dumps can contain in-memory secrets, private key material, or internal state, and metrics can reveal operational/business-sensitive information — matching CWE-200 exposure of sensitive information to an unauthorized actor, the same bug class as the referenced advisory.

### Likelihood Explanation
Likelihood is high wherever the node's default listening port is reachable by an unprivileged client (e.g., misconfigured network exposure, or any deployment that doesn't strictly firewall the API port), since no credentials, tokens, or session cookies are required — the routes are simply absent from any `auth.Authenticate` wrapper, unlike all comparable debug/metrics routes in the same file.

### Recommendation
Wrap `loopRoutes` registration with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` (or a dedicated internal-only middleware/network binding) used for `debugRoutes`, so plugin metrics and pprof proxy endpoints require authentication, consistent with `/debug/vars` and other sensitive routes.

### Proof of Concept
1. Start a Chainlink node with at least one LOOP plugin enabled (e.g. Median/Solana relayer) so `loopRegistry` has a registered plugin.
2. Without any session cookie or API token, send:
   - `GET /plugins/<name>/metrics`
   - `GET /plugins/<name>/debug/pprof/heap?debug=1`
   - `GET /plugins/<name>/debug/pprof/profile?seconds=5`
3. Observe the responses are returned successfully (200 OK) with plugin metrics/heap/profile data, despite no authentication being provided — confirming the routes registered in `loopRoutes` (`core/web/router.go` lines 230-236) bypass `auth.Authenticate`.

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

**File:** docs/CONFIG.md (L37-43)
```markdown
### InsecurePPROFHeap
:warning: **_ADVANCED_**: _Do not change this setting unless you know what you are doing._
```toml
InsecurePPROFHeap = true # Default
```
InsecurePPROFHeap allows dumping the heap in pprof. This is very useful for debugging memory leaks but in certain rare cases may potentially expose sensitive data e.g. private key components, so is disabled by default.
Deprecated: no effect. Always enabled.
```
