The claim's code references are accurate and verified directly against the repository.

Audit Report

## Title
Unauthenticated Access to LOOP Plugin Debug/pprof and Metrics Endpoints - (File: core/web/router.go)

## Summary
`loopRoutes` is mounted on the base `api` gin group in `NewRouter`, which only applies rate-limiting and cookie-session middleware, not authentication. This leaves `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` reachable by any network client without credentials, unlike the equivalent host-level pprof route (`metricRoutes`) which is deliberately nested inside the authenticated `authv2` group, and `debugRoutes`, which explicitly wraps `/debug/vars` in `auth.Authenticate`.

## Finding Description
In `NewRouter`, the `api` group is created with only `rateLimiter` and `sessions.Sessions` middleware [1](#0-0) . `loopRoutes(app, api)` is called directly on this unauthenticated group and itself adds no auth middleware, registering `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` [2](#0-1) . By contrast, `debugRoutes` explicitly gates `/debug/vars` behind `auth.Authenticate(...)` [3](#0-2) , and the host-level `pprof` handlers registered via `metricRoutes` are placed inside the `authv2` group, which requires token or session authentication [4](#0-3) [5](#0-4) .

The handlers forward requests to the plugin subprocess's internal HTTP server using the plugin's Prometheus port: `pluginMetricHandler` proxies `/metrics` [6](#0-5) , and `pluginPPROFHandler`/`pluginPPROFPOSTSymbolHandler` proxy `/debug/pprof/*` and `/debug/pprof/symbol`, with the profile name taken verbatim from the URL wildcard `gc.Param("profile")` and concatenated into the outbound request URL [7](#0-6) . None of these handlers perform any authentication or authorization check before proxying the request.

## Impact Explanation
An unauthenticated network client reaching the node's API port can enumerate registered LOOP plugins via `/discovery`, and pull live pprof dumps (heap, goroutine, allocs) or trigger CPU profile/trace collection from plugin subprocesses via `/plugins/:name/debug/pprof/*`. This is an in-scope information-disclosure/resource-exhaustion issue analogous to a debug-introspection endpoint being placed outside the node's normal authentication boundary, in contrast to the sibling host-level `pprof` route (`metricRoutes`) which is correctly gated behind `authv2`.

## Likelihood Explanation
High. No credentials, session cookie, or role are required — the routes are statically defined and reachable via a plain HTTP GET/POST to a well-known path pattern on the node's standard listening port. Plugin names are discoverable via the equally unauthenticated `/discovery` endpoint.

## Recommendation
Wrap `loopRoutes` (or at minimum the `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` routes) in the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` middleware used by `debugRoutes`, consistent with how `metricRoutes` is nested inside `authv2`. If `/discovery` and `/plugins/:name/metrics` must remain reachable by an external Prometheus scraper, protect them with a separate bearer-token check rather than leaving them fully open.

## Proof of Concept
```
# Enumerate plugins without any authentication
curl http://<node-host>:6688/discovery

# Dump heap profile of a named plugin without authentication
curl "http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/heap"

# Trigger a 60s CPU profile / trace on the plugin without authentication (resource exhaustion)
curl "http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/profile?seconds=60"
```
This can be confirmed by writing a gin-router integration test that starts `NewRouter` and issues an unauthenticated request to `/plugins/:name/debug/pprof/heap` (with a registered test plugin in `plugins.LoopRegistry`), expecting `200 OK` instead of `401 Unauthorized`, contrasted against `TestShell_Profile_Unauthenticated` for the host-level `/v2/debug/pprof` route which does return `401` [8](#0-7) .

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
