## Finding: Unauthenticated pprof profiling proxy for LOOP plugins

### Title
Authentication bypass allows unauthenticated CPU/heap/trace profiling via `/plugins/:name/debug/pprof/*` - (File: `core/web/router.go`, `core/web/loop_registry.go`)

### Summary
The chainlink node HTTP router registers LOOP-plugin pprof-proxy routes (`/plugins/:name/debug/pprof/*profile` and `/plugins/:name/debug/pprof/symbol`) on the base `api` router group, which carries only rate-limiting and session middleware — no authentication is applied, unlike every other profiling-adjacent route in the codebase.

### Finding Description
In `NewRouter`, the top-level `api` group is created with only a rate limiter and cookie session middleware, and no authentication: [1](#0-0) 

`loopRoutes(app, api)` is called directly on this unauthenticated `api` group: [2](#0-1) 

This registers `pluginPPROFHandler` (GET) and `pluginPPROFPOSTSymbolHandler` (POST) with no auth middleware at all, in contrast to the equivalent host-level pprof group `metricRoutes`, which is only ever mounted under the authenticated `authv2` group (`metricRoutes(authv2)`): [3](#0-2) [4](#0-3) 

The handler itself forwards attacker-controlled parameters (including `seconds`, which controls profiling duration) to the plugin's internal pprof endpoint and streams back the result, with a timeout computed directly from the client-supplied `seconds` value: [5](#0-4) [6](#0-5) 

The code comment claims this is "internal btw the node and plugin," but the route is exposed on the node's public-facing HTTP API without any authentication check, so any unauthenticated client that can reach the node's webserver can invoke it.

### Impact Explanation
An unauthenticated remote client can trigger CPU/heap/trace/goroutine profiling on any registered LOOP plugin process by hitting `/plugins/:name/debug/pprof/profile?seconds=N` (or `trace`, `symbol`, etc.), repeatable and parallelizable across plugin names, causing sustained CPU consumption in plugin processes for the duration of `N` seconds per request — a denial-of-service vector directly analogous to the RustFS `/profile/cpu` bug. Error paths also leak internal infrastructure details (plugin hostnames and ports used for LOOP inter-process communication) in plaintext responses, an information-disclosure issue paralleling the RustFS filesystem-path leak.

### Likelihood Explanation
Likelihood is high: the route requires no credentials, no special headers, and no prior state — a single unauthenticated HTTP request against the node's default webserver port is sufficient. The `seconds` parameter is fully attacker-controlled and forwarded as-is.

### Recommendation
Require the same authentication middleware used for `authv2`/`metricRoutes` (`auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`) on the `loopRoutes` group, or at minimum on the `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` routes, mirroring how the local pprof group in `metricRoutes` is gated. Also bound/validate the `seconds` query parameter to a sane maximum, and avoid echoing internal plugin URLs in error responses.

### Proof of Concept
1. Start a chainlink node with at least one LOOP plugin registered.
2. Without any session cookie or API token, send:
   `GET http://<node>/plugins/<plugin-name>/debug/pprof/profile?seconds=60`
3. The request is proxied unauthenticated to the plugin's internal pprof server and blocks/consumes CPU for 60 seconds; repeating this concurrently against multiple plugin names amplifies resource exhaustion, with no `401 Unauthorized` ever returned since the `api` route group applied to `loopRoutes` carries no auth middleware. [7](#0-6)

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

**File:** core/web/router.go (L180-199)
```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", expvar.Handler())
}

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

**File:** core/web/router.go (L445-446)
```go
		// Debug routes accessible via authentication
		metricRoutes(authv2)
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

**File:** core/web/loop_registry.go (L190-215)
```go
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
