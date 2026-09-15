Audit Report

## Title
Missing authentication on LOOP plugin pprof debug endpoints - (File: core/web/router.go)

## Summary
`loopRoutes` in `core/web/router.go` registers `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` directly on the unauthenticated `api` router group, unlike `debugRoutes` and `authv2` which explicitly wrap handlers in `auth.Authenticate(...)`. However, `/discovery` and `/plugins/:name/metrics` are intentionally-public-by-design Prometheus scrape endpoints (documented and covered by an unauthenticated integration test), while the `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` routes have no such documented justification and expose Go `pprof` heap/goroutine/profile/trace data of internal plugin processes to any unauthenticated caller.

## Finding Description
`loopRoutes` registers all four routes on the bare `api` group with no auth middleware: [1](#0-0) . This differs from `debugRoutes`, which wraps `/debug/vars` in `auth.Authenticate(...)`: [2](#0-1) , and from `v2Routes`/`authv2`, which requires token/session auth plus role checks: [3](#0-2) .

Critically, `/discovery` and `/plugins/:name/metrics` are documented as intentionally unauthenticated middleware for external Prometheus scraping: [4](#0-3) , and the project's own integration test explicitly asserts these two endpoints return `200 OK` without any authentication, confirming this is tested, intended behavior rather than an oversight: [5](#0-4) . Treating these two routes as a vulnerability is not supported.

The pprof routes, however, are not part of that documented Prometheus-scraping design and proxy sensitive Go runtime debug data (heap dumps, goroutine stacks, CPU/allocation profiles, symbol resolution) of the internal LOOP plugin process to any caller who can guess or discover a plugin name via `/discovery`: [6](#0-5) . There is no equivalent unauthenticated-by-design justification or test coverage for these routes analogous to the metrics/discovery case.

## Impact Explanation
Unauthenticated retrieval of `pprof` heap/goroutine dumps from the internal LOOP plugin process could expose process memory contents (potentially including key material or other sensitive in-memory state handled by the plugin), which would map to an in-scope "key/secret exfiltration" impact class. The `profile`/`trace` endpoints also accept an attacker-controlled `seconds` parameter, which could be used to tie up plugin CPU resources, but per `SECURITY.md`, "impacts that only require DDoS" are explicitly out of scope, so the availability angle alone does not qualify. [7](#0-6) 

## Likelihood Explanation
Any client that can reach the node's HTTP API can call `/discovery` (itself intentionally public) to enumerate plugin names, then hit `/plugins/<name>/debug/pprof/<profile>` with no credentials, making the pprof-specific gap trivially reachable given the intentionally-open discovery endpoint. The claim's characterization of `/discovery` and `/metrics` as vulnerable, however, is incorrect — they are deliberately unauthenticated by design, verified by both project documentation and an unauthenticated integration test, so a bounty triager would reject the discovery/metrics portion of the claim while the pprof-specific gap is narrower and its confidentiality impact (vs. mere DoS) less concretely demonstrated in the report (no PoC shows actual secret extraction from a heap dump — only a generic assertion that it "returns a full heap dump").

## Recommendation
Leave `/discovery` and `/plugins/:name/metrics` unauthenticated as designed for Prometheus scraping (or restrict via network/allowlist if desired), but wrap the `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` routes in the same `auth.Authenticate(...)` middleware used by `debugRoutes`, consistent with how the equivalent core-node `/debug/pprof` routes should be protected.

## Proof of Concept
No PoC was provided demonstrating actual sensitive data (e.g., key material) recovered from a plugin heap dump — the report only asserts that `GET /plugins/<plugin-name>/debug/pprof/heap` "returns a full heap dump", which is consistent with the code but does not concretely demonstrate confidential-data exfiltration or fund-movement impact as required for a high-severity classification.

### Citations

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

**File:** core/web/router.go (L245-257)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	{
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)
```

**File:** plugins/README.md (L30-51)
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

**File:** SECURITY.md (L44-44)
```markdown
- Impacts that only require DDoS.
```
