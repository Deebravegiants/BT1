Audit Report

## Title
Unauthenticated exposure of LOOP plugin `pprof` debug/profiling endpoints - (File: `core/web/router.go`)

## Summary
The `loopRoutes` function registers `/plugins/:name/debug/pprof/*profile` and `/plugins/:name/debug/pprof/symbol` directly on the top-level `api` router group, which carries only rate-limiting and session middleware, with no `auth.Authenticate(...)` wrapper. This contrasts with every other debug/introspection surface in the same file (`debugRoutes`, `metricRoutes`), which are explicitly gated behind session or v2 authentication.

## Finding Description
`NewRouter` builds `api` with only rate limiting and cookie sessions [1](#0-0) , then calls `loopRoutes(app, api)` which registers the pprof-proxy handlers with zero authentication middleware: [2](#0-1)  (matching the reported line range in this repo's file). By contrast, `debugRoutes` explicitly wraps `/debug/vars` in `auth.Authenticate(...)` [3](#0-2) , and `metricRoutes` (the standard Go `net/http/pprof` handlers) is mounted only inside the authenticated `authv2` group.

The handler implementation confirms the forwarding is unauthenticated and driven solely by the `:name` path param: `pluginPPROFHandler` builds a URL to the plugin's internal pprof server and proxies the request with no additional authorization check [4](#0-3) , and `pluginMetricHandler`/`pluginPPROFPOSTSymbolHandler` behave the same way [5](#0-4) [6](#0-5) . The documented intent in `plugins/README.md` is that only `/discovery` and `/plugins/<name>/metrics` should be reachable, to support Prometheus scraping — full `pprof` debug endpoints (`heap`, `goroutine`, `profile`, `trace`, `symbol`) are not part of that documented, intentionally-exposed surface [7](#0-6) .

## Impact Explanation
An unauthenticated network client reaching the node's HTTP listener can pull `pprof` heap/goroutine dumps and CPU profiles from any registered LOOP plugin process by guessing/enumerating plugin names (a small known set: `median`, `solana`, `starknet`). Heap and goroutine dumps can contain sensitive in-process data. This is an authentication-bypass on an internal introspection surface that was clearly intended to be routed only for coarse metrics scraping, not full debug/profiling access — a genuine node API authentication gap, distinct from a pure denial-of-service concern (which is separately excluded by the program's rules).

## Likelihood Explanation
No credentials are required: any client that can reach the node's configured web server port can issue a plain HTTP GET to `/plugins/<name>/debug/pprof/heap` (or `/profile`, `/trace`, etc.) since the route sits in the `api` group outside any `auth.Authenticate` wrapper, unlike the structurally identical `metricRoutes` pprof handlers, which require v2 session/API-key authentication.

## Recommendation
Wrap `/plugins/:name/debug/pprof/*profile` and `/plugins/:name/debug/pprof/symbol` in the same `auth.Authenticate(...)` middleware applied to `debugRoutes`/`metricRoutes`, leaving only `/discovery` and `/plugins/:name/metrics` unauthenticated for Prometheus scraping, consistent with the documented design intent in `plugins/README.md`.

## Proof of Concept
1. Start a chainlink node with a LOOP plugin registered (e.g., set `CL_MEDIAN_CMD` per `plugins/README.md`).
2. As an unauthenticated client, run: `curl http://<node-host>:6688/plugins/median/debug/pprof/heap?debug=1`.
3. Observe a full heap profile of the plugin process returned with HTTP 200 and no authentication challenge, confirmed by the route registration in `core/web/router.go` (`loopRoutes`) and the forwarding logic in `pluginPPROFHandler` in `core/web/loop_registry.go`.

### Citations

**File:** core/web/router.go (L77-93)
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

	guiAssetRoutes(engine, config.Insecure().DisableRateLimiting(), app.GetLogger())
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

**File:** core/web/loop_registry.go (L168-188)
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
```

**File:** plugins/README.md (L30-44)
```markdown
#### Prometheus


LOOPPs are dynamic, and so must be monitoring. 
We use Plugin discovery to dynamically determine what to monitor based on what plugins are running
and we route external prom scraping to the plugins without exposing them directly

The endpoints are

`/discovery` : HTTP Service Discovery [https://prometheus.io/docs/prometheus/latest/configuration/configuration/#http_sd_config]
Prometheus server is configured to poll this url to discover new endpoints to monitor. The node serves the response based on what plugins are running,

`/plugins/<name>/metrics`: The node acts as very thin middleware to route from Prometheus server scrape requests to individual plugin /metrics endpoint
Once a plugin is discovered via the discovery mechanism above, the Prometheus service calls the target endpoint at the scrape interval
The node acts as middleware to route the request to the /metrics endpoint of the requested plugin
```
