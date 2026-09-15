Audit Report

## Title
Unauthenticated LOOP plugin pprof/metrics/discovery proxy endpoints mounted on the same public listener as authenticated APIs - ([File: core/web/router.go])

## Summary
`NewRouter` in `core/web/router.go` mounts `loopRoutes` on the shared, publicly reachable `api` gin route group, which only carries rate-limiting and session-cookie-store middleware (no authentication check) [1](#0-0) . Unlike `debugRoutes` and `v2Routes`, which explicitly wrap their groups with `auth.Authenticate(...)` [2](#0-1) [3](#0-2) , `loopRoutes` registers its handlers with no auth wrapper at all [4](#0-3) .

## Finding Description
The four handlers registered by `loopRoutes` — `discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, and `pluginPPROFPOSTSymbolHandler` — are implemented in `core/web/loop_registry.go`, and each is explicitly commented as being "internal btw the node and plugin" [5](#0-4) [6](#0-5) [7](#0-6) . Despite this internal-only intent, they are reachable through the exact same `gin.Engine`/port as the node's authenticated user-facing API, since `NewRouter` builds a single engine and the resulting handler is passed to a single public HTTP(S) server started via `ws.HTTPPort()` [8](#0-7) . `pluginPPROFHandler` forwards the caller-controlled `profile` path parameter and query parameters (including `seconds`) directly into a proxied request to the plugin's internal pprof server with no authentication check before invocation [9](#0-8) , and `pluginPPROFPOSTSymbolHandler` forwards an attacker-supplied request body similarly [10](#0-9) . This breaks the access-control pattern established elsewhere in the same file, where every other sensitive route group (`/debug`, `/v2`) is explicitly authenticated.

## Impact Explanation
An unauthenticated network client reaching the node's public web port can enumerate internal LOOP plugin names/ports via `/discovery` and `/plugins/:name/metrics`, and can remotely trigger CPU/heap/goroutine profiling with an attacker-controlled duration via `/plugins/:name/debug/pprof/*profile`, as well as post arbitrary bodies to `/plugins/:name/debug/pprof/symbol`. This is an authentication/access-control bypass (CWE-284/CWE-862) on internal diagnostic surface, exposing internal topology information and enabling resource-consumption abuse of plugin processes without any credential.

## Likelihood Explanation
High for any deployment where the node's web server HTTP port is reachable by untrusted clients, since no session cookie or API token is required — this contradicts the pattern used for every comparable route in the same router (`debugRoutes`, `v2Routes`), which do require authentication.

## Recommendation
Wrap the `loopRoutes` group with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` middleware used by `debugRoutes`, or move these plugin proxy/pprof/discovery endpoints off the publicly routable engine entirely (e.g., a separate internal-only listener not exposed by the operator UI ingress).

## Proof of Concept
1. Run a Chainlink node with at least one LOOP plugin registered and the web server port reachable without additional network filtering.
2. From an unauthenticated client (no session cookie, no API token) issue:
   - `curl http://<node>:<port>/discovery`
   - `curl http://<node>:<port>/plugins/<plugin-name>/metrics`
   - `curl "http://<node>:<port>/plugins/<plugin-name>/debug/pprof/profile?seconds=30"`
3. Confirm all three requests return data without ever passing through `auth.Authenticate`, by inspecting `NewRouter`/`loopRoutes` in `core/web/router.go` showing no auth middleware applied compared to `debugRoutes`/`v2Routes` in the same file.

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

**File:** core/web/loop_registry.go (L104-105)
```go
	// unlike discovery, this endpoint is internal btw the node and plugin
	pluginURL := fmt.Sprintf("http://%s:%d/metrics", l.loopHostName, p.EnvCfg.PrometheusPort)
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

**File:** core/cmd/shell.go (L450-461)
```go
	handler, err := web.NewRouter(app, ginPrometheus)
	if err != nil {
		return errors.Wrap(err, "failed to create web router")
	}
	server := server{handler: handler, lggr: app.GetLogger()}

	g, gCtx := errgroup.WithContext(ctx)
	serverStartTimeoutDuration := config.WebServer().StartTimeout()
	if ws.HTTPPort() != 0 {
		runServer := server.runFn(ws.ListenIP(), ws.HTTPPort(), config.WebServer().HTTPWriteTimeout())
		go tryRunServerUntilCancelled(gCtx, app.GetLogger(), serverStartTimeoutDuration, runServer)
	}
```
