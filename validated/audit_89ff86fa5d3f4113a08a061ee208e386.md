Audit Report

## Title
Missing Authentication for LOOP Plugin Discovery/Metrics/pprof Debug Endpoints - (File: `core/web/router.go`)

## Summary
`loopRoutes` is registered on the top-level `api` route group in `NewRouter`, which only applies a rate limiter and session-cookie parsing middleware, not an authentication check. Unlike `debugRoutes` (session-authenticated) and `metricRoutes` (only mounted inside the token/session-authenticated `authv2` group), the LOOP plugin discovery, metrics-proxy, and pprof-proxy handlers in `core/web/loop_registry.go` are reachable by any unauthenticated client that can reach the node's HTTP API.

## Finding Description
In `NewRouter`, the `api` group is created with only a rate limiter and cookie-session middleware (which just parses cookies, it doesn't enforce authentication): [1](#0-0) 

`loopRoutes` registers four endpoints on that group with no `auth.Authenticate(...)` wrapper at all: [2](#0-1) 

This is inconsistent with the other diagnostic route groups in the same file. `debugRoutes` requires session authentication: [3](#0-2) 

And `metricRoutes` (the node's own pprof endpoints) is only ever invoked inside the `authv2` group, which requires `auth.Authenticate(... AuthenticateByToken, AuthenticateBySession)`: [4](#0-3) [5](#0-4) 

The handlers behind the unauthenticated `loopRoutes` proxy directly to the internal LOOP plugin's HTTP metrics/pprof server, forwarding attacker-controlled query parameters (`debug`, `gc`, `seconds`): [6](#0-5) [7](#0-6) 

No existing middleware in the `api` group performs credential verification before these handlers execute, so any client capable of reaching the node's HTTP API port can call `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` without any session cookie or API token.

## Impact Explanation
An unauthenticated remote client reaching the node's HTTP API can enumerate registered LOOP plugins via `/discovery`, pull heap/goroutine/allocs profiles via `/plugins/:name/debug/pprof/*`, and force CPU profiling for a client-chosen duration or trigger GC via query parameters. Heap/goroutine dumps of a LOOP plugin process can reveal sensitive in-memory data. This maps to the in-scope "key/secret exfiltration" and "missing node API authentication" impact categories, since a security boundary (authentication) that is enforced for functionally equivalent debug endpoints (`metricRoutes`, `debugRoutes`) is absent here.

## Likelihood Explanation
Exploitation requires only a plain unauthenticated HTTP GET against the node's public HTTP API port — no credentials, tokens, or elevated network position are needed, making this trivially and repeatably reachable by any unprivileged client that can route to the node's API.

## Recommendation
Wrap `loopRoutes` in `core/web/router.go` with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession, auth.AuthenticateByToken)` (and an appropriate role gate) used by `debugRoutes`/`authv2`, or move the plugin discovery/metrics/pprof routes into the authenticated `authv2` group alongside `metricRoutes`.

## Proof of Concept
Against a running node with a LOOP plugin registered, and without any session cookie or API token:
1. `GET http://<node-host>:<http-port>/discovery` → returns 200 with plugin target metadata.
2. `GET http://<node-host>:<http-port>/plugins/<pluginName>/metrics` → returns 200 with plugin metrics.
3. `GET http://<node-host>:<http-port>/plugins/<pluginName>/debug/pprof/heap` → returns 200 with a full heap dump.
4. `GET http://<node-host>:<http-port>/plugins/<pluginName>/debug/pprof/profile?seconds=60` → returns 200 after forcing 60s of CPU profiling, with no `401 Unauthorized` returned at any step, confirming the absence of `auth.Authenticate` around `loopRoutes` (`core/web/router.go:230-236`) versus the authenticated `metricRoutes(authv2)` call (`core/web/router.go:446`).

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

**File:** core/web/router.go (L444-446)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
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

**File:** core/web/loop_registry.go (L130-166)
```go
const PPROFOverheadSeconds = 30

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
