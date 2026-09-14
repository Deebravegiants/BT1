## Analysis

This maps directly to a known chainlink issue: `core/web/router.go`'s `loopRoutes` registers the LOOP plugin debug/pprof and service-discovery endpoints on the main HTTP API router **without any authentication middleware**, unlike every other sensitive route in the file (e.g. `debugRoutes`, which explicitly wraps `/debug/vars` in `auth.Authenticate`).

### Title
Unauthenticated exposure of LOOP plugin `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` endpoints enables information disclosure and DoS - (File: core/web/router.go, core/web/loop_registry.go)

### Summary
`loopRoutes` registers four HTTP handlers directly on the unauthenticated portion of the gin router group with no session/token check, allowing any remote unprivileged client that can reach the node's web port to trigger internal pprof profiling, read metrics, or enumerate plugin discovery data.

### Finding Description
`NewRouter` builds a single `api` route group protected only by a rate limiter and cookie-session middleware (neither of which enforces authentication), then calls `loopRoutes(app, api)`. [1](#0-0) 

Compare this to `debugRoutes`, which explicitly requires a valid session before exposing `expvar`: [2](#0-1) 

`loopRoutes` registers its handlers with no auth wrapper at all: [3](#0-2) 

The handlers themselves proxy to internal LOOP plugin debug servers based on attacker-supplied path/query parameters, with no authentication check inside the handler code either: [4](#0-3) [5](#0-4) 

`pprofURLVals` passes through an attacker-controlled `seconds` query parameter that is used both as the pprof profiling duration and to compute the forwarding-request timeout, so a remote unauthenticated caller directly controls how long the node holds a CPU-profiling connection open.

### Impact Explanation
An unauthenticated remote attacker can:
- Call `/discovery` to enumerate internal plugin names and the node/plugin metrics topology (information disclosure), as `discoveryHandler` returns plugin names and hosts without any credential check.
- Call `/plugins/:name/debug/pprof/profile?seconds=N` repeatedly with large `N` to hold open long-running CPU profiling sessions against LOOP plugins, consuming node/plugin resources — a denial-of-service vector directly analogous to the OctoPrint report ("obtain sensitive information or cause a denial of service via HTTP requests").
- Pull `/plugins/:name/debug/pprof/heap` or `goroutine` dumps, which can leak in-memory state (including potentially sensitive data held by the plugin process) to an unauthenticated caller.

This matches the "internet-facing gateway (handlers, allowlist bypass)" analog category explicitly in scope, since these routes sit on the same public router as authenticated `/v2/*` API routes but bypass `auth.Authenticate` entirely.

### Likelihood Explanation
No credentials, tokens, or session cookies are required — any client capable of sending an HTTP request to the node's configured web/API port can trigger these handlers, exactly the "unprivileged actor" scenario in scope for this analog.

### Recommendation
Wrap `loopRoutes` (or at minimum the pprof/metrics/discovery handlers) in the same `auth.Authenticate(app.AuthenticationProvider(), ...)` middleware used by `debugRoutes`, or bind these debug endpoints to a separate internal-only listener/port that is not exposed on the public API router, consistent with how `metricRoutes`' pprof handlers are intended to be operator-only.

### Proof of Concept
1. Start a chainlink node with the standard web server enabled and at least one LOOP plugin registered.
2. Without any session cookie or `X-API-KEY`/`X-API-SECRET` headers, send: `GET http://<node>:<port>/discovery` — returns plugin discovery JSON.
3. Send: `GET http://<node>:<port>/plugins/<plugin-name>/debug/pprof/profile?seconds=60` repeatedly from multiple connections — each request holds the connection/goroutine open for up to 60+30 seconds per `PPROFOverheadSeconds`, with no rate limiting keyed to authentication, causing resource exhaustion.
4. Send: `GET http://<node>:<port>/plugins/<plugin-name>/debug/pprof/heap` — dumps plugin heap memory to the unauthenticated caller.

### Citations

**File:** core/web/router.go (L77-92)
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
