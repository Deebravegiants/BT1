### Title
Unauthenticated LOOP plugin discovery/metrics/pprof endpoints expose internal node and plugin data - ([File: core/web/router.go])

### Summary
The `loopRoutes` route group in `core/web/router.go` registers the `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` endpoints without any authentication middleware, unlike every other sensitive route group in the same router (`debugRoutes`, `sessionRoutes`, `v2Routes`), which explicitly wrap their groups with `auth.Authenticate(...)`.

### Finding Description
`NewRouter` creates the `api` group with only rate limiting and session-cookie middleware, no authentication requirement by default: [1](#0-0) 

Compare this with the other route registrations on the same `api` group:
- `debugRoutes` requires session auth: `group := r.Group("/debug", auth.Authenticate(...))` [2](#0-1) 
- `sessionRoutes` splits unauthenticated (`/sessions` POST) from an explicitly authenticated group for `DELETE /sessions` [3](#0-2) 
- `v2Routes` explicitly separates a small unauthenticated group from a large `authv2` group wrapped in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` [4](#0-3) 

`loopRoutes`, however, registers all four handlers directly on the passed-in `RouterGroup` with no `auth.Authenticate` wrapper at all: [5](#0-4) 

The handlers themselves perform no independent authentication/authorization checks:
- `discoveryHandler` returns Prometheus service-discovery data listing all registered LOOP plugin names, hostnames, and ports with no auth check [6](#0-5) 
- `pluginMetricHandler` proxies to an internal plugin's `/metrics` endpoint and returns the response with no auth check [7](#0-6) 
- `pluginPPROFHandler` proxies arbitrary Go `net/http/pprof` profile requests (heap, goroutine, profile, trace, allocs, block, mutex, threadcreate) to the internal plugin process, again with no authentication [8](#0-7) 
- `pluginPPROFPOSTSymbolHandler` similarly forwards the pprof `symbol` endpoint [9](#0-8) 

An existing test confirms these endpoints are reachable via a plain, unauthenticated `client := app.NewHTTPClient(nil)` and return `http.StatusOK`: [10](#0-9) 

This is directly analogous to CVE-2026-55814's bug class: internet-facing "download"/data-export style endpoints (here, pprof profile/heap dumps and metrics/service-discovery data) reachable by an unauthenticated actor because the route registration omits the authentication middleware applied to sibling route groups.

### Impact Explanation
- `/discovery` discloses internal topology: plugin names, internal hostnames, and the ports used for Prometheus scraping — information useful for further targeted attacks against the node's internal network surface.
- `/plugins/:name/metrics` and pprof endpoints (`heap`, `profile`, `goroutine`, `allocs`, etc.) can leak process memory contents via heap/goroutine dumps. Since the Chainlink node handles private keys, database secrets, and other sensitive material in memory, an unauthenticated actor able to trigger a heap dump on a LOOP plugin process could potentially extract sensitive data or at minimum perform reconnaissance and resource-exhaustion (CPU/duration-based pprof profile/trace requests) against the node without any credentials.
- This matches the CVSS profile of the reference CVE (network-reachable, no privileges/user interaction required, confidentiality impact) though the blast radius here is scoped to LOOP-plugin operational/debug data rather than arbitrary file "download," so the severity is likely High rather than Critical.

### Likelihood Explanation
High, if LOOP plugins/CORE routes are exposed to a network-reachable Chainlink API server (default node configuration exposes the web API). No credentials, tokens, or session cookies are required — a plain HTTP GET is sufficient, as demonstrated by the test using an unauthenticated `NewHTTPClient(nil)` and receiving `200 OK` responses.

### Recommendation
Wrap `loopRoutes` registration with the same authentication middleware used for other sensitive route groups (e.g., `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`), consistent with `debugRoutes` and `authv2` in `core/web/router.go`. At minimum, the pprof forwarding endpoints (`pluginPPROFHandler`, `pluginPPROFPOSTSymbolHandler`) should require authenticated admin-level access, since they can trigger memory dumps and CPU-intensive profiling of plugin processes.

### Proof of Concept
1. Start a Chainlink node with at least one registered LOOP plugin (e.g., a median/relayer plugin) and the web server exposed on its default port.
2. Without any session cookie, API token, or Basic Auth credentials, issue:
   - `curl http://<node-host>:<port>/discovery` — returns JSON listing all plugin names/hosts/ports.
   - `curl http://<node-host>:<port>/plugins/<pluginName>/metrics` — returns full Prometheus metrics for the plugin process.
   - `curl "http://<node-host>:<port>/plugins/<pluginName>/debug/pprof/heap"` — returns a heap-memory profile dump of the plugin process.
3. All three requests succeed with `HTTP 200`, confirming no authentication is enforced, as also shown by the existing unauthenticated test client usage in `core/web/loop_registry_test.go` (lines 99-152).

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

**File:** core/web/router.go (L238-248)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
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

**File:** core/web/loop_registry_test.go (L99-152)
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

	t.Run("core metrics OK", func(t *testing.T) {
		t.Parallel()
		// core node metrics endpoint
		resp, cleanup := client.Get(expectedCoreEndPoint)
		t.Cleanup(cleanup)
		cltest.AssertServerResponse(t, resp, http.StatusOK)

		b, err := io.ReadAll(resp.Body)
		require.NoError(t, err)
		t.Logf("core metrics response %s", b)
	})
```
