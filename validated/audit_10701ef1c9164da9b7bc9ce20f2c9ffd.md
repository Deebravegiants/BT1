The claim is fully verified against the code. All key elements check out:

- `loopRoutes` is registered directly on the top-level `api` group with no auth middleware: `debugRoutes(app, api); healthRoutes(app, api); sessionRoutes(app, api); v2Routes(app, api); loopRoutes(app, api)` [1](#0-0) , while the `api` group itself only applies rate limiting and session cookie middleware, no authentication [2](#0-1) .
- In contrast, `metricRoutes` (the core `/v2/debug/pprof/*` equivalent) is deliberately nested inside the `authv2` group under a comment "Debug routes accessible via authentication" [3](#0-2) , and `debugRoutes` similarly wraps `/debug/vars` in `auth.Authenticate(...)` [4](#0-3) .
- `loopRoutes` itself contains zero authentication middleware calls: `r.GET("/discovery", ...); r.GET("/plugins/:name/metrics", ...); r.GET("/plugins/:name/debug/pprof/*profile", ...); r.POST("/plugins/:name/debug/pprof/symbol", ...)` [5](#0-4) .
- The pprof handler proxies caller-controlled query params and the full `profile` path segment to the plugin's internal pprof server with no auth check [6](#0-5) , and the POST symbol handler does the same for the request body [7](#0-6) .
- The existing test suite confirms these routes are reachable via a plain, unauthenticated HTTP client (`app.NewHTTPClient(nil)`) and return `200 OK` for `/discovery` and `/plugins/mockLoopImpl/metrics` without any session/token setup [8](#0-7) .
- `plugins/README.md` documents the intended purpose as "very thin middleware" for Prometheus scraping only, not general pprof exposure, so the addition of full pprof proxy routes without auth is inconsistent with the stated design intent [9](#0-8) .

This is a genuine, unpatched authorization gap: an unauthenticated network caller can enumerate plugin names via `/discovery` and pull full pprof profiles (goroutine, heap, cmdline, CPU via `seconds=`) per plugin, none of which requires the session/token or role checks that gate every comparable debug surface in this router. This is not a misconfiguration, host-level, or operator-only issue — it's directly triggerable by an unprivileged HTTP client against the node's exposed web server port, matching the information-disclosure/missing-authorization impact class in scope.

Audit Report

## Title
Unauthenticated exposure of internal pprof profiling/debug data via LOOP plugin routes - (File: core/web/router.go, core/web/loop_registry.go)

## Summary
The LOOP plugin routes (`/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, `/plugins/:name/debug/pprof/symbol`) are registered via `loopRoutes(app, api)` directly on the top-level `api` router group, which applies only rate limiting and session-cookie middleware and no authentication check, unlike the functionally equivalent `/v2/debug/pprof/*` endpoints which are gated behind `auth.Authenticate` in the `authv2` group. This allows any unauthenticated network caller reaching the node's web server to enumerate LOOP plugin names and pull full pprof profiling data (goroutines, heap, cmdline, CPU profiles) for each plugin.

## Finding Description
`loopRoutes` is mounted on `api` with no auth middleware wrapper: `r.GET("/discovery", ...); r.GET("/plugins/:name/metrics", ...); r.GET("/plugins/:name/debug/pprof/*profile", ...); r.POST("/plugins/:name/debug/pprof/symbol", ...)` (`core/web/router.go:230-236`), called from `NewRouter` alongside other `api`-group routes (`core/web/router.go:87-91`), where `api` only has rate limiting and session middleware (`core/web/router.go:77-85`). By contrast, `debugRoutes` wraps `/debug/vars` in `auth.Authenticate(...)` (`core/web/router.go:180-183`), and `metricRoutes` (the core pprof equivalent) is explicitly nested in the authenticated `authv2` group under the comment "Debug routes accessible via authentication" (`core/web/router.go:444-446`). The handlers `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` forward caller-supplied query parameters and path segments directly to the internal plugin pprof server with no authorization gate (`core/web/loop_registry.go:150-188`). The existing test suite exercises these routes with a plain unauthenticated HTTP client and observes 200 OK responses (`core/web/loop_registry_test.go:99-129`), confirming no auth is required in practice. This contradicts the stated design in `plugins/README.md:42-44`, which describes these routes as thin metrics-scraping middleware, not a general-purpose unauthenticated pprof proxy.

## Impact Explanation
This is an information-disclosure vulnerability (CWE-862/863 class, missing authorization) allowing an unauthenticated attacker to obtain goroutine stack traces, heap/memory profiles, running command-line arguments (`cmdline`), and CPU profiles (via `seconds=`) for any LOOP plugin process, as well as internal topology information (plugin names, internal hostnames/ports) via `/discovery`. This is a legitimate confidentiality/information-disclosure impact within the node API authentication/authorization impact category.

## Likelihood Explanation
High for any node whose web server HTTP port is reachable by an untrusted network, since the exploit requires no credentials, tokens, session cookies, or any prior privileged access — it is directly triggerable by a normal unauthenticated HTTP client, consistent with the "unprivileged actor" requirement.

## Recommendation
Wrap `loopRoutes` (or at minimum the pprof/debug sub-routes) in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, matching the protection applied to `metricRoutes` and `debugRoutes`, or otherwise restrict these routes to trusted/internal network access only.

## Proof of Concept
1. Start a Chainlink node with a LOOP plugin registered and the web server port reachable.
2. Without any Authorization header or session cookie, send `GET /discovery` — observe `200 OK` with plugin names, as demonstrated in the existing `TestLoopRegistry` test (`core/web/loop_registry_test.go:101-122`) using an unauthenticated `app.NewHTTPClient(nil)`.
3. For a discovered plugin name `X`, send `GET /plugins/X/debug/pprof/goroutine?debug=2` and `GET /plugins/X/debug/pprof/profile?seconds=30` without credentials — both succeed and return pprof data via `pluginPPROFHandler` (`core/web/loop_registry.go:150-166`).
4. Compare against `GET /v2/debug/pprof/goroutine`, which requires authentication per `metricRoutes` in the `authv2` group (`core/web/router.go:444-446`) and returns `401 Unauthorized` without a valid session/token.

### Citations

**File:** core/web/router.go (L77-85)
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
```

**File:** core/web/router.go (L87-91)
```go
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

**File:** core/web/router.go (L444-446)
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

**File:** core/web/loop_registry_test.go (L99-129)
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
```

**File:** plugins/README.md (L42-44)
```markdown
`/plugins/<name>/metrics`: The node acts as very thin middleware to route from Prometheus server scrape requests to individual plugin /metrics endpoint
Once a plugin is discovered via the discovery mechanism above, the Prometheus service calls the target endpoint at the scrape interval
The node acts as middleware to route the request to the /metrics endpoint of the requested plugin
```
