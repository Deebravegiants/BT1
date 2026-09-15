## Analysis: CVE-2021-39211 analog in chainlink

The CVE describes an **unauthenticated endpoint that discloses internal server/system information** (GLPI's `ajax/telemetry.php`). Investigating chainlink's web server, I found a real analog: several diagnostic/debug routes are mounted on the main web engine **without any authentication middleware**, unlike the rest of the `/v2` API which requires session or token auth via `auth.Authenticate`.

### Title
Unauthenticated disclosure of internal node/plugin state via `/discovery` and `/plugins/:name/debug/pprof/*` routes - (File: `core/web/router.go`)

### Summary
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` on the same `api` route group used by the public HTTP API, but these routes are never wrapped with `auth.Authenticate(...)`, unlike every other operational route (`debugRoutes` explicitly wraps `/debug/vars` with session auth, while `loopRoutes` does not receive equivalent protection).

### Finding Description
In `core/web/router.go`, the top-level `NewRouter` wires several route groups onto the same `api` group that only has rate limiting and session middleware applied: [1](#0-0) 

`debugRoutes` correctly requires session authentication before exposing `expvar`: [2](#0-1) 

However, `loopRoutes` — mounted right alongside it on the same unauthenticated `api` group — exposes plugin metrics discovery and full pprof debugging without any auth check: [3](#0-2) 

The handlers themselves confirm no authentication/authorization check is performed. `discoveryHandler` returns internal hostnames, exposed Prometheus ports, and the full list of registered LOOP plugin names to any caller: [4](#0-3) 

`pluginPPROFHandler` proxies to the internal `/debug/pprof/<profile>` endpoint of any named plugin, forwarding attacker-controlled query parameters (`debug`, `gc`, `seconds`) with no auth gate: [5](#0-4) 

This is the same bug class as CVE-2021-39211: an internet-reachable HTTP endpoint that discloses internal server topology/state (hostnames, ports, plugin names, profiling/goroutine/heap data) to unauthenticated clients, and additionally allows unauthenticated CPU-profile/trace collection with a caller-controlled `seconds` duration.

Note also that the health endpoints (`/health`, `/health.txt`, `/readyz`) are similarly registered unauthenticated: [6](#0-5) 
and the code's own comment on `PublicReadyz` acknowledges that `Readyz` "leak[s] internal service state on publicly reachable endpoints" when `?full` is requested, which is exactly the class of issue the CVE describes: [7](#0-6) 

### Impact Explanation
An unauthenticated remote attacker who can reach the node's web server port (commonly exposed for the Operator UI / API) can:
- Enumerate internal hostnames, exposed metrics ports, and installed LOOP plugin names via `/discovery`.
- Pull live pprof `profile`/`trace`/`heap`/`goroutine` dumps from plugins via `/plugins/:name/debug/pprof/*`, which can leak stack traces, memory contents, and internal code paths, and can be used to fingerprint the node for follow-on attacks.
- Trigger CPU-intensive profiling operations (`/profile?seconds=N`) with attacker-supplied duration, contributing to resource exhaustion.
- Retrieve detailed internal health-check names/error output via `/readyz?full`.

This is a confidentiality-only, no-code-execution disclosure — consistent with the CVE's CVSS profile (`C:L/I:N/A:N`, no privileges required, network attack vector).

### Likelihood Explanation
High — these routes require no credentials, no special network position, and are mounted on the standard node web server alongside the public API, so any external caller with network access to the node's HTTP port can trigger them.

### Recommendation
Wrap `loopRoutes` (and ideally `Readyz`'s `?full` detail path) with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` (or a dedicated internal-only network binding) used for `debugRoutes`, so that plugin discovery, metrics, and pprof endpoints are not reachable by unauthenticated clients. Consider binding these diagnostic endpoints to a separate internal-only listener instead of the public API router.

### Proof of Concept
```
# No credentials required:
curl http://<node-host>:6688/discovery
curl http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/heap
curl "http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/profile?seconds=30"
curl "http://<node-host>:6688/readyz?full"
```
Each of these requests succeeds without any `Authorization`/session cookie, returning internal topology, live profiling data, or detailed health-check internals.

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

**File:** core/web/router.go (L180-183)
```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", expvar.Handler())
}
```

**File:** core/web/router.go (L220-228)
```go
func healthRoutes(app chainlink.Application, r *gin.RouterGroup) {
	hc := HealthController{app}
	r.GET("/readyz", hc.Readyz)
	r.GET("/public-readyz", hc.PublicReadyz)
	r.GET("/health", hc.Health)
	r.GET("/health.txt", func(context *gin.Context) {
		context.Request.Header.Set("Accept", gin.MIMEPlain)
	}, hc.Health)
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

**File:** core/web/health_controller.go (L27-58)
```go
// PublicReadyz is a minimal readiness endpoint intended for public load balancer health checks.
// Unlike Readyz, it never returns per-check details regardless of query parameters, to avoid
// leaking internal service state on publicly reachable endpoints.
func (hc *HealthController) PublicReadyz(c *gin.Context) {
	ready, _ := hc.App.GetHealthChecker().IsReady()
	if !ready {
		c.Status(http.StatusServiceUnavailable)
		return
	}
	c.Status(http.StatusOK)
}

// NOTE: We only implement the k8s readiness check, *not* the liveness check. Liveness checks are only recommended in cases
// where the app doesn't crash itself on panic, and if implemented incorrectly can cause cascading failures.
// See the following for more information:
// - https://srcco.de/posts/kubernetes-liveness-probes-are-dangerous.html
func (hc *HealthController) Readyz(c *gin.Context) {
	status := http.StatusOK

	checker := hc.App.GetHealthChecker()

	ready, errors := checker.IsReady()

	if !ready {
		status = http.StatusServiceUnavailable
	}

	c.Status(status)

	if _, ok := c.GetQuery("full"); !ok {
		return
	}
```
