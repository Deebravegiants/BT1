### Title
Unauthenticated access to LOOP plugin metrics/pprof proxy routes allows internal-network SSRF-style path forwarding - ([File: core/web/router.go])

### Summary
The `loopRoutes` handler group registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the top-level `api` router group, which only carries rate-limiting and session middleware — no authentication is required to reach these endpoints, unlike every other sensitive route in the router (`v2Routes`, `debugRoutes`, and the authenticated `metricRoutes` mounted under `authv2`).

### Finding Description
`NewRouter` builds an `api` group with only `rateLimiter` and `sessions.Sessions` middleware, and then calls `loopRoutes(app, api)` before any authentication middleware is attached to those specific routes: [1](#0-0) 

`loopRoutes` itself adds no `auth.Authenticate` wrapper, unlike `debugRoutes`, which explicitly requires a session, or `metricRoutes` (pprof for the node itself), which is only invoked inside the authenticated `authv2` group: [2](#0-1) [3](#0-2) [4](#0-3) 

The unauthenticated `pluginPPROFHandler` builds a forwarding URL to an internal LOOP-plugin process by directly concatenating the caller-supplied `*profile` wildcard path parameter and forwarding query parameters (`debug`, `gc`, `seconds`) without any path validation, before proxying the request to `http://<loopHostName>:<PrometheusPort>/debug/pprof/<profile>`: [5](#0-4) [6](#0-5) 

Similarly, `pluginMetricHandler` and `pluginPPROFPOSTSymbolHandler` proxy GET/POST requests to the internal plugin's Prometheus/pprof port with no caller authentication: [7](#0-6) [8](#0-7) 

This mirrors the reported bug class: administrative/internal-facing routes (here, LOOP plugin debug/metrics proxy routes) mounted at a path that bypasses the node's normal authentication gate, reachable by any client that can reach the node's HTTP port.

### Impact Explanation
Any unauthenticated client that can reach the Chainlink node's web server port can:
- Enumerate registered LOOP plugins and their internal Prometheus ports via `/discovery`.
- Pull raw Prometheus metrics for any plugin via `/plugins/:name/metrics`, which may reveal internal runtime/operational details.
- Trigger CPU/heap/goroutine profiling (`/plugins/:name/debug/pprof/*profile`) with attacker-controlled `seconds`/`debug`/`gc` query parameters, which can cause the plugin process to block for extended, attacker-chosen durations — an availability/DoS vector.
- Because `profile` is taken verbatim from the URL and concatenated into the forwarded path, a caller has some ability to influence the exact internal path requested on the plugin's HTTP listener, extending reach beyond the intended `/debug/pprof/*` namespace on that internal port.

There is no direct disclosure of node private keys/credentials via this path, but it exposes internal operational data and a resource-exhaustion primitive to unauthenticated callers, consistent with the CWE-306 (missing authentication) class in the reference advisory.

### Likelihood Explanation
Any actor with network access to the node's HTTP port (the same actor who could hit `/v2/*` endpoints) can trigger this without credentials, since the routes are mounted before/outside the authentication middleware chain. Likelihood is high for any deployment where the node's web port is reachable to more than a fully trusted operator (e.g., shared LAN, proxied ingress), matching the "same trust boundary" reachability described in the analog advisory.

### Recommendation
Require the same authentication used for `metricRoutes`/`debugRoutes` (`auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, gated by an appropriate role) before dispatching to `loopRoutes` handlers, or restrict access to only the local/loopback network the way the ha-mcp fix restricted its root-mounted routes to the trusted Supervisor origin.

### Proof of Concept
```
GET /discovery HTTP/1.1
Host: <node-host>:6688

GET /plugins/<name>/metrics HTTP/1.1
Host: <node-host>:6688

GET /plugins/<name>/debug/pprof/profile?seconds=60 HTTP/1.1
Host: <node-host>:6688
```
No session cookie or API token is required for any of the above requests because `loopRoutes` is registered on the base `api` group without an authentication middleware, per [9](#0-8) .

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

**File:** core/web/loop_registry.go (L168-215)
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
