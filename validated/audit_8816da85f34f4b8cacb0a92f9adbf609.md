### Title
Unauthenticated `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` endpoints disclose internal service/plugin details and debug data - (File: core/web/router.go)

### Summary
The LOOP plugin routes registered by `loopRoutes` are mounted on the shared `api` gin route group with no authentication middleware applied, unlike nearly every other route group in the router (`debugRoutes`, `v2Routes`, `sessionRoutes`). This exposes plugin discovery metadata, prometheus metrics, and full Go `pprof` debug/profiling data to any unauthenticated client that can reach the node's API port — directly analogous to CVE-2024-9802, where a public conformance-validation endpoint leaked internal service details (available endpoints, swagger, version) to unauthenticated users.

### Finding Description
In `NewRouter`, the top-level `api` group only applies rate limiting and session middleware; authentication is applied selectively per sub-route-group: [1](#0-0) 

`debugRoutes` explicitly wraps `/debug/vars` with `auth.Authenticate`: [2](#0-1) 

But `loopRoutes` applies no authentication at all to its handlers: [3](#0-2) 

The `discoveryHandler` returns the hostname, exposed prometheus port, and the names of all registered LOOP plugins to any caller: [4](#0-3) 

`pluginPPROFHandler` forwards unauthenticated requests to the internal `/debug/pprof/*` endpoint of any named plugin, concatenating the caller-supplied `profile` path parameter directly into the internal request URL and returning the raw response (goroutine dumps, heap profiles, CPU profiles, stack traces) to the caller: [5](#0-4) 

This is a stronger disclosure surface than the CVE's conformance-check leak: it doesn't just reveal version/endpoint metadata, it forwards full runtime debug/profiling data (which can include memory contents, goroutine stacks, and internal function names/paths) to any unauthenticated network client, and acts as an unauthenticated proxy into an internal-only service (`l.loopHostName`).

### Impact Explanation
An unauthenticated attacker with network access to the Chainlink node's API port can:
- Enumerate all running LOOP plugins and internal topology via `/discovery`.
- Pull raw prometheus metrics for the node and each plugin via `/plugins/:name/metrics`.
- Pull full `pprof` debug output (`heap`, `goroutine`, `profile`, `trace`, etc.) via `/plugins/:name/debug/pprof/*`, which can leak internal state, memory layout, and aid further attacks (this is generally considered sensitive/internal-only tooling, akin to leaking a debug console).
This matches the CVSS 5.3 (Confidentiality: Low, no integrity/availability impact) profile of the reference CVE — information disclosure to an unauthenticated party, not a direct compromise.

### Likelihood Explanation
Likelihood is high wherever the node's HTTP API is reachable by unauthenticated network clients (e.g., misconfigured deployments exposing the API port), since no credentials, tokens, or session are required to reach `/discovery` or the `/plugins/*` routes — this is a straightforward, unauthenticated GET request.

### Recommendation
Require authentication (or restrict to trusted network sources / internal-only listener) for `loopRoutes`, consistent with how `debugRoutes` wraps `/debug/vars` with `auth.Authenticate`. At minimum, gate `/plugins/:name/debug/pprof/*` and `/plugins/:name/metrics` behind the same authentication used for other administrative/debug endpoints, and validate/allowlist the `profile` path segment before forwarding to the internal plugin URL.

### Proof of Concept
```
# No credentials required
curl http://<chainlink-node>:6688/discovery
curl http://<chainlink-node>:6688/plugins/<plugin-name>/metrics
curl http://<chainlink-node>:6688/plugins/<plugin-name>/debug/pprof/goroutine?debug=2
```
Each request succeeds without any `Authorization` header, session cookie, or API token, returning internal plugin names, prometheus targets, and raw pprof debug output.

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

**File:** core/web/loop_registry.go (L52-81)
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

	b, err := l.jsonMarshalFn(groups)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		_, err = w.Write([]byte(err.Error()))
		if err != nil {
			l.logger.Error(err)
		}
		return
	}
	_, err = w.Write(b)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		l.logger.Error(err)
	}
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
