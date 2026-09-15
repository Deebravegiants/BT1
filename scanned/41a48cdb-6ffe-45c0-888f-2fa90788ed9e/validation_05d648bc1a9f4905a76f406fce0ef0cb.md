## Analysis

The reported CVE-2018-14602 concerns GitLab's Prometheus `/metrics` endpoint disclosing private project pathnames to unauthenticated users. The closest structural analog in this chainlink codebase is the **LOOP plugin discovery/metrics/pprof gateway**, which is mounted without any authentication middleware, unlike every other sensitive route group in the router.

### Title
Unauthenticated disclosure and pprof access via LOOP plugin discovery/metrics gateway - (File: `core/web/router.go`)

### Summary
`loopRoutes` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the top-level `api` group with no authentication middleware, while every comparable route group (`v2Routes`, `debugRoutes`, `sessionRoutes`) explicitly wraps sensitive paths in `auth.Authenticate(...)`.

### Finding Description
In `NewRouter`, the `api` group only applies rate limiting and session cookie middleware before dispatching to route groups: [1](#0-0) 

Compare this to `debugRoutes`, which explicitly authenticates `/debug/vars`: [2](#0-1) 

and `v2Routes`, which splits an `unauthedv2` group (only for the intentionally public `resume/:runID` endpoint) from an `authv2` group requiring token/session auth for everything else: [3](#0-2) 

However, `loopRoutes` registers all of its endpoints with zero auth wrapper: [4](#0-3) 

The `discoveryHandler` returns a JSON list of internal plugin/service names and their scrape paths to any caller: [5](#0-4) 

`pluginMetricHandler` proxies to internal LOOP plugin's `/metrics` port based on unauthenticated caller-supplied `name`: [6](#0-5) 

More severely, `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` proxy full Go `net/http/pprof` requests (profile, heap, trace, goroutine dumps, symbol resolution) to the internal plugin process without any authentication check: [7](#0-6) 

### Impact Explanation
An unauthenticated remote caller can enumerate registered LOOP plugin names via `/discovery`, scrape internal plugin metrics via `/plugins/:name/metrics`, and pull full pprof profiling data (heap, goroutine stacks, CPU profiles) via `/plugins/:name/debug/pprof/*`. This is a stronger analog to the GitLab CVE's "private pathname disclosure" — beyond leaking internal service/plugin names and metrics, it also exposes runtime memory/goroutine state that can leak secrets, internal addresses, or aid further attacks, all without any credentials.

### Likelihood Explanation
Any client with network access to the node's HTTP port can hit these endpoints directly; no token, session, or role is required, and the routes are always mounted whenever the router is built (`prometheus` param only gates the separate `/metrics` core endpoint, not this plugin gateway).

### Recommendation
Wrap `loopRoutes` registration in an authenticated group (mirroring `debugRoutes`/`authv2`), e.g. require `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` for `/discovery`, `/plugins/:name/metrics`, and especially the `/plugins/:name/debug/pprof/*` and symbol endpoints, or gate them behind the same `Prometheus.AuthToken` mechanism used for `/metrics` in `prometheusHandler`.

### Proof of Concept
1. Start a chainlink node with LOOP plugins enabled (no `Prometheus.AuthToken` needed since this path bypasses that check entirely).
2. Without any session cookie or API token, issue `GET /discovery` — receive JSON listing all registered plugin names and metrics paths (as shown in `TestLoopRegistry`, `core/web/loop_registry_test.go:104-121`).
3. Issue `GET /plugins/<name>/debug/pprof/heap?debug=1` — receive full heap dump of the internal plugin process, unauthenticated. [8](#0-7)

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
