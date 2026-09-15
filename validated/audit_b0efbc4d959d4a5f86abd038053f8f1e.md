Audit Report

## Title
Loop plugin discovery/metrics/pprof routes mounted without authentication middleware, exposing runtime profiling and internal plugin topology to unauthenticated network clients - ([File: core/web/router.go])

## Summary
`loopRoutes` is registered directly on the base `api` router group in `NewRouter`, which only carries request-size limiting, tracing, CORS, security headers, rate limiting, and cookie-session middleware — none of which perform authentication. Unlike sibling route groups (`debugRoutes`, `authv2`) that explicitly wrap themselves with `auth.Authenticate(...)`, `loopRoutes` has no such wrapper, so any network client that can reach the node's HTTP API can call `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` without credentials.

## Finding Description
`NewRouter` builds the `api` group with only rate limiting and session middleware attached: [1](#0-0) . `debugRoutes` explicitly gates its own `/debug` subgroup with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` [2](#0-1) , and `authv2` similarly wraps its group with `auth.Authenticate(...)` before registering user/token/job/admin routes [3](#0-2) . By contrast, `loopRoutes(app, api)` registers `GET /discovery`, `GET /plugins/:name/metrics`, `GET /plugins/:name/debug/pprof/*profile`, and `POST /plugins/:name/debug/pprof/symbol` directly on the unauthenticated `api` group, with no per-route or per-group auth middleware applied anywhere in the function [4](#0-3) .

These handlers proxy live requests to the LOOP plugin's internal Prometheus/pprof HTTP endpoint and stream the raw response back to the caller, including full `net/http/pprof` profiling data (heap, goroutine, cmdline, profile, trace, symbol) and Prometheus metrics text: [5](#0-4) [6](#0-5) . The `discoveryHandler` also leaks internal plugin topology (hostnames, ports, plugin names) with no auth check [7](#0-6) .

I confirmed via code inspection that no authentication middleware is applied anywhere in the `loopRoutes` call chain, and there is no separate, equivalent auth gate elsewhere in `router.go` that would cover these three route patterns. This is a genuine, code-level omission, not a misconfiguration or environment-dependent issue — the routes are unauthenticated on every default deployment where LOOP plugins are registered.

## Impact Explanation
Unauthenticated `net/http/pprof` access (`heap`, `goroutine`, `profile`, `trace`, `cmdline`, `symbol`) forwarded through `pluginPPROFHandler` lets any network client capture heap/goroutine dumps and trigger CPU profiling of a running LOOP plugin process on demand, which is both an information-disclosure vector (in-memory secrets, internal addresses) and a remote resource-exhaustion vector (`profile`/`trace` with attacker-controlled `seconds`). `/discovery` and `/plugins/:name/metrics` disclose internal plugin network topology and metrics without authorization. This is a concrete, in-scope "missing authentication on node API" finding (CWE-306/862 class), consistent with information disclosure and node-availability impact categories.

## Likelihood Explanation
Any client capable of reaching the Chainlink node's HTTP API port — the same precondition required to reach any other unauthenticated public route on the node — can issue these requests with zero credentials, since the entire `loopRoutes` group inherits no auth middleware. Exploitability is gated only on the operator having LOOP plugins registered (a real, commonly-used deployment mode for CCIP/LOOP-based OCR jobs), not on any special privilege or network position beyond normal API reachability.

## Recommendation
Wrap the `loopRoutes(app, api)` call (or the routes it registers) with the same `auth.Authenticate(app.AuthenticationProvider(), ...)` middleware used by `debugRoutes`/`authv2`, e.g. register these routes on an authenticated subgroup instead of the bare `api` group in `core/web/router.go`. If external Prometheus scraping without session/token auth is a hard requirement for `/discovery`/`/plugins/:name/metrics`, consider a separate, network-isolated metrics listener rather than exposing it on the primary authenticated API surface, and in any case gate the pprof proxy routes (`/plugins/:name/debug/pprof/*`) behind authentication since they have no legitimate need to be reachable by unauthenticated external scrapers.

## Proof of Concept
Against a running Chainlink node with at least one LOOP plugin registered:
```
curl -i http://<node-host>:<port>/discovery
curl -i http://<node-host>:<port>/plugins/<plugin-name>/metrics
curl -i http://<node-host>:<port>/plugins/<plugin-name>/debug/pprof/heap
curl -i http://<node-host>:<port>/plugins/<plugin-name>/debug/pprof/profile?seconds=10
```
None of these require an `Authorization` header or session cookie, since `loopRoutes` (`core/web/router.go:230-236`) is mounted on the unauthenticated `api` group (`core/web/router.go:77-91`) with no analog to the `auth.Authenticate(...)` wrapper used by `debugRoutes` (`core/web/router.go:180-183`) and `authv2` (`core/web/router.go:245-248`). A Go integration test can assert this by constructing the router via `NewRouter` with a registered mock LOOP plugin and issuing an `httptest` request to `/plugins/<name>/debug/pprof/heap` without setting any session cookie or bearer token, expecting `200 OK` instead of `401 Unauthorized`.

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

**File:** core/web/router.go (L245-248)
```go
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
