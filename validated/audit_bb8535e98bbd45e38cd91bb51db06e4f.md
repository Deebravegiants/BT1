Based on the code review, the claim is accurate and well-supported. The test file `core/web/loop_registry_test.go` confirms these endpoints are intentionally designed to be reachable without authentication (the test client makes plain `GET` requests with no auth headers and expects `200 OK`), and this matches the actual routing code — `loopRoutes(app, api)` is called at [1](#0-0)  on the same unauthenticated `api` group used for `debugRoutes`/`healthRoutes`, while `v2Routes` explicitly separates an authenticated `authv2` sub-group at [2](#0-1)  and gates the node's own pprof/metrics routes behind it at [3](#0-2) . The LOOP registry handlers themselves — `discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, and `pluginPPROFPOSTSymbolHandler` — perform no authentication checks internally, confirmed at [4](#0-3) [5](#0-4) [6](#0-5) .

Audit Report

## Title
Unauthenticated LOOP registry discovery, metrics-proxy, and pprof-proxy endpoints bypass Chainlink node API authentication - (File: core/web/router.go)

## Summary
The LOOP plugin registry routes (`/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*`, `/plugins/:name/debug/pprof/symbol`) are registered via `loopRoutes(app, api)` directly on the unauthenticated `api` route group in `NewRouter`, while all other sensitive routes (`/v2/**`, node's own `/debug/pprof`) are explicitly wrapped in an authenticated sub-group. This allows any unauthenticated client with network access to the node's API port to enumerate internal plugin topology, pull raw plugin metrics, and trigger expensive/information-disclosing pprof profiling operations against LOOP plugin processes.

## Finding Description
`NewRouter` creates an `api` group with only rate-limiting and session-cookie middleware, no authentication, at `core/web/router.go:77-85`. `loopRoutes(app, api)` is registered on this group at `core/web/router.go:91`, alongside `debugRoutes`/`healthRoutes`/`sessionRoutes`/`v2Routes`. Critically, `v2Routes` (`core/web/router.go:238-248`) creates a distinct `authv2` sub-group wrapped in `auth.Authenticate(...)`, and the node's own pprof endpoints (`metricRoutes`) are deliberately placed inside that authenticated group at `core/web/router.go:444-447`. `loopRoutes` (`core/web/router.go:230-236`) receives no such wrapping. The handler implementations in `core/web/loop_registry.go` (`discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, `pluginPPROFPOSTSymbolHandler`) perform no authentication or authorization checks of their own — they only validate that a plugin name exists in the registry before proxying the request to the internal plugin's Prometheus/pprof port. The existing `core/web/loop_registry_test.go` test explicitly demonstrates this: it issues plain unauthenticated `client.Get("/discovery")` and `client.Get("/plugins/mockLoopImpl/metrics")` calls and asserts `http.StatusOK`, confirming these endpoints are reachable without any credentials by design/oversight, in contrast to how `/v2/**` and node pprof routes require session/token auth.

## Impact Explanation
An unauthenticated network-adjacent client can: (1) enumerate internal LOOP plugin hostnames/ports and names via `/discovery`, aiding reconnaissance; (2) read raw Prometheus metrics from each registered plugin via `/plugins/:name/metrics`, which can leak operational/internal state; (3) repeatedly trigger CPU/heap/goroutine/trace pprof captures against plugin processes via `/plugins/:name/debug/pprof/*`, causing resource exhaustion or leaking runtime memory/stack data. This maps to the in-scope "node API authentication bypass" impact category — an authentication boundary that protects equivalent functionality elsewhere in the same router (`metricRoutes`/`v2Routes`) is absent for the LOOP registry routes.

## Likelihood Explanation
High. The routes are unconditionally mounted every time `NewRouter` is constructed (`loopRoutes(app, api)` at line 91), with no build-tag or dev-only guard. Any client that can reach the node's normal HTTP API port (default 6688) can hit these endpoints with no credentials, and the operation is trivially repeatable (e.g., for repeated pprof-triggered DoS).

## Recommendation
Move `loopRoutes` registration under an authenticated route group (mirroring `authv2 := r.Group("/v2", auth.Authenticate(...))`), or explicitly wrap `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` handlers with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` (and consider `auth.RequiresAdminRole` for the pprof endpoints), consistent with how the node's own pprof/metrics routes are gated via `metricRoutes(authv2)`.

## Proof of Concept
1. Start a Chainlink node with default WebServer config and at least one LOOP plugin registered (see `core/web/loop_registry_test.go` `TestLoopRegistry` for a reproducible setup pattern using `app.GetLoopRegistry().Register(...)`).
2. Without any `X-API-KEY`/`X-API-SECRET` headers or session cookie, issue:
   - `GET http://<node-host>:6688/discovery`
   - `GET http://<node-host>:6688/plugins/<plugin-name>/metrics`
   - `GET http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/heap`
3. Observe HTTP 200 responses with discovery/metrics/pprof data, exactly as the existing test `TestLoopRegistry` in `core/web/loop_registry_test.go` demonstrates using an unauthenticated `app.NewHTTPClient(nil)` client.

### Citations

**File:** core/web/router.go (L87-91)
```go
	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)
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
