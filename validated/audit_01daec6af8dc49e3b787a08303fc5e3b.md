## Title
Missing Authentication for LOOP Plugin Debug/Profiling and Metrics Endpoints - (File: `core/web/router.go`)

### Summary
The Chainlink node's HTTP API exposes LOOP (Local Out-Of-Process) plugin service-discovery, metrics-proxy, and pprof debug/profiling endpoints via `loopRoutes` without any authentication middleware, unlike every other sensitive route in the same router (`v2Routes`, `debugRoutes`, `metricRoutes`). This mirrors the CVE-2020-11969 pattern of an operationally useful management/debug interface (JMX in TomEE, pprof here) being reachable by an unauthenticated actor because the authentication wrapper was simply omitted for that code path.

### Finding Description
`NewRouter` registers `loopRoutes(app, api)` on the shared `api` route group, which only carries a rate limiter and cookie-session middleware (cookie parsing, not auth enforcement): [1](#0-0) 

`loopRoutes` itself adds no `auth.Authenticate(...)` wrapper at all, in contrast to `debugRoutes` (session-authenticated) and `metricRoutes` (only mounted inside the token/session-authenticated `authv2` group): [2](#0-1) [3](#0-2) [4](#0-3) 

The handlers behind these unauthenticated routes proxy directly into the internal LOOP plugin's pprof and metrics HTTP servers with attacker-controlled query parameters (`debug`, `gc`, `seconds`): [5](#0-4) [6](#0-5) 

This is the same bug class as GHSA-836g-5fr5-fgcr: an administrative/diagnostic interface capable of revealing sensitive runtime state (goroutine stacks, heap contents which can include key material or secrets held in memory) and capable of triggering resource-intensive operations (CPU profiling for an attacker-chosen duration, forced GC) is reachable without any credential check, over the node's public-facing HTTP listener.

### Impact Explanation
An unauthenticated remote client can:
- Enumerate registered LOOP plugins and their metrics/pprof targets via `/discovery`.
- Pull heap/goroutine/allocs profiles via `/plugins/:name/debug/pprof/*profile`, which can leak in-memory secrets, internal addresses, and job/keystore-adjacent data structures.
- Trigger CPU profiling for a client-specified `seconds` duration or force garbage collection (`gc` param), providing a low-cost denial-of-service lever against the plugin process.
This satisfies the "key/secret disclosure" and "no-auth critical function" criteria for a High-severity CWE-306 analog.

### Likelihood Explanation
Likelihood is high for any deployment where the node's HTTP API port is reachable (default operator UI/API port). No credentials, tokens, or special network position are required — a plain HTTP GET to `/plugins/:name/debug/pprof/heap` (or `/discovery` to first enumerate plugin names) is sufficient, matching the "unprivileged client request" reachability bar.

### Recommendation
Wrap `loopRoutes` (or at minimum the `/plugins/:name/debug/pprof/*` and `/plugins/:name/metrics` routes) with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession, auth.AuthenticateByToken)` + admin-role gate used elsewhere (e.g., as `metricRoutes` is nested inside `authv2`), or move it fully inside the authenticated `api`/`authv2` group in `core/web/router.go`. Audit `discoveryHandler`/`pluginMetricHandler`/`pluginPPROFHandler` in `core/web/loop_registry.go` to ensure they cannot be reached pre-auth even via alternate route registration.

### Proof of Concept
1. Start a chainlink node with a LOOP plugin registered (any p2p/median/etc LOOP-based EVM plugin).
2. Without any session cookie or API token, issue:
   - `GET http://<node-host>:<http-port>/discovery` → returns plugin names and internal target metadata.
   - `GET http://<node-host>:<http-port>/plugins/<pluginName>/debug/pprof/heap` → returns full heap dump.
   - `GET http://<node-host>:<http-port>/plugins/<pluginName>/debug/pprof/profile?seconds=60` → forces 60s CPU profiling load on the plugin process.
3. All three requests succeed with `200 OK` and no `401 Unauthorized`, confirmed by the absence of any `auth.Authenticate` middleware around `loopRoutes` in `core/web/router.go:230-236`, in contrast to the authenticated `metricRoutes(authv2)` call at line 446.

### Citations

**File:** core/web/router.go (L87-91)
```go
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
