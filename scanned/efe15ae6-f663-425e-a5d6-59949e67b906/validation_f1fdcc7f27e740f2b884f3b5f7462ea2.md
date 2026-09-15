### Title
Unauthenticated pprof/metrics endpoints for LOOP plugins expose sensitive debug data - (File: core/web/router.go, core/web/loop_registry.go)

### Summary
Chainlink's HTTP API router wires the LOOP plugin discovery, metrics, and pprof endpoints onto the base `api` route group, which only has rate limiting and session middleware attached — not the `auth.Authenticate(...)` middleware used everywhere else in the router. This means `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` are reachable by any unauthenticated network client, analogous to the Dapr Dashboard CVE-2022-38817 pattern of an operator-facing panel exposing sensitive data due to missing access control.

### Finding Description
`NewRouter` builds an `api` group with only rate limiting and cookie-session middleware [1](#0-0) , and then calls `loopRoutes(app, api)` on that same unauthenticated group: [2](#0-1) 

Compare this to every other sensitive route group in the same file, which is explicitly wrapped in `auth.Authenticate(...)` before being exposed (e.g. `authv2`, `ethKeysGroup`, `userOrEI`) [3](#0-2) [4](#0-3) . There is even a comment in the same file distinguishing the properly-guarded debug routes from these ("Debug routes accessible via authentication" applies to `metricRoutes(authv2)`, not `loopRoutes`) [5](#0-4) .

The pprof handler forwards requests directly to the internal LOOP plugin's `/debug/pprof/*` endpoint and streams the raw response back to the caller without any authentication check: [6](#0-5) [7](#0-6) 

The node's own configuration documentation acknowledges that heap/pprof dumps "may potentially expose sensitive data e.g. private key components" [8](#0-7) , confirming the impact class of this exposure.

### Impact Explanation
An unauthenticated network client can retrieve heap dumps, goroutine stacks, CPU profiles, and Prometheus metrics for any installed LOOP plugin by hitting `/plugins/:name/debug/pprof/heap` (or `/goroutine`, `/profile`, etc.) and `/plugins/:name/metrics`, without providing any session cookie or API token. Heap/goroutine dumps from a long-running Go process can contain sensitive in-memory data (potentially key material, internal identifiers, or other secrets held in plugin memory), matching the CWE-306 "Incorrect Access Control" / sensitive-data-disclosure pattern in the referenced advisory.

### Likelihood Explanation
High likelihood for any node with the LOOP registry populated and its web server reachable: the routes are registered unconditionally in `loopRoutes`, require no credentials, and are trivially reachable via a normal HTTP GET/POST from any unprivileged client that can reach the node's HTTP port.

### Recommendation
Move `loopRoutes(app, api)` (or at minimum the `/plugins/:name/debug/pprof/*` and `/plugins/:name/metrics` handlers) behind the same `auth.Authenticate(...)` + `auth.RequiresAdminRole` (or equivalent) middleware chain used for other sensitive/debug endpoints (e.g. as done for `metricRoutes(authv2)`), or otherwise restrict these endpoints to trusted internal networks only.

### Proof of Concept
Against a running node, without any session cookie or `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers:
```
GET /plugins/<plugin-name>/debug/pprof/heap?debug=1 HTTP/1.1
Host: <node-host>
```
This request is served by `pluginPPROFHandler` via the unauthenticated `api` route group and returns the raw heap profile from the internal plugin process.

### Citations

**File:** core/web/router.go (L78-91)
```go
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

**File:** core/web/router.go (L445-446)
```go
		// Debug routes accessible via authentication
		metricRoutes(authv2)
```

**File:** core/web/router.go (L450-454)
```go
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
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

**File:** core/config/docs/core.toml (L4-7)
```text
# **ADVANCED**
# InsecurePPROFHeap allows dumping the heap in pprof. This is very useful for debugging memory leaks but in certain rare cases may potentially expose sensitive data e.g. private key components, so is disabled by default.
# Deprecated: no effect. Always enabled.
InsecurePPROFHeap = true # Default
```
