## Analysis

The pyload bug class is: **an unauthenticated route serves internal/sensitive server state that should require authentication**, due to a route being wired up without any access-control middleware. Searching for the closest structural analog in this codebase — chainlink node's HTTP API (`gin`-based, not Flask) — the strongest candidate is the `loopRoutes` registration in the node router, which forwards to internal debug/profiling endpoints without any authentication middleware, unlike every other sensitive route in the same file.

### Title
Unauthenticated exposure of LOOP plugin `pprof` debug/profiling and metrics proxy endpoints - (File: `core/web/router.go`, `core/web/loop_registry.go`)

### Summary
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the top-level `api` router group, which only carries rate-limiting and session middleware — no `auth.Authenticate(...)` wrapper is applied, unlike every other sensitive route family in the same file (`debugRoutes`, `metricRoutes`, `v2Routes`).

### Finding Description
In `core/web/router.go`, `NewRouter` builds the `api` group with only rate limiting and session middleware, then calls: [1](#0-0) 

Compare this to `debugRoutes`, which explicitly wraps its `/debug/vars` route in `auth.Authenticate(...)`, and `metricRoutes`, which is only mounted inside the authenticated `authv2` group at line 446: [2](#0-1) [3](#0-2) 

`loopRoutes`, however, registers pprof-proxying and metrics-proxying handlers with zero authentication: [4](#0-3) 

The handlers themselves, in `core/web/loop_registry.go`, forward the request to an internal plugin's pprof/metrics HTTP server based solely on the `:name` path param (a plugin name such as `solana`, `starknet`, `median`) with no additional check: [5](#0-4) [6](#0-5) 

This is analogous to the pyload issue in spirit — a debug/introspection surface (`render/<path>` in pyload, `pprof`/metrics proxy here) is reachable by any unauthenticated actor because it was wired into the router outside of the authentication middleware chain that protects the rest of the sensitive API surface, even though the intent (per `plugins/README.md`) was only to expose the coarse `/discovery` and `/metrics` endpoints for Prometheus scraping — not full Go `pprof` debug endpoints (`heap`, `profile`, `trace`, `goroutine`, `cmdline`, `symbol`).


### Impact Explanation
An unauthenticated network client that can reach the node's web server can pull full `pprof` profiles (`heap`, `goroutine`, `trace`, arbitrary `debug=N`/`seconds=N` CPU profiles) from any registered LOOP plugin process. Heap/goroutine dumps can contain sensitive in-memory data (e.g., decrypted key material, secrets, connection strings) handled by the plugin process, and repeated CPU-profile/trace requests can be used to degrade plugin availability. This is weaker than the pyload `SECRET_KEY` leak (which is a single deterministic disclosure), since pprof output is not guaranteed to contain secrets, but it is a genuine "unauthenticated actor obtains internal runtime introspection data that was intended to be gated" analog.

### Likelihood Explanation
Any client able to reach the node's HTTP listener can enumerate registered plugin names (a small, guessable set — `median`, `solana`, `starknet`, etc., as referenced in `plugins/README.md`) and issue `GET /plugins/<name>/debug/pprof/heap` or similar without any credentials, since the route is outside the authenticated route groups.

### Recommendation
Wrap the pprof-proxying routes (`/plugins/:name/debug/pprof/*profile`, `/plugins/:name/debug/pprof/symbol`) in the same `auth.Authenticate(...)` middleware used by `debugRoutes`/`metricRoutes`, and reserve unauthenticated access only for the coarse `/discovery` and `/plugins/:name/metrics` endpoints that are meant for Prometheus scraping, matching the documented intent in `plugins/README.md`.

### Proof of Concept
1. Start a chainlink node with a LOOP plugin registered (e.g. `median`, `solana`).
2. As an unauthenticated client, issue: `curl http://<node-host>:6688/plugins/median/debug/pprof/heap?debug=1`
3. Observe the full heap profile of the plugin process returned without any authentication, per the unauthenticated route registration in `loopRoutes` (`core/web/router.go:230-236`) and the forwarding logic in `pluginPPROFHandler` (`core/web/loop_registry.go:150-166`).

### Citations

**File:** core/web/router.go (L87-93)
```go
	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)

	guiAssetRoutes(engine, config.Insecure().DisableRateLimiting(), app.GetLogger())
```

**File:** core/web/router.go (L180-199)
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

**File:** core/web/router.go (L438-446)
```go
		buildInfo := BuildInfoController{app}
		authv2.GET("/build_info", buildInfo.Show)

		vault := VaultController{app}
		authv2.POST("/vault/dkg_results/verify", auth.RequiresEditRole(vault.VerifyDKGResult))
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))

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
