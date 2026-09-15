Confirmed: `HTTPPort` (default `6688`) is described as "the port used for the Chainlink Node API, CLI, and GUI" [1](#0-0) , and this is the same `engine`/`api` group that `loopRoutes` is registered on in `NewRouter` [2](#0-1) .

### Title
Unauthenticated exposure of internal plugin metrics and pprof forwarding via `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` endpoints - (File: `core/web/router.go`, `core/web/loop_registry.go`)

### Summary
The Chainlink node's main web server (`NewRouter`) mounts several routes with no authentication middleware, mirroring the CVE-2022-34321 Pulsar Proxy pattern where a "stats" style endpoint was reachable without credentials and additionally allowed remote control of debugging/logging behavior.

### Finding Description
`NewRouter` builds an `api` route group scoped only by rate limiting and session storage (no auth requirement), then calls `loopRoutes(app, api)` directly on that group: [3](#0-2) 

`loopRoutes` registers four handlers with zero `auth.Authenticate(...)` wrapping, unlike `debugRoutes` (which wraps `/debug/vars` in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`) and `metricRoutes` (only mounted inside the already-authenticated `authv2` group): [4](#0-3) [5](#0-4) [6](#0-5) 

The handlers themselves live in `core/web/loop_registry.go`:
- `discoveryHandler` returns the list of all registered LOOP plugin names plus their Prometheus scrape paths [7](#0-6) .
- `pluginMetricHandler` forwards any request for a registered plugin name to that plugin's internal `/metrics` endpoint and returns the response body unauthenticated [8](#0-7) .
- `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` forward arbitrary `debug/pprof/*` requests (including attacker-controlled `seconds`, `debug`, `gc` query params) to the plugin's internal pprof server and proxy back the raw response, again with no authentication check [9](#0-8) .

This is functionally analogous to the Pulsar `/proxy-stats` issue: an unauthenticated internet-facing endpoint that (a) discloses internal topology/naming information about running plugins (`discoveryHandler`), and (b) allows an unauthenticated caller to trigger expensive, attacker-tunable profiling operations (`pluginPPROFHandler` with a `seconds` parameter) against internal plugin processes.

### Impact Explanation
An unauthenticated remote client reaching the node's HTTP API port can:
- Enumerate all registered LOOP plugin names via `/discovery`, disclosing internal architecture/topology information not otherwise exposed.
- Pull full Prometheus metrics for any named plugin via `/plugins/:name/metrics` without credentials.
- Trigger CPU/heap/goroutine profiling on internal plugin processes via `/plugins/:name/debug/pprof/*` with a controllable duration (`seconds` query param, capped only by `PPROFOverheadSeconds`), which can be repeated to generate sustained CPU overhead on internal plugin servers — a denial-of-service vector directly analogous to the Pulsar logging-level DoS.

### Likelihood Explanation
These routes are mounted on the primary node API port (default `6688`) which serves the API, CLI, and Operator UI [1](#0-0) . Any operator who exposes this port without an additional reverse-proxy/authentication layer in front of it (a common misconfiguration, exactly the scenario the original Pulsar advisory calls out) will expose these endpoints to any unauthenticated caller who can reach the port.

### Recommendation
Wrap `loopRoutes` registration with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` (or a dedicated internal-only auth method / IP allowlist) used for `debugRoutes` and the authenticated `v2Routes` group, so `/discovery`, `/plugins/:name/metrics`, and the `/plugins/:name/debug/pprof/*` family require an authenticated session/token, consistent with how `metricRoutes` (core node pprof) is already gated.

### Proof of Concept
1. Start a node with at least one LOOP plugin registered (e.g. following `plugins/README.md`'s Prometheus discovery setup) [10](#0-9) .
2. Without any session cookie or API token, send `GET /discovery` to the node's HTTP port — confirm it returns `200 OK` with the list of registered plugins, as exercised (without auth headers) by the test harness itself: [11](#0-10) .
3. Send `GET /plugins/<name>/debug/pprof/profile?seconds=30` repeatedly without credentials; observe the plugin's internal pprof server performing repeated CPU profiling on behalf of the unauthenticated caller [12](#0-11) .

### Citations

**File:** docs/CONFIG.md (L538-542)
```markdown
### HTTPPort
```toml
HTTPPort = 6688 # Default
```
HTTPPort is the port used for the Chainlink Node API, [CLI](/docs/configuration-variables/#cli-client), and GUI.
```

**File:** core/web/router.go (L77-92)
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

**File:** core/web/router.go (L445-447)
```go
		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
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

**File:** core/web/loop_registry.go (L130-215)
```go
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
	b, err := io.ReadAll(res.Body)
	if err != nil {
		msg := fmt.Sprintf("error reading plugin %q pprof", html.EscapeString(pluginName))
		l.logger.Errorw(msg, "err", err)
		gc.Data(http.StatusInternalServerError, "text/plain", fmt.Appendf(nil, "%s: %s", msg, err))
		return
	}

	gc.Data(http.StatusOK, "text/plain", b)
}
```

**File:** plugins/README.md (L30-52)
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

**File:** core/web/loop_registry_test.go (L99-122)
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
```
