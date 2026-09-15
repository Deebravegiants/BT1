### Title
Unauthenticated pprof-profiling DoS via `/plugins/:name/debug/pprof/*profile` - ([File: core/web/loop_registry.go])

### Summary
Chainlink's node API router mounts `loopRoutes` on the base `api` group, which only carries a rate limiter and session middleware, unlike `debugRoutes` which explicitly requires `auth.Authenticate` [1](#0-0) . The pprof-forwarding endpoint `/plugins/:name/debug/pprof/*profile` lets any unauthenticated client control the profiling duration (`seconds` query parameter) forwarded to a plugin process, causing the node to hold an outbound HTTP request/goroutine open for a client-controlled amount of time.

### Finding Description
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on `api`, which is only gated by `rateLimiter(...)` and `sessions.Sessions(...)` — no `auth.Authenticate` call is applied, unlike `sessionRoutes`'s `/sessions` DELETE endpoint or `debugRoutes`'s `/debug/vars` [2](#0-1) . This means these endpoints are reachable by any unprivileged client without a session cookie or API token.

`pluginPPROFHandler` reads the `seconds` query parameter directly from the incoming request and uses it, uncapped, to build both the timeout for the outbound request and the `seconds` value forwarded to the plugin's own `/debug/pprof/profile` (or similar CPU-profile) endpoint: [3](#0-2) 

`pprofURLVals` parses `seconds` from the query string with no upper bound validation, only adding a fixed `PPROFOverheadSeconds` (30s) on top of whatever value the client provided: [4](#0-3) 

An unauthenticated caller can therefore request `seconds=<very large>` repeatedly, causing the node to open many long-lived outbound HTTP connections/goroutines to the internal LOOP-plugin metrics port and hold them open for the requested duration (bounded only by the derived `context.WithTimeout`, which itself scales with the attacker-supplied value) via `doRequest`: [5](#0-4) 

This mirrors the CVE-2019-0548 bug class (ASP.NET Core improperly handling web requests, leading to disproportionate resource consumption/denial of service) but manifests here as an unauthenticated request whose parameters directly and unboundedly control how long node resources (goroutines, HTTP client connections, context timers) are held.

### Impact Explanation
Because the route is unauthenticated and the profiling duration is attacker-controlled with no maximum bound, a remote unprivileged client can repeatedly issue requests with large `seconds` values against any registered plugin name (existence of the plugin is validated, but the attacker can enumerate configured LOOP plugin names or brute force valid ones) to accumulate many simultaneously in-flight profiling requests. Each held connection consumes a goroutine and an HTTP client connection on the node for the full requested duration, which can degrade availability of the node's HTTP API server and its ability to service legitimate node-management requests — a denial-of-service condition analogous to the reported CVE.

### Likelihood Explanation
The endpoint requires no authentication and no special network position — only network reachability to the node's exposed HTTP API port, which is explicitly the "internet-facing" management surface. The only precondition is knowledge of a valid `pluginName` registered in `LoopRegistry`, which is discoverable via the equally-unauthenticated `/discovery` endpoint listed alongside it.

### Recommendation
Require `auth.Authenticate` (session or API token) on `loopRoutes`, consistent with `debugRoutes`. Additionally, cap the `seconds` parameter in `pprofURLVals` to a sane maximum (e.g., matching `PPROFOverheadSeconds`-scale bounds) and consider adding a per-endpoint concurrency limit for pprof-forwarding requests.

### Proof of Concept
1. Determine a registered LOOP plugin name via `GET /discovery` (no auth required).
2. Send repeated unauthenticated requests: `GET /plugins/<pluginName>/debug/pprof/profile?seconds=3600` (or the largest integer accepted) without any session cookie or API key.
3. Each request causes the node to open an outbound HTTP call to the plugin's internal metrics port with a timeout of `seconds + 30` seconds via `doRequest`, tying up a goroutine/connection for that duration [6](#0-5) .
4. Repeating this concurrently against the node's exposed HTTP API accumulates long-lived goroutines/connections, degrading availability of the node's management API.

### Citations

**File:** core/web/router.go (L87-91)
```go
	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)
```

**File:** core/web/router.go (L180-236)
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

func ginHandlerFromHTTP(h http.HandlerFunc) gin.HandlerFunc {
	return func(c *gin.Context) {
		h.ServeHTTP(c.Writer, c.Request)
	}
}

func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
}

func healthRoutes(app chainlink.Application, r *gin.RouterGroup) {
	hc := HealthController{app}
	r.GET("/readyz", hc.Readyz)
	r.GET("/public-readyz", hc.PublicReadyz)
	r.GET("/health", hc.Health)
	r.GET("/health.txt", func(context *gin.Context) {
		context.Request.Header.Set("Accept", gin.MIMEPlain)
	}, hc.Health)
}

func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
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
