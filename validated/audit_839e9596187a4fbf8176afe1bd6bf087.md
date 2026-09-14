### Title
Missing authorization on `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` HTTP endpoints exposes live LOOP plugin runtime data - (File: core/web/router.go, core/web/loop_registry.go)

### Summary
The chainlink node's web API router registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the unauthenticated `api` route group, unlike every other sensitive "debug"-class endpoint in the same router file which is explicitly wrapped in `auth.Authenticate(...)`.

### Finding Description
`NewRouter` builds a route group `api` with only rate-limiting and session middleware, no authentication [1](#0-0) . Individual route-registration functions are then responsible for adding their own auth requirement. `debugRoutes` explicitly wraps `/debug/vars` in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` [2](#0-1) , and `sessionRoutes` similarly creates an authenticated sub-group for `DELETE /sessions` [3](#0-2) . The node's own `pprof` endpoints (`metricRoutes`) are registered under the `authv2` group, which requires token or session authentication [4](#0-3) [5](#0-4) .

`loopRoutes`, however, is called directly on the bare `api` group with no authentication wrapper at all: `debugRoutes(app, api)`, `healthRoutes(app, api)`, `sessionRoutes(app, api)`, `v2Routes(app, api)`, `loopRoutes(app, api)` [6](#0-5) . Its registrations are:
```
r.GET("/discovery", ...)
r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
``` [7](#0-6) 

`pluginPPROFHandler` forwards the request to the LOOP plugin's own `/debug/pprof/<profile>` HTTP endpoint (heap, goroutine, profile, trace, cmdline, allocs, block, mutex, threadcreate, etc.) and streams the raw response back to the caller with zero access check [8](#0-7) . `pluginPPROFPOSTSymbolHandler` similarly forwards to `/debug/pprof/symbol` [9](#0-8) . `pluginMetricHandler` forwards to the plugin's `/metrics` Prometheus endpoint and streams it back unauthenticated [10](#0-9) .

This is the exact bug-class match to the vttablet `/debug/vrlog` advisory: a debugging/diagnostics HTTP handler that omits the access-control check applied to every sibling "debug"-family endpoint in the same file, allowing an unauthenticated, unprivileged client to pull live internal diagnostic/runtime data from the node's exposed HTTP listener.

### Impact Explanation
`pprof` `heap`, `goroutine`, `profile`, `trace`, and `cmdline` dumps of a LOOP plugin process can contain in-memory secrets (private key material, decrypted job configuration, OCR keys, API tokens, database connection strings) that were resident in the plugin process at capture time. Because these handlers require no authentication, any network client that can reach the node's HTTP API port (the same port that serves the GraphQL API, session login, etc., commonly exposed for legitimate remote operator access) can retrieve this data or repeatedly trigger CPU/heap profiling (`?seconds=N`) to induce resource exhaustion — a read-only information-disclosure and minor availability issue matching the CWE-862 (Missing Authorization) class of the reference advisory. This is strictly less severe than raw SQL/PII leakage in the Vitess case, but constitutes the same category: unauthorized disclosure of live internal diagnostic data due to an inconsistently-applied auth check.

### Likelihood Explanation
High likelihood of reachability: the affected routes are registered on the same top-level engine and port as all other node API routes, requiring no special network position — any client that can send an HTTP GET/POST to the node's web server (as confirmed by the existing test `TestLoopRegistry`, which calls `/discovery` and `/plugins/mockLoopImpl/metrics` via the standard `app.NewHTTPClient(nil)` without any auth headers and receives `200 OK`) [11](#0-10) . The pprof forwarding path (`pluginPPROFHandler`/`pluginPPROFPOSTSymbolHandler`) is registered identically (no auth wrapper) and is reachable the same way, though it was not directly exercised by an existing test in the index.

### Recommendation
Wrap `loopRoutes` registration in the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` middleware used by `authv2` (or at minimum apply `auth.RequiresAdminRole` given the sensitivity of pprof/heap dumps), mirroring how `debugRoutes`, `sessionRoutes`, and the node's own `metricRoutes` are protected. Concretely, change:
```go
loopRoutes(app, api)
```
to register on an authenticated sub-group, e.g.:
```go
authLoop := api.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession))
loopRoutes(app, authLoop)
```
and update any tests (e.g. `TestLoopRegistry`) to authenticate before calling `/discovery`, `/plugins/:name/metrics`, and the pprof forwarding endpoints.

### Proof of Concept
1. Start a chainlink node with a LOOP plugin registered (as in `TestLoopRegistry`).
2. Without any session cookie or API token, send:
   - `GET /discovery` → returns `200 OK` with full plugin service-discovery JSON, confirmed working unauthenticated in `TestLoopRegistry` [12](#0-11) .
   - `GET /plugins/<name>/metrics` → returns `200 OK` with the plugin's raw Prometheus metrics [13](#0-12) .
   - `GET /plugins/<name>/debug/pprof/heap` → forwarded via `pluginPPROFHandler` to the plugin's `/debug/pprof/heap` and streamed back with no auth check [8](#0-7) .
3. Compare against `GET /v2/debug/pprof/heap` (the node's own pprof, registered under `authv2`) which returns `401 Unauthorized` without credentials, demonstrating the inconsistency [4](#0-3) [5](#0-4) .

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

**File:** core/web/router.go (L207-218)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
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

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/router.go (L445-446)
```go
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

**File:** core/web/loop_registry_test.go (L99-140)
```go
	client := app.NewHTTPClient(nil)

	t.Run("discovery endpoint", func(t *testing.T) {
		t.Parallel()
		// under the covers this is routing thru the app into loop registry
		resp, cleanup := client.Get("/discovery")
		t.Cleanup(cleanup)
		cltest.AssertServerResponse(t, resp, http.StatusOK)

		b, err := io.ReadAll(resp.Body)
		require.NoError(t, err)
		t.Logf("discovery response %s", b)
		var got []*targetgroup.Group
		require.NoError(t, json.Unmarshal(b, &got))

		gotLabels := make([]model.LabelSet, 0, len(got))
		for _, ls := range got {
			gotLabels = append(gotLabels, ls.Labels)
		}
		assert.Len(t, gotLabels, len(expectedLabels))
		for i := range expectedLabels {
			assert.Equal(t, expectedLabels[i], gotLabels[i])
		}
	})

	t.Run("plugin metrics OK", func(t *testing.T) {
		t.Parallel()
		// plugin name `mockLoopImpl` matches key in PluginConfigs
		resp, cleanup := client.Get(expectedLooppEndPoint)
		t.Cleanup(cleanup)
		cltest.AssertServerResponse(t, resp, http.StatusOK)

		b, err := io.ReadAll(resp.Body)
		require.NoError(t, err)
		t.Logf("plugin metrics response %s", b)

		var (
			exceptedCount  = 1
			expectedMetric = fmt.Sprintf("%s %d", testMetricName, exceptedCount)
		)
		require.Contains(t, string(b), expectedMetric)
	})
```
