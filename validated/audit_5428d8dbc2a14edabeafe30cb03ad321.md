Audit Report

## Title
Unauthenticated LOOP plugin metrics/pprof proxy allows internal service access via `/plugins/:name/...` - (File: core/web/router.go)

## Summary
`loopRoutes` is registered in `NewRouter` alongside `debugRoutes`, `sessionRoutes`, and `v2Routes`, but unlike those groups it is never wrapped in `auth.Authenticate(...)`, so its handlers are reachable by any unauthenticated network client that can reach the node's HTTP port. This exposes plugin `/metrics` and `/debug/pprof/*` proxying to internal LOOP plugin processes without any credential check.

## Finding Description
`NewRouter` calls `debugRoutes(app, api)`, `healthRoutes(app, api)`, `sessionRoutes(app, api)`, `v2Routes(app, api)`, `loopRoutes(app, api)` in sequence on the shared `api` group [1](#0-0) . `debugRoutes` explicitly gates its `/debug/vars` endpoint behind `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` [2](#0-1) , and `sessionRoutes`/`v2Routes` similarly wrap sensitive endpoints in `auth.Authenticate` [3](#0-2) . In contrast, `loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the passed-in group `r` with zero auth middleware [4](#0-3) .

`pluginMetricHandler` takes the unauthenticated, attacker-controlled `:name` path parameter, resolves it against the live plugin registry, and if found, proxies a live GET to an internal-only backend (`http://<loopHostName>:<PrometheusPort>/metrics`), returning the raw response to the caller [5](#0-4) . `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` do the same for `/debug/pprof/*` and `/debug/pprof/symbol`, forwarding query params (`debug`, `gc`, `seconds`) and, for the symbol endpoint, the raw POST body, straight through to the internal backend with no authentication check anywhere in the call path [6](#0-5) . The code comments even acknowledge these are meant to be internal-only ("unlike discovery, this endpoint is internal btw the node and plugin"), confirming the security assumption that was not enforced [7](#0-6) .

## Impact Explanation
Any unauthenticated client able to reach the node's public HTTP listener can enumerate registered LOOP plugins via `/discovery` and then pull live `pprof` profiles (heap, goroutine, trace, allocs, etc.) and Prometheus `/metrics` for any plugin process, all without session cookie, API token, or any credential. This is a genuine authentication-bypass exposing internal diagnostic/runtime-state surfaces (memory contents, goroutine stacks, internal configuration values) through the same public listener that serves the operator UI/API, and the `seconds` parameter on `pprof` profile/trace additionally allows triggering long-running captures for resource exhaustion.

## Likelihood Explanation
High. No credentials, session, or special network position are required beyond ordinary reachability to the node's HTTP port, which is the same port used for all normal API interactions. The plugin name is directly attacker-suppliable and matched against the live registry; the only precondition is that at least one LOOP plugin is registered, which is a normal deployment condition for LOOPP-based chains.

## Recommendation
Wrap `loopRoutes` registration in the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` (or an admin-role-gated) middleware used by `debugRoutes`/`v2Routes`, or relocate these internal diagnostic endpoints to a separate internal-only listener not exposed on the public-facing HTTP port.

## Proof of Concept
1. Start a Chainlink node with at least one LOOP plugin registered (e.g., an EVM-adjacent LOOPP chain).
2. As an unauthenticated client, `GET /discovery` on the node's HTTP port and observe the JSON list of registered plugin names and metrics paths — no auth header/cookie required.
3. `GET /plugins/<name>/metrics` with no session cookie; response returns the plugin's internal Prometheus metrics.
4. `GET /plugins/<name>/debug/pprof/heap?debug=1` with no authentication; response returns a live heap dump forwarded from the plugin's internal debug server, confirming the internal-only backend is reachable by an unprivileged actor.

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

**File:** core/web/router.go (L216-217)
```go
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
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
