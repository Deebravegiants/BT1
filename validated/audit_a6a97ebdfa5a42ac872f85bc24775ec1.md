The code confirms the claim exactly as described: `loopRoutes` in `core/web/router.go` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` on the top-level `api` group with no authentication wrapper, while `debugRoutes` and `v2Routes`/`authv2` explicitly require `auth.Authenticate(...)`.

Audit Report

## Title
Unauthenticated disclosure and pprof access via LOOP plugin discovery/metrics gateway - (File: `core/web/router.go`)

## Summary
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the top-level `api` group with no authentication middleware, unlike every other sensitive route group (`debugRoutes`, `v2Routes`/`authv2`) which explicitly wrap sensitive paths in `auth.Authenticate(...)`. This allows any network-reachable, unauthenticated client to enumerate internal LOOP plugin names, scrape their internal metrics, and pull full pprof runtime/memory dumps from internal plugin processes.

## Finding Description
In `NewRouter`, the `api` group applies only rate limiting and session cookie middleware before dispatching to route groups [1](#0-0) . `debugRoutes` explicitly requires session authentication for `/debug/vars` [2](#0-1) , and `v2Routes` splits an intentionally public `unauthedv2` group (only for `resume/:runID`) from an `authv2` group requiring token/session auth for all other endpoints [3](#0-2) . In contrast, `loopRoutes` registers all four of its endpoints directly with zero auth wrapper [4](#0-3) .

`discoveryHandler` returns a JSON list of internal plugin/service names and scrape paths to any caller with no auth check [5](#0-4) . `pluginMetricHandler` proxies to the internal LOOP plugin's `/metrics` port based on caller-supplied `name`, again with no auth check [6](#0-5) . Most severely, `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` proxy full `net/http/pprof` requests (heap, goroutine, trace, symbol) to the internal plugin process, unauthenticated [7](#0-6) . This is confirmed working end-to-end by the existing test, which hits `/discovery` through the real router without any authentication and gets a `200 OK` [8](#0-7) .

## Impact Explanation
An unauthenticated remote caller with network access to the node's HTTP port can enumerate registered LOOP plugin names, scrape internal plugin metrics, and pull full pprof profiling data (heap, goroutine stacks, CPU profiles) from the internal plugin process without any credentials. This exposes internal service topology and can leak runtime memory/goroutine state (potentially secrets or internal addresses), aiding further attacks. This is a legitimate information-disclosure / missing-authentication finding on a Chainlink node HTTP API route group, distinct from the analogous compare (`debugRoutes`, `authv2`) that all require authentication for comparable sensitivity.

## Likelihood Explanation
No credential, token, or session is required — any client with network access to the node's configured web server port can trigger this directly and repeatably, as demonstrated by the existing unauthenticated test hitting `/discovery` successfully [8](#0-7) . The routes are unconditionally mounted whenever `NewRouter` is built [9](#0-8) ; the separate `Prometheus.AuthToken` gate on the core `/metrics` endpoint (via `prometheusHandler`) does not apply to this plugin gateway [10](#0-9) .

## Recommendation
Wrap `loopRoutes` registration in an authenticated group mirroring `debugRoutes`/`authv2`, e.g., require `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` for `/discovery`, `/plugins/:name/metrics`, and especially the `/plugins/:name/debug/pprof/*` and symbol endpoints, or gate them behind the same `Prometheus.AuthToken` bearer-token mechanism used for the core `/metrics` endpoint.

## Proof of Concept
1. Start a chainlink node with a LOOP plugin registered in `LoopRegistry` and the web server enabled (no `Prometheus.AuthToken` is checked on this path).
2. Without any session cookie or API token, issue `GET /discovery` and observe a `200 OK` JSON response listing all registered plugin names and metrics paths, as demonstrated in `TestLoopRegistry` (`core/web/loop_registry_test.go:101-122`).
3. Issue `GET /plugins/<name>/metrics` and `GET /plugins/<name>/debug/pprof/heap?debug=1` unauthenticated and observe the proxied internal plugin metrics/heap dump returned via `pluginMetricHandler`/`pluginPPROFHandler` (`core/web/loop_registry.go:96-118`, `150-166`).

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

**File:** core/web/router.go (L676-700)
```go
// use is adapted from ginprom.prometheusHandler to add support for custom http.Handler
func prometheusHandler(token string, h http.Handler) gin.HandlerFunc {
	return func(c *gin.Context) {
		if token == "" {
			h.ServeHTTP(c.Writer, c.Request)
			return
		}

		header := c.Request.Header.Get("Authorization")

		if header == "" {
			c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
			return
		}

		bearer := "Bearer " + token

		if header != bearer {
			c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
			return
		}

		h.ServeHTTP(c.Writer, c.Request)
	}
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

**File:** core/web/loop_registry.go (L96-118)
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

**File:** core/web/loop_registry_test.go (L101-122)
```go
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
```
