Audit Report

## Title
Unauthenticated exposure of LOOPP plugin Prometheus metrics and pprof profiling data via `/discovery` and `/plugins/:name/*` routes - ([File: core/web/router.go])

## Summary
`loopRoutes` is registered directly on the top-level `api` router group in `NewRouter`, which only applies rate-limiting and cookie-session middleware — no authentication is required to reach `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, or `/plugins/:name/debug/pprof/symbol`. This lets any unauthenticated network client enumerate LOOPP plugins and pull their raw Prometheus metrics and pprof debug/profile data (heap, goroutine stacks, CPU profiles).

## Finding Description
In `core/web/router.go`, the `api` group is created with only rate limiting and session middleware: [1](#0-0) . `loopRoutes(app, api)` is then registered on this group with no call to `auth.Authenticate(...)`: [2](#0-1) .

This is inconsistent with every other sensitive route group in the same file: `debugRoutes` wraps its `/debug/vars` route in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` [3](#0-2) , and `metricRoutes` (the equivalent pprof endpoint set for the core node process) is only invoked from within the already-authenticated `authv2` group [4](#0-3) , itself gated by `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` [5](#0-4) .

The handlers backing the loop routes proxy requests to internal LOOPP plugin processes and return their raw output verbatim to the caller: `pluginMetricHandler` forwards to the plugin's `/metrics` endpoint [6](#0-5) , and `pluginPPROFHandler`/`pluginPPROFPOSTSymbolHandler` forward to the plugin's `/debug/pprof/*` endpoints, including heap, goroutine, profile, trace and symbol lookups [7](#0-6) . `discoveryHandler` enumerates all registered plugins and their metrics scrape paths [8](#0-7) .

No other middleware in the request chain (rate limiter, session store, CORS, helmet, size limiter) performs authentication, so any client capable of reaching the node's HTTP port can call these endpoints without any credential.

## Impact Explanation
This is an information-disclosure vulnerability: an unauthenticated caller can obtain full pprof heap/goroutine/CPU-profile dumps and Prometheus metric output for any loaded LOOPP plugin. Depending on the plugin, pprof heap and goroutine dumps can contain in-memory data, internal identifiers, and configuration state that should be operator-only, and this directly breaks the security boundary the codebase itself establishes for equivalent core-process debug/pprof endpoints (`debugRoutes`, `metricRoutes`), which are explicitly authenticated. This maps to an in-scope "node API authentication bypass" class of impact — access to protected/internal diagnostic endpoints without credentials.

## Likelihood Explanation
High for any node whose web server port is reachable by an untrusted party: a single unauthenticated GET request to `/discovery`, `/plugins/<name>/metrics`, or `/plugins/<name>/debug/pprof/heap` succeeds with no `Authorization` header or session cookie, as confirmed by the complete absence of any `auth.Authenticate` wrapper around `loopRoutes` registration in `core/web/router.go`.

## Recommendation
Wrap `loopRoutes(app, api)` registration with the same authentication middleware used elsewhere (e.g., `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`), or move it into the authenticated `authv2` group alongside `metricRoutes`, so `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` require valid session/token credentials like all other diagnostic endpoints.

## Proof of Concept
Against a running node with a LOOPP plugin registered, with no session cookie or bearer token:
```
GET /discovery HTTP/1.1
Host: node:6688
```
```
GET /plugins/<plugin-name>/metrics HTTP/1.1
Host: node:6688
```
```
GET /plugins/<plugin-name>/debug/pprof/heap?debug=1 HTTP/1.1
Host: node:6688
```
All three return `200 OK` with plugin data, confirmed by tracing the route registration path in `core/web/router.go` lines 87-91/230-236 (no `auth.Authenticate` call) versus the authenticated equivalents at lines 180-183 and 444-447.

### Citations

**File:** core/web/router.go (L77-85)
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

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
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
