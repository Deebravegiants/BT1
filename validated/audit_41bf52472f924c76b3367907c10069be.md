Audit Report

## Title
Unauthenticated access to internal LOOP plugin metrics/pprof endpoints via `/plugins/:name/*` routes - ([File: core/web/router.go])

## Summary
`loopRoutes` in `core/web/router.go` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the base `api` group, which is only wrapped with rate-limiting and cookie-session middleware — not `auth.Authenticate(...)`. This is confirmed by direct code inspection: the `api` group is created at [1](#0-0)  with only `rateLimiter` and `sessions.Sessions`, and `loopRoutes(app, api)` is invoked directly on it at [2](#0-1) , while `loopRoutes` itself applies no auth wrapper to any of its four routes [3](#0-2) .

## Finding Description
Every other sensitive route group in the router is explicitly wrapped in authentication: `debugRoutes` requires `auth.Authenticate(..., auth.AuthenticateBySession)` for `/debug/vars` [4](#0-3) ; `sessionRoutes`'s destroy route requires session auth [5](#0-4) ; and the entire `v2Routes` group's `authv2` subgroup requires `auth.AuthenticateByToken`/`auth.AuthenticateBySession` [6](#0-5) , with additional per-route role checks like `auth.RequiresAdminRole`. In contrast, `loopRoutes` has no such wrapper anywhere — the four handlers (`discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, `pluginPPROFPOSTSymbolHandler`) are registered directly on the raw `r` group without any `auth.Authenticate` call, and the handler implementations themselves in `core/web/loop_registry.go` perform no authentication or authorization check before proxying to the plugin's internal metrics/pprof server [7](#0-6) [8](#0-7) . The pprof handler forwards the attacker-supplied `seconds` query parameter to control CPU profile duration [9](#0-8) , and the request timeout is derived from that same attacker-controlled value, extending resource consumption on the plugin. This matches the exact code the claim cites, with no additional/hidden auth middleware found anywhere in the call chain.

## Impact Explanation
This is an in-scope finding: an unauthenticated network client reaching the node's exposed web server can retrieve internal Prometheus metrics for any registered LOOP plugin and can trigger heap/goroutine/CPU pprof dumps and symbol lookups without any credential. Pprof heap/goroutine dumps can leak sensitive in-process data, and attacker-controlled `seconds` values can be used to hold open long-running profiling requests against the plugin process (resource exhaustion / partial DoS vector). This falls within the "node API authentication bypass" impact category, since a route that should logically require the same protection as `/debug/pprof/*` (gated behind `metricRoutes(authv2)` — session/token auth) is instead exposed unauthenticated.

## Likelihood Explanation
High. No credentials, session cookie, or API token are needed — only network reachability to the node's HTTP listener, which is required for basic operation of the node's UI/API and is typically reachable to at least some client population (internal network, or public in misconfigured deployments). The routes are reachable via a single unauthenticated HTTP GET/POST, and the plugin name only needs to be one that is registered on the node (enumerable via `/discovery`, which is also on the same unauthenticated group).

## Recommendation
Wrap `loopRoutes` — or at minimum the `/plugins/:name/metrics` and `/plugins/:name/debug/pprof/*` routes — in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, consistent with how `metricRoutes(authv2)` and `debugRoutes` protect the functionally equivalent node-level `/debug/pprof/*` and `/debug/vars` endpoints. If these endpoints are intended solely for internal Prometheus scraping, consider requiring a dedicated scrape token or restricting them to a loopback-only listener instead of exposing them via the main authenticated API surface.

## Proof of Concept
1. Start a Chainlink node with at least one LOOP plugin registered (e.g., a Solana/Median plugin) so that `plugins.LoopRegistry` has an entry with a non-zero `PrometheusPort`.
2. Without any session cookie or `Authorization`/API token header, send:
   `GET /plugins/<plugin-name>/metrics`
   and
   `GET /plugins/<plugin-name>/debug/pprof/heap?seconds=30`
3. Observe both requests return `200 OK` with plugin metrics/pprof payloads, confirmed by tracing the code path `pluginMetricHandler`/`pluginPPROFHandler` → `doRequest`/direct proxy → plugin's internal HTTP server, none of which perform an authentication check, unlike the equivalent authenticated `metricRoutes(authv2)` pprof endpoints.

### Citations

**File:** core/web/router.go (L78-85)
```go
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)
```

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
