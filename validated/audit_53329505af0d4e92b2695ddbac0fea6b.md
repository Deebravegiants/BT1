Audit Report

## Title
Unauthenticated exposure of internal plugin metrics and pprof debug endpoints via LOOP registry routes - (File: core/web/router.go)

## Summary
The `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` routes are registered on the top-level `api` gin route group in `NewRouter`, which applies only rate-limiting and session middleware and no authentication check, allowing any unauthenticated network caller to retrieve internal LOOP plugin metrics and full pprof profiling data.

## Finding Description
`NewRouter` builds the `api` group with `rateLimiter` and `sessions.Sessions` only, then calls `loopRoutes(app, api)` directly on it: [1](#0-0) . `loopRoutes` registers the discovery, metrics, and pprof-forwarding handlers with no additional authorization: [2](#0-1) . This is inconsistent with the equivalent node-local pprof endpoints (`metricRoutes`), which are deliberately nested inside the authenticated `authv2` group with the comment "Debug routes accessible via authentication": [3](#0-2) , and with `/debug/vars`, which is wrapped in session auth via `debugRoutes`: [4](#0-3) .

The handlers `pluginMetricHandler`, `pluginPPROFHandler`, and `pluginPPROFPOSTSymbolHandler` forward caller-supplied `debug`, `gc`, `seconds` query parameters and the `profile` path parameter straight through to the internal plugin's `/debug/pprof/*` and `/metrics` endpoints, with no auth check inside these functions either: [5](#0-4) . The existing integration test confirms these routes are reachable via a plain, unauthenticated `client.Get` call with no session/token setup: [6](#0-5) .

## Impact Explanation
An unauthenticated network attacker able to reach the node's HTTP API port can enumerate registered LOOP plugins via `/discovery` and pull pprof heap/goroutine/CPU profiles and metrics for each. Heap and goroutine dumps can expose sensitive in-process data (including private key material per the node's own documentation on `InsecurePPROFHeap`), and profiling data discloses internal code structure — a reconnaissance/data-exfiltration capability that maps to the "key/secret exfiltration" and "node API authentication bypass" impact classes.

## Likelihood Explanation
High for any deployment where the web server port is reachable by unauthenticated clients: no credentials, session, or token are required, only network reachability — the routes are registered on the same unauthenticated `api` group as public endpoints, contrasting directly with the deliberately authenticated `metricRoutes`.

## Recommendation
Move `loopRoutes` registration to the authenticated route group (matching `metricRoutes` under `authv2`), or explicitly wrap it with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` before exposing `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*`.

## Proof of Concept
1. Start a Chainlink node with at least one LOOP plugin registered (as in `TestLoopRegistry`).
2. Without any session cookie or API token, send `GET /discovery` to enumerate plugin names and ports — confirmed reachable unauthenticated per the existing test's `client.Get("/discovery")` call with no prior authentication setup.
3. Send `GET /plugins/<name>/debug/pprof/heap?debug=1` without authentication; `pluginPPROFHandler` forwards this to the plugin's raw pprof heap endpoint and returns the result directly to the caller.

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

**File:** core/web/router.go (L443-446)
```go
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))

		// Debug routes accessible via authentication
		metricRoutes(authv2)
```

**File:** core/web/loop_registry.go (L95-188)
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

const PPROFOverheadSeconds = 30

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
