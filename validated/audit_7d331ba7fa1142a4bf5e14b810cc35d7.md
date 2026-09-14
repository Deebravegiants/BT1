The relevant finding here maps well onto the Chaos Mesh analog: Chainlink's web router exposes LOOP-plugin debug/profiling proxy routes without any authentication middleware.

### Title
Unauthenticated LOOP Plugin pprof/Metrics/Discovery Proxy Endpoints Enable Cluster-Wide Denial of Service - ([File: core/web/router.go])

### Summary
The Chainlink node's web router registers `loopRoutes`, which exposes HTTP handlers that proxy requests to internal LOOP plugin processes' `pprof` profiling and metrics endpoints, directly on the `api` route group **without any authentication middleware**, unlike almost every other sensitive route in the router (`debugRoutes`, `v2Routes`, `sessionRoutes` all wrap their groups in `auth.Authenticate(...)`).

### Finding Description
In `NewRouter`, routes are registered on the `api` group, which by itself only carries rate limiting and session middleware, not authentication: [1](#0-0) 

`debugRoutes` explicitly wraps its `/debug` group in `auth.Authenticate(...)`: [2](#0-1) 

But `loopRoutes` registers its handlers directly on `r` (the unauthenticated `api` group) with no auth wrapper at all: [3](#0-2) 

This is in contrast to the equivalent node-level `/v2/debug/pprof` routes (`metricRoutes`), which are deliberately nested inside the authenticated `authv2` group: [4](#0-3) 

The unauthenticated `loopRoutes` handlers, implemented in `core/web/loop_registry.go`, forward attacker-controlled requests — including the `seconds` and `profile` (wildcard path) parameters — to the internal LOOP plugin's `/debug/pprof/*` endpoint with no sanitization or bound beyond a computed timeout: [5](#0-4) 

The `pluginPPROFHandler` builds the target URL by directly concatenating the unauthenticated caller's wildcard `profile` parameter, and `pprofURLVals` passes through an attacker-supplied `seconds` value used both as the pprof query parameter and to compute the request context timeout: [6](#0-5) 

Any unauthenticated caller who can reach the node's HTTP web server (the standard Chainlink UI/API port) can trigger CPU/goroutine/trace profiling on every registered LOOP plugin process, hold connections/goroutines open for the profiling duration, and repeat this without any rate limit tied to authenticated users (only the generic `AuthenticatedPeriod`/rate limiter middleware from the `api` group applies, which is not identity-scoped since there's no authenticated identity here).

### Impact Explanation
This is functionally the same bug class as CVE-2025-59358: an unauthenticated actor can reach a debug/profiling control surface that lets them trigger expensive, long-running operations (CPU profiling, trace collection) against backend processes (LOOP plugins) purely by knowing/guessing a plugin name, with no session, token, or role check. Repeated or concurrent invocation of `/plugins/:name/debug/pprof/profile?seconds=N` or `/trace` against multiple plugins can exhaust CPU, memory, or goroutines on the node and its LOOP plugin subprocesses, resulting in denial of service — matching the CVSS:3.1 `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` profile of the source advisory.

### Likelihood Explanation
Likelihood is high for any deployment where the node's web/API port is reachable by the attacker (which is the default Chainlink node exposure model — port 6688 for UI/API/CLI) and LOOP plugins are enabled. No credentials, tokens, or session cookies are required; only the plugin name (discoverable via the also-unauthenticated `/discovery` endpoint) is needed.

### Recommendation
Wrap `loopRoutes` handlers in the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` middleware used for `authv2`/`metricRoutes`, and consider requiring at least `RequiresRunRole`/`RequiresAdminRole` given the operational sensitivity of triggering CPU profiling. Additionally validate/allowlist the wildcard `profile` path parameter before forwarding to the internal LOOP plugin URL, and bound the `seconds` parameter to prevent resource-exhaustion via excessively long profiling windows.

### Proof of Concept
Against a running node exposing its web server (default port 6688) with a registered LOOP plugin `myplugin`, an unauthenticated client can issue:
```
GET /discovery HTTP/1.1
Host: node:6688
```
to enumerate plugin names, then:
```
GET /plugins/myplugin/debug/pprof/profile?seconds=60 HTTP/1.1
Host: node:6688
```
with no `X-API-KEY`/`X-API-SECRET` headers or session cookie — the request succeeds and forces the plugin's process to perform a 60-second CPU profile. Repeating this concurrently across all plugin names causes sustained CPU exhaustion without any authentication.

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

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/loop_registry.go (L130-148)
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
