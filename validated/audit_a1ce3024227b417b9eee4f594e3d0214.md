Audit Report

## Title
Unauthenticated Exposure of Diagnostic pprof/Metrics Endpoints for LOOP Plugins - (File: core/web/loop_registry.go)

## Summary
The `loopRoutes` function in `core/web/router.go` registers `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` on the same unauthenticated `api` gin group that only carries rate-limiting and session-store middleware, with no `auth.Authenticate` wrapper, unlike the node's own `/debug/vars` route in `debugRoutes` which is explicitly gated by `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`. This lets any unauthenticated network client that can reach the node's HTTP listener pull full pprof dumps (heap/goroutine/profile/trace) and Prometheus metrics from internal LOOP plugin processes.

## Finding Description
`NewRouter` builds the primary `api` group with only rate limiting and session-store middleware (no authentication check) at `core/web/router.go:78-85`, then calls `loopRoutes(app, api)` at line 91 alongside `debugRoutes(app, api)` at line 87. `debugRoutes` correctly wraps its `/debug/vars` route in a dedicated authenticated sub-group: `group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))` (`core/web/router.go:180-183`). `loopRoutes`, in contrast, registers its routes directly on the passed-in unauthenticated group with no auth middleware at all (`core/web/router.go:230-236`).

The handlers in `core/web/loop_registry.go` confirm the routes perform no session/token check before proxying: `pluginMetricHandler` (lines 96-128) builds `pluginURL := fmt.Sprintf("http://%s:%d/metrics", l.loopHostName, p.EnvCfg.PrometheusPort)` and forwards the request/response with no auth gate; `pluginPPROFHandler` (lines 150-166) similarly builds `pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), ...)`, appends caller-supplied `debug`/`gc`/`seconds` query parameters via `pprofURLVals` (lines 132-148), and streams the plugin's raw pprof response back via `doRequest` (lines 190-215). None of these handlers call any authentication or authorization helper, and the routes are mounted on a `RouterGroup` without any such middleware in its chain, unlike every route under `v2Routes`'s `authv2` group (`core/web/router.go:245-248`) or `debugRoutes`.

## Impact Explanation
This is an in-scope, unauthenticated information-disclosure vulnerability: pprof heap/goroutine/trace dumps of the plugin process can reveal in-memory state, internal topology (`PrometheusPort`, internal hostnames), and running goroutine stacks, and the `/profile`/`/trace` variants accept a caller-controlled `seconds` parameter that ties up plugin CPU for that duration, enabling a lightweight resource-exhaustion vector — all without any credential. This falls squarely within the class of "node API authentication bypass / unauthenticated disclosure of internal runtime state," which is a legitimate Chainlink node security concern, and is not covered by the SECURITY.md exclusion for "server-side non-confidential information disclosure" since heap/goroutine dumps can contain more than IPs/server names (in-flight payloads, internal state).

## Likelihood Explanation
Any client with network reachability to the node's web server — the same interface serving the authenticated `/v2` API — can issue a plain unauthenticated `GET` to trigger this; no session cookie, API key, or role is required, and the routes are registered unconditionally whenever LOOP plugins are configured in `loopRoutes` (`core/web/router.go:230-236`). This requires no operator/admin access, no leaked credentials, and no host-level access, satisfying the "unprivileged actor" bar.

## Recommendation
Wrap the `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` routes with the same session/token authentication middleware used elsewhere (e.g., `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`), consistent with how `debugRoutes` protects `/debug/vars`, or move these diagnostic endpoints to a separate internal-only listener not exposed on the primary API surface.

## Proof of Concept
1. Start a Chainlink node with a LOOP plugin registered (e.g., a Median/EVM LOOPP), with the web server reachable on `<node-host>:<web-port>`.
2. Without any session cookie or API key, send:
   `GET http://<node-host>:<web-port>/plugins/<plugin-name>/debug/pprof/heap?debug=1`
3. Observe that `pluginPPROFHandler` (`core/web/loop_registry.go:150-166`) forwards the request to the plugin's internal pprof server and returns the raw heap dump with HTTP 200, with no authentication challenge at any point in the request path (`core/web/router.go:78-91, 230-236`). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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
