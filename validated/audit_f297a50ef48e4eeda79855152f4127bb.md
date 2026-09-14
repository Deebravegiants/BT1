### Title
Unauthenticated Access to LOOP Plugin Debug/pprof and Metrics Endpoints - (File: core/web/router.go)

### Summary
The Chainlink node's HTTP router mounts the LOOP-plugin discovery, metrics-proxy, and `pprof` forwarding routes on the base `api` group, which only carries rate-limiting and session middleware — not the `auth.Authenticate` middleware used elsewhere for sensitive debug endpoints. This lets any unauthenticated network client reach the node's `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` endpoints, which proxy live introspection data (heap dumps, goroutine stacks, CPU/trace profiles) from the plugin subprocess.

### Finding Description
`NewRouter` builds the top-level `api` group with only rate limiting and cookie-session middleware, no authentication: [1](#0-0) 

`debugRoutes`, by contrast, explicitly wraps its `/debug/vars` route in `auth.Authenticate(...)`, and the equivalent host `pprof` endpoints registered via `metricRoutes` are deliberately placed inside the authenticated `authv2` group: [2](#0-1) [3](#0-2) 

However, `loopRoutes` is called directly on the unauthenticated `api` group and registers no auth middleware of its own: [4](#0-3) [5](#0-4) 

The handlers it wires up forward requests straight to the plugin subprocess's internal HTTP server (`/metrics`, `/debug/pprof/*`, `/debug/pprof/symbol`) using the plugin's Prometheus port, with the profile name taken verbatim from the URL wildcard parameter and concatenated into the outbound request URL: [6](#0-5) [7](#0-6) 

This is the same bug class as the referenced CVE: an optional/internal debug-introspection subsystem (pprof/dumper) that is reachable by an unprivileged, unauthenticated requester because it was not placed behind the node's normal authentication boundary, unlike its sibling host-level `pprof` route which was correctly gated.

### Impact Explanation
An unauthenticated attacker with network access to the node's API port can:
- Enumerate all registered LOOP plugins and their internal target addresses via `/discovery`.
- Pull live `heap`/`goroutine`/`allocs` pprof dumps from a plugin subprocess (e.g. Median/relayer plugins), which can contain sensitive in-memory data such as key material, RPC credentials, or database connection strings that the plugin process holds.
- Trigger `profile`/`trace` collection with attacker-controlled `seconds`, which forces the plugin process to spend CPU/time producing profiling data — a low-cost resource-exhaustion vector against a chain relayer process.
This maps to unauthorized disclosure/DoS reachable by any unprivileged actor hitting the node's public API, matching the "session/token handling" and "internet-facing gateway allowlist/handler" analog classes.

### Likelihood Explanation
High: no credentials, session, or special role are required — a plain HTTP GET/POST to a known, statically-defined route (`/plugins/:name/debug/pprof/...`) on the node's standard listening port is sufficient. The route pattern is discoverable simply by reading the open-source router code or via the unauthenticated `/discovery` endpoint that enumerates plugin names.

### Recommendation
Wrap `loopRoutes` (or at minimum the `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` routes) in the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` middleware already used for `debugRoutes` and the host-level `metricRoutes`, consistent with how `authv2` gates other sensitive endpoints in `v2Routes`. If `/discovery` and `/plugins/:name/metrics` must remain reachable by an external Prometheus scraper, protect them with a separate bearer-token check (as already implemented for `prometheusHandler`) rather than leaving them fully open.

### Proof of Concept
```
# Enumerate plugins without any authentication
curl http://<node-host>:6688/discovery

# Dump heap profile of a named plugin without authentication
curl "http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/heap"

# Trigger a 60s CPU profile / trace on the plugin without authentication (resource exhaustion)
curl "http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/profile?seconds=60"
```
No session cookie, API token, or role is required for any of these requests, in contrast to the equivalent `/v2/debug/pprof/*` host route, which returns `401 Unauthorized` without a valid session as verified by `TestShell_Profile_Unauthenticated` [8](#0-7) .

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

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/loop_registry.go (L95-128)
```go
// pluginMetricHandlers routes from endpoints published in service discovery to the backing LOOP endpoint
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

**File:** core/web/loop_registry.go (L150-188)
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
}
```

**File:** core/cmd/shell_remote_test.go (L500-514)
```go
func TestShell_Profile_Unauthenticated(t *testing.T) {
	t.Parallel()

	app := startNewApplicationV2(t, nil)

	client := app.NewAuthenticatingShell(&cltest.MockCountingPrompter{T: t, EnteredStrings: []string{}})

	set := flag.NewFlagSet("test", 0)
	set.Uint("seconds", 1, "")
	set.String("output_dir", t.TempDir(), "")

	err := client.Profile(cli.NewContext(nil, set, nil))
	require.ErrorContains(t, err, "profile collection failed:")
	require.ErrorContains(t, err, "Unauthorized")
}
```
