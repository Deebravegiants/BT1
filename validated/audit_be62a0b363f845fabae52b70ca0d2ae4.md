Audit Report

## Title
Unauthenticated Node API Endpoints Proxy Attacker-Controlled Paths to Internal LOOP Plugin pprof/Metrics Servers - (File: core/web/router.go, core/web/loop_registry.go)

## Summary
The `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` routes are registered via `loopRoutes` directly on the base `api` gin group, which only applies rate limiting and session middleware — no `auth.Authenticate` wrapper is applied, unlike every comparable debug/admin surface in the router (`debugRoutes`, `metricRoutes` mounted under `authv2`, and all `v2Routes` admin endpoints). This contradicts the code's own documented assumption that these are "internal" endpoints, and additionally the `profile` route parameter is concatenated unsanitized into the outbound backend URL in `pluginPPROFHandler`.

## Finding Description
`loopRoutes` is invoked directly on the `api` group (`core/web/router.go` L78-91), which carries only rate limiting and cookie-session middleware — no authentication requirement: [1](#0-0) 

Compare this to every other sensitive surface in the same file: `/debug/vars` requires `auth.Authenticate(...)` [2](#0-1) , and the standard Go `net/http/pprof` handlers registered via `metricRoutes` are only mounted inside the authenticated `authv2` group [3](#0-2) . All of `v2Routes`' admin functionality is likewise gated by `auth.Authenticate`/`auth.RequiresAdminRole` etc.

`loopRoutes` registers the plugin proxy endpoints with no such guard: [4](#0-3) 

The handler code itself documents the assumption that this is meant to be internal-only traffic ("this endpoint is internal btw the node and plugin"), but that assumption is never enforced at the routing layer: [5](#0-4) 

Compounding this, `pluginPPROFHandler` builds the outbound URL by directly splicing the raw `gc.Param("profile")` wildcard value into a `fmt.Sprintf` format string with no `filepath.Clean`/prefix validation, unlike the traversal guards used elsewhere in the codebase (`core/services/workflows/syncer/v2/fetcher.go` L222-231, `core/web/middleware.go` L196-208). Since `/plugins/:name/debug/pprof/*profile` is a gin catch-all route, an unauthenticated caller fully controls everything after `/debug/pprof/`, including `../` sequences, before it is forwarded via `doRequest`: [6](#0-5) 

## Impact Explanation
Any unauthenticated client that can reach the node's HTTP listener can invoke Go's `net/http/pprof`-equivalent debug surface (goroutine dumps, heap dumps, CPU profiling) and `/metrics` of internal LOOP plugin processes, entirely bypassing the authentication model applied to every functionally equivalent debug endpoint in the same router (`/debug/vars`, `/v2/debug/pprof/*`). This is an authentication-bypass class finding (CWE-306) for a debug/profiling feature the code's own comments state should be internal-only, mapping to "node API authentication ... bypass." Profile/heap/goroutine dumps of the plugin process can leak sensitive in-memory data, and the CPU-profile endpoint's attacker-controlled `seconds` parameter allows tying up plugin resources for a bounded but attacker-chosen duration (mild DoS). The unsanitized `profile` concatenation is a secondary aggravating factor whose full traversal impact depends on what else, if anything, listens on the plugin's `PrometheusPort` — this part could not be fully confirmed.

## Likelihood Explanation
High for the access-control gap: it requires zero credentials — only network reachability to the node's HTTP API (the same reachability required for `/health`, `/discovery`, etc.), and is trivially and repeatably triggerable via a single unauthenticated GET request. No operator, admin, or host access is needed.

## Recommendation
Wrap `loopRoutes`' plugin-proxy endpoints (`/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*`) in the same `auth.Authenticate(...)` middleware used for `/debug/vars` and the authenticated pprof routes in `v2Routes`, leaving only `/discovery` public if external Prometheus scraping genuinely requires it (and consider a scrape-token check similar to `prometheusHandler`'s bearer-token gate). Additionally, sanitize `gc.Param("profile")` with `path.Clean`/prefix-allowlist validation before splicing it into the outbound `pluginURL` in `pluginPPROFHandler`.

## Proof of Concept
1. Start a Chainlink node with at least one LOOP plugin registered (e.g., a Solana/EVM relayer running as a LOOP).
2. Without any session cookie or API token, issue: `curl http://<node-host>:<port>/plugins/<plugin-name>/debug/pprof/goroutine?debug=2` — this succeeds and returns the plugin's goroutine dump.
3. Compare with: `curl http://<node-host>:<port>/v2/debug/pprof/goroutine` — this returns `401 Unauthorized` (or a login redirect), demonstrating the inconsistency between the two functionally equivalent debug surfaces.
4. To probe the concatenation issue, request `curl "http://<node-host>:<port>/plugins/<plugin-name>/debug/pprof/../../metrics"` and inspect node logs (`Forwarding plugin pprof request ... url=...`) to confirm the literal unsanitized URL sent to the internal LOOP host/port.

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

**File:** core/web/router.go (L445-446)
```go
		// Debug routes accessible via authentication
		metricRoutes(authv2)
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

**File:** core/web/loop_registry.go (L190-205)
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
```
