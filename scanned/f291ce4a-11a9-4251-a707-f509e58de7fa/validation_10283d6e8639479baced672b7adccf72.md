### Title
Unauthenticated LOOP plugin pprof proxy allows path injection into internal SSRF request - (File: core/web/loop_registry.go)

### Summary
The reported spotipy bug (CVE-2023-23608) is a path-traversal-class issue where a client-supplied URI/URL fragment is spliced into an API request path without proper validation, letting the caller redirect the request to an unintended endpoint. The chainlink Go node has an analog in `LoopRegistryServer.pluginPPROFHandler`, which builds an internal HTTP request URL by directly concatenating a user-controlled wildcard route parameter into a `fmt.Sprintf` format string, and that endpoint is registered without any authentication middleware.

### Finding Description
`pluginPPROFHandler` takes the gin wildcard parameter `profile` straight from the request path and splices it into the outbound request URL: [1](#0-0) 

```go
pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), l.loopHostName, p.EnvCfg.PrometheusPort)
```

`gc.Param("profile")` is completely attacker-controlled — it is not validated against the fixed set of legitimate pprof profile names (`cmdline`, `profile`, `symbol`, `trace`, `allocs`, `block`, `goroutine`, `heap`, `mutex`, `threadcreate`), and it is inserted as-is into a `fmt.Sprintf` format string used to build the target URL before the request is dispatched with `l.doRequest`. This mirrors the spotipy flaw: a value intended to select one of a small set of known sub-resources is used to build the target path with no allowlist/canonicalization, letting the caller redirect the request to an arbitrary path on the internal LOOP plugin host (`l.loopHostName:p.EnvCfg.PrometheusPort`), or inject additional path segments/format-string style content (`%`-sequences are also unsanitized since the parameter feeds directly into `fmt.Sprintf`'s format string, not just an argument).

Critically, this handler is reachable without authentication. In `core/web/router.go`, `loopRoutes(app, api)` is invoked directly on the base `api` group with no `auth.Authenticate(...)` wrapper, unlike every other sensitive group (`debugRoutes`, `authv2`, etc.), which are explicitly wrapped in `auth.Authenticate`: [2](#0-1) [3](#0-2) [4](#0-3) 

So `/plugins/:name/debug/pprof/*profile` is registered as an unauthenticated route while the equivalent standard-library `/debug/pprof/*` group (`metricRoutes`) is deliberately placed inside the authenticated `authv2` group, confirming pprof-style endpoints are treated as sensitive elsewhere in this codebase but this LOOP-proxy variant is exposed to any unauthenticated caller who can reach the node's web port.

### Impact Explanation
Any unauthenticated network client that can reach the node's HTTP API can invoke this handler for any registered LOOP plugin name (validated only via `l.registry.Get(pluginName)`), then supply an arbitrary `profile` path segment that is spliced into an outbound request URL to the plugin's internal Prometheus-labeled port. Because the URL is built without canonicalizing or allowlisting the path, this could be used to probe or hit other endpoints exposed on that internal host:port beyond the intended `/debug/pprof/*` surface (SSRF-adjacent path confusion), and because the value is inserted into the format string of `fmt.Sprintf` rather than passed as an argument, unexpected `%` verbs in the attacker input could also cause malformed URLs or Go format-string panics/undefined output. This is unauthenticated cross-boundary request confusion analogous to the spotipy advisory's redirection of API calls to unintended endpoints.

### Likelihood Explanation
High: the route requires no authentication, no special network position, and only knowledge of a registered plugin name (obtainable via the also-unauthenticated `/discovery` endpoint, which lists all registered plugin names). This is a straightforward, remotely reachable, unprivileged-actor path.

### Recommendation
1. Restrict the `profile` parameter to an explicit allowlist of the pprof sub-paths handled by `metricRoutes` (`cmdline`, `profile`, `symbol`, `trace`, `allocs`, `block`, `goroutine`, `heap`, `mutex`, `threadcreate`, and index) before constructing the outbound URL, rejecting anything else with 404/400.
2. Build the target URL using `url.URL{Scheme, Host, Path: path.Join(...)}` (with `path.Clean`) rather than `fmt.Sprintf` string concatenation, and never pass user input as part of a `fmt.Sprintf` format string.
3. Require authentication (`auth.Authenticate(...)`) on the `loopRoutes` group, consistent with how `debugRoutes`/`metricRoutes` are gated elsewhere in `core/web/router.go`.

### Proof of Concept
1. Discover a registered plugin name via the unauthenticated `GET /discovery` endpoint (returns plugin names in Prometheus service-discovery JSON). [5](#0-4) 
2. Send an unauthenticated request:
```
GET /plugins/<pluginName>/debug/pprof/../../../<arbitrary-path>?<injected>
```
3. `pluginPPROFHandler` builds `pluginURL := fmt.Sprintf("http://<loopHostName>:<PrometheusPort>/debug/pprof/" + "../../../<arbitrary-path>?<injected>", ...)` and forwards the request via `l.doRequest`, returning the response body to the unauthenticated caller — demonstrating that the path segment intended only for the fixed pprof sub-resource set is used unchecked to redirect the internal request. [6](#0-5)

### Citations

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
