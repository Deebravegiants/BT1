Based on the code, there's a genuine analog in this repository: **the LOOP plugin routes are mounted with no authentication middleware at all**, unlike every other operational/debug route in the router.

### Title
Unauthenticated access to internal plugin metrics/pprof endpoints via `/plugins/:name/*` routes - ([File: core/web/router.go])

### Summary
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the base `api` group, which only carries rate-limiting and session middleware — no `auth.Authenticate(...)` wrapper is applied, in contrast to every other sensitive route group in the router.

### Finding Description
In `NewRouter`, the `api` group is created with only rate limiting and cookie-session middleware, no authentication requirement: [1](#0-0) [2](#0-1) 

`loopRoutes` is called on this unauthenticated `api` group directly (`loopRoutes(app, api)`), unlike `sessionRoutes`/`v2Routes` internals which wrap sensitive endpoints in `auth.Authenticate(...)`. Compare this to `debugRoutes`, which explicitly requires session auth for the analogous `/debug/vars` expvar endpoint: [3](#0-2) 

The plugin handlers (`pluginMetricHandler`, `pluginPPROFHandler`, `pluginPPROFPOSTSymbolHandler`) proxy requests straight through to the internal LOOP plugin's pprof/metrics HTTP server based on attacker-controlled `:name` and `:profile` path/query parameters, with no authentication check performed anywhere in the handler chain: [4](#0-3) 

This is structurally the same bug class as GHSA-72qv-j8vr-xvfv: a category of routes ("plugin endpoints") is exempted from the authentication enforcement that is applied to functionally equivalent routes elsewhere in the same router (e.g. `/debug/vars`, `/debug/pprof/*` under `metricRoutes(authv2)`).

### Impact Explanation
An unauthenticated network client can:
- Enumerate/query `/plugins/:name/metrics` for any registered LOOP plugin, retrieving internal Prometheus metrics that may include internal identifiers, addresses, or performance/security-relevant telemetry.
- Trigger `/plugins/:name/debug/pprof/*profile` (heap, goroutine, cpu profile via `seconds`) and `/plugins/:name/debug/pprof/symbol`, which can leak in-memory data (potentially including secrets held in plugin process memory) via heap/goroutine dumps, and can be abused for resource exhaustion (blocking CPU profile duration controlled by the `seconds` query parameter forwarded in `pprofURLVals`) — a denial-of-service vector against the LOOP plugin process. [5](#0-4) 

### Likelihood Explanation
High — no credentials, session, or API token are required; the routes are reachable directly on the node's exposed web server port, identical to how the Mattermost plugin routes were reachable without MFA enforcement despite being intended to require authentication like other endpoints in the app.

### Recommendation
Wrap `loopRoutes` (or at minimum the `/plugins/:name/metrics` and `/plugins/:name/debug/pprof/*` routes) in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` consistent with `metricRoutes(authv2)` and `debugRoutes`, or restrict access via network/allowlist controls if these are intended purely for internal Prometheus scraping.

### Proof of Concept
1. Start a Chainlink node with a LOOP plugin registered.
2. Without any session cookie or API token, send:
   `GET /plugins/<plugin-name>/debug/pprof/heap?seconds=30`
   or
   `GET /plugins/<plugin-name>/metrics`
3. Observe the request succeeds (200 OK) and returns internal plugin profiling/metrics data, confirming the absence of any authentication check on these routes, unlike the equivalent `/debug/pprof/*` routes reachable only via `metricRoutes(authv2)`.

### Citations

**File:** core/web/router.go (L76-92)
```go
	engine.Use(helmet.Default())
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
