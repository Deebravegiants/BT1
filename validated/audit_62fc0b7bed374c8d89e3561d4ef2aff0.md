Note: "Impacts that only require DDoS" is explicitly out of scope, which limits (but does not entirely negate) part of the claimed DoS impact, though the information-disclosure impact (unauthenticated pprof/metrics data exposure) stands independently.

The code fully substantiates the claim: `loopRoutes(app, api)` is registered directly on the base `api` group with no `auth.Authenticate(...)` wrapper [1](#0-0) , unlike `debugRoutes` and `sessionRoutes`'s authenticated group, which explicitly wrap sensitive endpoints in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` [2](#0-1) [3](#0-2) . The `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` routes are registered unauthenticated [4](#0-3) . `pluginPPROFHandler` concatenates the unsanitized wildcard `gc.Param("profile")` directly into the internal request URL via `fmt.Sprintf` [5](#0-4) , and `doRequest` executes that request against the internal host with no further path validation [6](#0-5) . The only gate, `l.registry.Get(pluginName)`, checks against a fixed set of registered plugin names, not a secret, and that same name is also discoverable via the equally unauthenticated `/discovery` endpoint [7](#0-6) .

Audit Report

## Title
Unauthenticated LOOP-plugin pprof/metrics proxy endpoints allow unvalidated path injection into internal debug requests - (File: `core/web/router.go`, `core/web/loop_registry.go`)

## Summary
The `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` routes are registered without any authentication middleware, unlike every other sensitive route group in the router (`debugRoutes`, `sessionRoutes` auth group, `v2Routes`). `pluginPPROFHandler` forwards the raw, attacker-controlled wildcard `profile` path segment into an internally constructed HTTP request URL via unsanitized string concatenation, and dispatches it to an internal plugin host with no further validation.

## Finding Description
`loopRoutes(app, api)` is invoked directly on the base `api` group in `NewRouter` with no `auth.Authenticate(...)` wrapper [1](#0-0) , in contrast to `debugRoutes`, which explicitly requires `auth.AuthenticateBySession` before exposing `expvar` data [2](#0-1) , and `sessionRoutes`, which wraps `DELETE /sessions` similarly [3](#0-2) .

`pluginPPROFHandler` takes the gin wildcard parameter `profile` straight from the URL and concatenates it unsanitized into the target URL string via `fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), ...)` [5](#0-4) . This is then dispatched by `doRequest`, which builds and executes an `http.Request` against the internal host with no path validation [6](#0-5) .

The only gate is `l.registry.Get(pluginName)` matching a running plugin's name — an internally-known but not secret value, itself enumerable via the also-unauthenticated `discoveryHandler`, which lists all registered plugin names and their metrics paths [7](#0-6) .

## Impact Explanation
An unauthenticated remote client can reach internal Go `pprof` debug endpoints (goroutine dumps, heap/cpu profiles, `/debug/pprof/trace`) and the plugin's `/metrics` endpoint contents proxied through the node's public API, without any session or API token. This is an authentication-bypass class issue mapping to unauthorized access to internal node/plugin diagnostic data — a legitimate node API authentication-bypass impact. The claimed resource-exhaustion DoS component (via the attacker-controlled `seconds` parameter) is explicitly excluded per `SECURITY.md`, which lists "Impacts that only require DDoS" as out of scope [8](#0-7) ; the information-disclosure impact (unauthenticated exposure of pprof profiling data and plugin metrics) stands as the primary in-scope impact.

## Likelihood Explanation
High: the routes are reachable by any network client with no authentication token or session, the plugin name is discoverable via `/discovery`, and `pluginPPROFHandler` performs no validation on the `profile` wildcard before use.

## Recommendation
Wrap `loopRoutes(app, api)` with the same `auth.Authenticate(...)` middleware pattern used for `debugRoutes`/`sessionRoutes`'s authenticated group, or gate these routes behind the existing Prometheus bearer-token mechanism uniformly across `/discovery` and `/plugins/*`. Additionally validate/allowlist the `profile` wildcard value before constructing the forwarded URL in `pluginPPROFHandler`.

## Proof of Concept
1. Start a chainlink node with a LOOP plugin registered and running (a known plugin name present in `l.registry`).
2. Without any session cookie or API token, issue `GET /discovery` to enumerate the running plugin name via the JSON response built in `discoveryHandler`.
3. Issue `GET /plugins/<name>/debug/pprof/profile?seconds=5` unauthenticated; per `pluginPPROFHandler`/`doRequest`, the node proxies this straight to the plugin's internal pprof endpoint and returns the captured profile data with no authentication check performed anywhere in the request path [9](#0-8) .

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

**File:** core/web/router.go (L216-217)
```go
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
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

**File:** SECURITY.md (L44-44)
```markdown
- Impacts that only require DDoS.
```
