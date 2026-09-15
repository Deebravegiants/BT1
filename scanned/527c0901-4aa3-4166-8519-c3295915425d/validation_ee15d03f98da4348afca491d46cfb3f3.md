### Title
Unauthenticated Information Disclosure and Debug-Endpoint Exposure via `/discovery` and `/plugins/:name/...` routes - ([File: core/web/router.go])

### Summary
The `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` routes are registered on the base, unauthenticated `api` router group with no `auth.Authenticate` middleware, unlike every other sensitive `/v2` route in the same file. This mirrors the CVE-2026-27796 bug class: a metadata/introspection endpoint that should require authentication is instead reachable by any unauthenticated client, disclosing internal service topology and, via the pprof passthrough, live process debug data.

### Finding Description
`loopRoutes` is invoked directly on the `api` group in `NewRouter`, which only carries CORS/rate-limiting/session middleware — no authentication check: [1](#0-0) 

```go
func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
}
``` [2](#0-1) 

Contrast this with every other authenticated-role-gated route (`authv2`) requiring `auth.Authenticate(...)` and, for admin-only surfaces, `auth.RequiresAdminRole`, e.g. the node's own `/debug/pprof` (via `metricRoutes`) is only mounted under the authenticated `authv2` group: [3](#0-2) 

`discoveryHandler` enumerates all registered LOOP plugins and returns their names plus the internal Prometheus scrape hostname/port to any caller: [4](#0-3) 

`pluginPPROFHandler`/`pluginPPROFPOSTSymbolHandler` take an unauthenticated caller's `profile`/query parameters and forward them to the internal `/debug/pprof/*` endpoint of the named LOOP plugin process, then relay the raw response body back to the caller: [5](#0-4) 

pprof profiles (heap, goroutine, allocs, etc.) can capture in-memory data from the plugin process, and the `seconds`/`debug`/`gc` parameters are attacker-controlled, allowing an unauthenticated caller to trigger expensive CPU/heap profiling on demand: [6](#0-5) 

The project's own documentation confirms `/discovery` is intended purely for Prometheus scraping, not general client consumption, yet it is exposed on the public node port with no distinguishing auth boundary from the rest of the API: [7](#0-6) 

### Impact Explanation
- `/discovery` leaks internal node hostname, the Prometheus scrape port, and the full list of active LOOP plugin names to any unauthenticated network client reaching the node's HTTP port — directly analogous to Homarr's leak of "internal service URLs, integration names, and service types."
- The pprof-forwarding endpoints are more severe than the Homarr analog: they let an unauthenticated caller trigger heap/goroutine/CPU profiling of a LOOP plugin process and receive the raw profile data back over HTTP, which can expose process memory contents (potentially including sensitive runtime state) and enables a low-cost denial-of-service by requesting long-duration CPU profiles (`seconds` parameter, up to attacker's choosing plus `PPROFOverheadSeconds`).
- No `auth.Authenticate` or role check gates any of these four routes, so exploitation requires no credentials, matching the "unauthenticated" precondition of the CVE.

### Likelihood Explanation
High for `/discovery` and `/plugins/:name/metrics`: they are simple unauthenticated `GET` requests with no precondition beyond the node's public HTTP port being reachable and a LOOP plugin being registered (common in loop/plugin-enabled deployments, e.g. Solana/Median LOOPPs). The pprof endpoints require only knowing/guessing a registered plugin name (enumerable via `/discovery`), making the pprof abuse path directly chainable from the discovery leak.

### Recommendation
Move `loopRoutes` registration under the authenticated `authv2` group (or a dedicated authenticated admin group), consistent with how the node's own `/debug/pprof` routes are gated via `metricRoutes(authv2)`. If Prometheus scraping from an external, non-authenticated network segment is required, isolate `/discovery` and `/plugins/:name/metrics` on a separate internal-only listener/port rather than the public API router, and require authentication for the pprof passthrough endpoints in all cases given their higher sensitivity and DoS potential.

### Proof of Concept
```
# Enumerate internal plugin topology without any credentials
curl http://<node-host>:6688/discovery
# => [{"targets":["<host>:6688"],"labels":{"__metrics_path__":"/metrics"}},
#     {"targets":["<host>:6688"],"labels":{"__metrics_path__":"/plugins/median/metrics","__meta_plugin_name__":"median"}}]

# Trigger and retrieve a heap profile of the named plugin process without authentication
curl "http://<node-host>:6688/plugins/median/debug/pprof/heap?seconds=30"
```

### Citations

**File:** core/web/router.go (L86-93)
```go

	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)

	guiAssetRoutes(engine, config.Insecure().DisableRateLimiting(), app.GetLogger())
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

**File:** core/web/router.go (L443-446)
```go
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))

		// Debug routes accessible via authentication
		metricRoutes(authv2)
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

**File:** core/web/loop_registry.go (L150-187)
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
```

**File:** plugins/README.md (L37-44)
```markdown
The endpoints are

`/discovery` : HTTP Service Discovery [https://prometheus.io/docs/prometheus/latest/configuration/configuration/#http_sd_config]
Prometheus server is configured to poll this url to discover new endpoints to monitor. The node serves the response based on what plugins are running,

`/plugins/<name>/metrics`: The node acts as very thin middleware to route from Prometheus server scrape requests to individual plugin /metrics endpoint
Once a plugin is discovered via the discovery mechanism above, the Prometheus service calls the target endpoint at the scrape interval
The node acts as middleware to route the request to the /metrics endpoint of the requested plugin
```
