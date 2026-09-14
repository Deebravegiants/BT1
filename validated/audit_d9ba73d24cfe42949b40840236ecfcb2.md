### Title
Unauthenticated Access to LOOP Plugin Metrics and pprof Debug Endpoints - (File: core/web/router.go)

### Summary
The chainlink node's core `/metrics` endpoint can optionally be protected by a `Prometheus.AuthToken` bearer-token check [1](#0-0) , but the parallel LOOP-plugin discovery, metrics-proxy, and pprof-proxy endpoints registered via `loopRoutes` are mounted on the API router group with **no authentication middleware at all**, exposing plugin Prometheus metrics and full Go `pprof` profiling data to any unauthenticated client.

### Finding Description
`NewRouter` builds an `api` route group that only applies rate limiting and session-cookie middleware, and then calls `loopRoutes(app, api)` alongside other route groups [2](#0-1) . Unlike `v2Routes`, which explicitly wraps sensitive routes with `auth.Authenticate(...)` before registering handlers [3](#0-2) , `loopRoutes` registers its handlers directly on the unauthenticated `r` group: [4](#0-3) 

This exposes three endpoints without any credential check:
- `GET /discovery` — returns Prometheus HTTP service-discovery target groups for the node and every registered LOOP plugin [5](#0-4) .
- `GET /plugins/:name/metrics` — proxies to the internal plugin's `/metrics` endpoint and returns the raw Prometheus text output to the caller [6](#0-5) .
- `GET /plugins/:name/debug/pprof/*profile` and `POST /plugins/:name/debug/pprof/symbol` — proxy to the plugin's `net/http/pprof` handlers, including profile/goroutine/heap dumps, with a caller-controlled `seconds` parameter [7](#0-6) .

This is distinct from, and bypasses, the deliberate `Prometheus.AuthToken` gate that protects the core `/metrics` route [8](#0-7)  — an unprivileged remote client can reach plugin metrics and profiling data even when the operator has configured `Prometheus.AuthToken` specifically to prevent pre-auth metrics disclosure, because that token is only checked by `prometheusHandler` for the ginprom-registered `/metrics` route, not for the LOOP-registry routes.

### Impact Explanation
An unauthenticated network client can:
- Enumerate all running LOOP plugins and their internal proxy targets via `/discovery`.
- Pull detailed Prometheus metrics for each plugin via `/plugins/:name/metrics`, which can reveal internal operational/business data (equivalent to the CVE-2023-6001 bug class of pre-auth Prometheus metrics disclosure).
- Trigger CPU/heap/goroutine profiling (`pprof`) on plugin processes via `/plugins/:name/debug/pprof/profile?seconds=N`, which can leak sensitive stack traces/memory layout and also serve as an unauthenticated CPU-consumption vector since `seconds` is attacker-controlled [9](#0-8) .

This is a concrete confidentiality (and secondary availability) issue reachable pre-authentication from any client that can reach the node's web server port.

### Likelihood Explanation
High — no special conditions are required beyond LOOP plugins being enabled (a supported deployment mode, referenced in `plugins/README.md`). The routes are registered unconditionally whenever the router is built and are reachable on the same port serving the operator UI/API.

### Recommendation
Wrap the `loopRoutes` group with the same authentication middleware used for other sensitive routes (e.g., `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`), or gate it behind the existing `Prometheus.AuthToken` check used by `prometheusHandler`, so plugin metrics/pprof data receive equivalent protection to the core `/metrics` endpoint.

### Proof of Concept
Against a running node with a LOOP plugin registered (e.g. named `median`):
```
curl http://<node-host>:6688/discovery
curl http://<node-host>:6688/plugins/median/metrics
curl "http://<node-host>:6688/plugins/median/debug/pprof/profile?seconds=30"
```
No `Authorization` header or session cookie is required for any of these requests, as confirmed by the route registration in `loopRoutes` [4](#0-3)  and the corresponding test that issues plain `client.Get(...)` calls without authentication setup [10](#0-9) .

### Citations

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

**File:** core/web/loop_registry.go (L130-166)
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
```

**File:** core/services/chainlink/config_prometheus.go (L1-16)
```go
package chainlink

import (
	"github.com/smartcontractkit/chainlink/v2/core/config/toml"
)

type prometheusConfig struct {
	s toml.PrometheusSecrets
}

func (p *prometheusConfig) AuthToken() string {
	if p.s.AuthToken == nil {
		return ""
	}
	return string(*p.s.AuthToken)
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
