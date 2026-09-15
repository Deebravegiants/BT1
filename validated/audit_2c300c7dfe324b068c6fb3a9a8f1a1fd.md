Audit Report

## Title
Unauthenticated LOOP Plugin pprof-Proxy Endpoints Expose Internal Debug Data - ([File: core/web/router.go])

## Summary
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` on the base `api` gin group, which enforces only rate limiting and session-cookie middleware, not authentication. `/discovery` and `/plugins/:name/metrics` are intentionally unauthenticated by design (documented in `plugins/README.md` as a Prometheus HTTP service-discovery mechanism), but the pprof-proxy handlers ride on the same unauthenticated route group with no separate access control, unlike the node's own equivalent `metricRoutes` (native `net/http/pprof`), which is deliberately gated behind `authv2`.

## Finding Description
`NewRouter` creates the `api` group with only rate limiting and session middleware (no `auth.Authenticate`) and calls `loopRoutes(app, api)` directly on it: [1](#0-0) . `loopRoutes` registers all four endpoints, including the pprof proxy handlers, on this unauthenticated group: [2](#0-1) . By contrast, the node's own pprof endpoints (`metricRoutes`) are explicitly wired only under the authenticated `authv2` group with a comment noting the intent ("Debug routes accessible via authentication"): [3](#0-2) .

`pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` proxy arbitrary `debug/pprof/*` requests (profile, heap, goroutine, trace, symbol) to the internal plugin process and return the raw response, with no authentication check inside the handler itself: [4](#0-3) .

However, `plugins/README.md` documents that `/discovery` and `/plugins/<name>/metrics` are intentionally unauthenticated — they exist specifically so that an external Prometheus server can scrape LOOP plugin metrics without direct network exposure of the plugin processes: [5](#0-4) . This is a deliberate design choice consistent with common Prometheus practice (unauthenticated `/metrics` endpoints are the norm across the ecosystem), which weakens the claim as it pertains to `/discovery` and `/plugins/:name/metrics`. SECURITY.md also explicitly places "server-side non-confidential information disclosure, such as IPs, server names" out of scope, which covers most of what `/discovery` exposes: [6](#0-5) .

The pprof-proxy routes are a different matter: there is no equivalent documentation or design rationale for leaving `debug/pprof/*` (heap, goroutine, profile, trace) unauthenticated, and the codebase's own convention (gating the analogous node-level pprof behind `authv2`) demonstrates the developers treat pprof data as sensitive and require authentication for it elsewhere.

## Impact Explanation
An unauthenticated network client reachable to the node's API port can pull heap, goroutine, CPU-profile, and trace data from any registered LOOP plugin process by guessing/enumerating a plugin name (itself derivable via the unauthenticated `/discovery` response). This is an information-disclosure issue; pprof heap/goroutine dumps can reveal internal state, stack traces, and potentially allocation-site data from LOOP plugin processes (e.g., relayer plugins), though the claim's assertion that this could directly expose "secrets/keys held in process memory" is speculative and not demonstrated with concrete evidence that any credential material is present in LOOP plugin process memory or would surface in a sampled pprof profile. The `/discovery` and `/metrics` portion of the original report is largely intentional/documented behavior and does not represent a broken security assumption.

## Likelihood Explanation
Exploitation requires only unauthenticated network access to the node's HTTP API and knowledge of a registered plugin name (obtainable via `/discovery`), so likelihood for reaching the pprof-proxy endpoints is high. However, actual sensitive-data exposure from those profiles is not concretely demonstrated in the report — no PoC shows recovered secrets, only that raw pprof output is returned, which is a lower-severity operational-information disclosure absent further proof.

## Recommendation
Gate the pprof-proxy routes (`/plugins/:name/debug/pprof/*profile`, `/plugins/:name/debug/pprof/symbol`) behind the same `auth.Authenticate`/admin-role middleware used for `metricRoutes(authv2)`, while leaving `/discovery` and `/plugins/:name/metrics` unauthenticated as intentionally designed for Prometheus scraping (optionally add a bearer-token check similar to `prometheusHandler`'s token gate for defense in depth).

## Proof of Concept
1. Start a node with a LOOP plugin registered.
2. Without any session/token, `GET /plugins/<plugin_name>/debug/pprof/heap?debug=1` and observe a `200 OK` with raw pprof heap output, confirming no authentication is enforced, unlike `/v2/debug/pprof/heap` which requires a valid session/token via `authv2`.

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

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
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

**File:** plugins/README.md (L30-51)
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

The simplest change to monitor LOOPPs is to add a service discovery to the scrape configuration
- job_name: 'chainlink_node'
  ...
+  http_sd_configs:
+      - url: "http://127.0.0.1:6688/discovery"
+        refresh_interval: 30s
```

**File:** SECURITY.md (L40-40)
```markdown
- Server-side non-confidential information disclosure, such as IPs, server names, and most stack traces.
```
