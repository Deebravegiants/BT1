## Finding [1](#0-0) 

The core web router registers LOOP-plugin pprof/metrics/discovery endpoints on the plain `api` group with no authentication middleware, unlike every other sensitive route group in the same file.

### Title
Unauthenticated exposure of LOOP-plugin pprof/metrics/discovery endpoints - (File: core/web/router.go)

### Summary
`loopRoutes` is mounted directly on the top-level `api` `*gin.RouterGroup` in `NewRouter`, which only carries a rate limiter and session middleware — it is never wrapped in `auth.Authenticate(...)` the way every comparable debug/metrics surface in the same file is.

### Finding Description
In `core/web/router.go`, `NewRouter` builds `api` with only rate limiting and cookie sessions, then calls: [2](#0-1) 

Compare this to the two other debug-style route groups defined in the very same file:
- `debugRoutes` explicitly wraps `/debug/vars` in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`. [3](#0-2) 
- `metricRoutes` (the native Go `pprof` handlers) is only ever invoked from inside the authenticated `authv2` group. [4](#0-3) 

`loopRoutes`, however, registers its four handlers with no authentication wrapper at all: [5](#0-4) 

These handlers, implemented in `core/web/loop_registry.go`, proxy requests to internal LOOP-plugin ports:
- `discoveryHandler` returns Prometheus service-discovery data listing every registered plugin's internal metrics path. [6](#0-5) 
- `pluginMetricHandler` fetches `/metrics` from the plugin's internal Prometheus port. [7](#0-6) 
- `pluginPPROFHandler` forwards an attacker-controlled `:profile` wildcard directly into a URL sent to the plugin's internal `/debug/pprof/` endpoint (heap, goroutine, profile, trace, allocs, etc.), and `pluginPPROFPOSTSymbolHandler` forwards a POST body to `/debug/pprof/symbol`. [8](#0-7) 

Because none of these routes pass through `auth.Authenticate`, any network-reachable client can, without credentials, enumerate registered LOOP plugins, pull their Prometheus metrics, and pull full Go `pprof` heap/goroutine/CPU-profile dumps of the plugin processes — analogous to the Zeppelin advisory's unauthenticated exposure of internal server resources via its cluster protocol.

### Impact Explanation
`pprof` heap and goroutine dumps can contain in-memory secrets (keys, tokens, decrypted payloads) and internal process/goroutine state; discovery/metrics responses reveal internal plugin topology and hostnames. This is server-resource disclosure reachable by any unauthenticated network client hitting the node's web server, matching the CWE-664 (improper resource control) bug class of the referenced advisory.

### Likelihood Explanation
High: the routes are reachable on the standard Chainlink node HTTP port with no credentials, subject only to the generic rate limiter, and require no special preconditions beyond the node running LOOP plugins (a common production configuration).

### Recommendation
Wrap `loopRoutes` registrations in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` (and an appropriate role check) the same way `debugRoutes` and `metricRoutes` are protected, or move these endpoints to an internal-only listener not exposed to the public web server group.

### Proof of Concept
Against a running node, without any session cookie or API token:
```
GET /discovery HTTP/1.1
Host: <node>:6688
```
returns plugin discovery data; then:
```
GET /plugins/<pluginName>/debug/pprof/heap HTTP/1.1
Host: <node>:6688
```
returns a full heap dump of the named LOOP plugin process with no authentication required, confirmed by the absence of any `auth.Authenticate` middleware around `loopRoutes(app, api)` in `core/web/router.go`.

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

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/loop_registry.go (L52-65)
```go
// discoveryHandler implements service discovery of prom endpoints for LOOPs in the registry
func (l *LoopRegistryServer) discoveryHandler(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	groups := make([]*targetgroup.Group, 0, 1+len(l.registry.List()))

	// add node metrics to service discovery
	groups = append(groups, pluginGroup(l.discoveryHostName, l.exposedPromPort, "/metrics"))

	// add all the plugins
	for _, registeredPlugin := range l.registry.List() {
		group := pluginGroup(l.discoveryHostName, l.exposedPromPort, pluginMetricPath(registeredPlugin.Name))
		group.Labels[LabelMetaPluginName] = model.LabelValue(registeredPlugin.Name)
		groups = append(groups, group)
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

**File:** core/web/loop_registry.go (L150-215)
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
