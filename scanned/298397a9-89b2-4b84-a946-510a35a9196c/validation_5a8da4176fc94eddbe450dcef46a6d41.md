### Title
Unauthenticated Exposure of Diagnostic pprof/Metrics Endpoints for LOOP Plugins - (File: core/web/loop_registry.go)

### Summary
The Chainlink node's HTTP API exposes `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` without any authentication middleware, unlike the node's own `/debug/vars` route which is explicitly wrapped in session authentication. This mirrors the JGroups `DiagnosticsHandler` bug class (CVE-2013-4112): a diagnostic/debug interface reachable by an unauthorized, unauthenticated actor that discloses sensitive runtime information (heap/goroutine/CPU-profile dumps, prometheus metrics) for internal LOOP plugin processes.

### Finding Description
In `core/web/router.go`, `debugRoutes` explicitly requires session authentication before exposing `expvar`: [1](#0-0) 

However `loopRoutes`, registered right after it on the same unauthenticated `api` group (which only has rate limiting and session-store middleware, not an authentication check), exposes plugin diagnostics with no auth guard at all: [2](#0-1) [3](#0-2) 

The handlers in `core/web/loop_registry.go` proxy these unauthenticated requests straight through to each LOOP plugin's internal Prometheus/pprof HTTP server: [4](#0-3) [5](#0-4) 

`pluginPPROFHandler` forwards the caller-controlled `:profile` path segment and query parameters (`debug`, `gc`, `seconds`) directly into the backing plugin's `/debug/pprof/<profile>` endpoint and streams the raw response back to the caller: [6](#0-5) 

Since no session/API-key check gates these routes, any network client that can reach the node's web server (the same interface that serves the authenticated `/v2` job/key management API) can retrieve plugin metrics and full pprof dumps (heap, goroutine, profile, trace) without ever authenticating.

### Impact Explanation
pprof heap/goroutine/trace dumps of a LOOP plugin process can contain sensitive in-memory data (e.g., request payloads, internal state, potentially secret material handled by the plugin), and always disclose internal topology/configuration (`PrometheusPort`, internal hostnames, running goroutine stacks) useful for further attacks. This is a direct, unauthenticated information-disclosure exposure analogous to the JGroups `DiagnosticsHandler` CVE, and the `/profile` and `/trace` variants can also be abused to tie up plugin CPU/goroutines for the configured duration, causing resource exhaustion without any credentials.

### Likelihood Explanation
Any client with network access to the node's HTTP listener can trigger this with a simple unauthenticated GET request — no valid session, API key, or credential of any kind is required, and the routes are registered unconditionally whenever LOOP plugins are configured.

### Recommendation
Wrap `loopRoutes` (or at minimum the `/plugins/:name/metrics` and `/plugins/:name/debug/pprof/*` routes) with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` middleware used by `debugRoutes`, or otherwise restrict these endpoints to trusted internal callers (e.g., separate internal-only listener/network policy) rather than exposing them on the primary API surface.

### Proof of Concept
1. Start a Chainlink node with a LOOP plugin registered (e.g., a Median/EVM LOOPP).
2. Without logging in or presenting any session cookie/API key, send:
   `GET http://<node-host>:<web-port>/plugins/<plugin-name>/debug/pprof/heap?debug=1`
3. The request is routed by `pluginPPROFHandler` straight to the plugin's internal pprof server and the raw heap dump is returned to the unauthenticated caller, as shown in `core/web/loop_registry.go:150-166`.

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
