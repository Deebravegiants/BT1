Audit Report

## Title
Unauthenticated LOOP Plugin Debug/Metrics/PPROF Endpoints Bypass the Node's Authentication Layer - (File: core/web/router.go)

## Summary
`NewRouter` mounts `loopRoutes` directly on the bare `api` route group, which only carries CORS/rate-limiting/session-cookie middleware and no authentication check, while the functionally equivalent node pprof surface (`metricRoutes`) is deliberately nested inside `authv2`, which requires `auth.Authenticate(..., auth.AuthenticateByToken, auth.AuthenticateBySession)`. This lets any unauthenticated network client hit `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol`.

## Finding Description
`NewRouter` builds `api := engine.Group(...)` with only rate-limiting and session-cookie middleware attached, and no `auth.Authenticate` call [1](#0-0) . It then registers `debugRoutes(app, api)`, `healthRoutes(app, api)`, `sessionRoutes(app, api)`, `v2Routes(app, api)`, and `loopRoutes(app, api)` all on that same unauthenticated `api` group [2](#0-1) .

`debugRoutes` self-wraps its `/debug/vars` route in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` [3](#0-2) , and the node's own pprof handlers (`metricRoutes`) are only ever invoked from inside `authv2`, a group explicitly gated by `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, with a code comment "Debug routes accessible via authentication" [4](#0-3) [5](#0-4) .

`loopRoutes`, by contrast, registers its handlers directly with no auth wrapper at all:
```go
func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
}
``` [6](#0-5) 

I verified the handler implementations in `core/web/loop_registry.go` and confirmed none of them perform any authentication or authorization check internally either — `discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, and `pluginPPROFPOSTSymbolHandler` all go straight from `gc.Param(...)`/`registry.Get(...)` to proxying the request, with no call into `auth` package or session/token validation [7](#0-6) [8](#0-7) . `pluginPPROFHandler` forwards attacker-controlled query parameters (`debug`, `gc`, `seconds`) straight into the proxied pprof request with only a bounded timeout, meaning a remote unauthenticated caller can request expensive profiles (`profile?seconds=N`) against the plugin's internal pprof port [9](#0-8) .

## Impact Explanation
An unauthenticated remote client reaching the node's HTTP API port can:
- Enumerate all registered LOOP plugins and their internal Prometheus scrape targets via `/discovery`.
- Pull raw Prometheus `/metrics` output per plugin via `/plugins/:name/metrics`.
- Pull CPU/heap/goroutine/mutex/block profiles and full stack traces via `/plugins/:name/debug/pprof/*profile`, which can leak sensitive in-process data (addresses, internal state, potentially secrets held in memory) and enable resource-exhaustion by repeatedly triggering `profile?seconds=N` requests against the plugin process.

This is a real, concrete authentication-bypass class issue — a route group intended to sit behind the node's authentication boundary is wired to the unauthenticated `api` group in `NewRouter`. It maps to the in-scope "node API authentication bypass" impact category.

## Likelihood Explanation
No credentials, tokens, or special network position are required beyond network reachability to the node's HTTP listener (the same port that serves the authenticated `/v2` API), which is a common deployment topology. A single unauthenticated GET/POST request triggers the exposure, and it is fully repeatable. The only precondition — one or more LOOP plugins registered in `LoopRegistry` — is standard for OCR2/median and other plugin-based job types, not a special or unusual configuration.

## Recommendation
Wrap `loopRoutes` in the same authentication requirement applied to `metricRoutes`/`debugRoutes` — either mount it inside `authv2` (optionally combined with `auth.RequiresAdminRole`), or wrap its own route group with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` before registering the `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` handlers. Add a regression test to `core/web/auth/auth_test.go`'s `routesRolesMap`-style suite asserting these routes return 401/403 for unauthenticated/non-admin callers.

## Proof of Concept
Against a running node with at least one LOOP plugin registered, without any `Authorization` header or session cookie:
```
curl -s http://NODE_HOST:6688/discovery
curl -s http://NODE_HOST:6688/plugins/<plugin-name>/metrics
curl -s http://NODE_HOST:6688/plugins/<plugin-name>/debug/pprof/goroutine?debug=2
curl -s http://NODE_HOST:6688/plugins/<plugin-name>/debug/pprof/profile?seconds=30
```
On the current code, these return HTTP 200 with discovery/metrics/pprof data and no `401 Unauthorized` challenge, in contrast to the authenticated `/v2/debug/pprof/*` routes gated inside `authv2` [5](#0-4) . A Go integration test using `httptest` against `NewRouter`'s returned `*gin.Engine`, asserting `401`/`403` for these four routes without auth headers, would formally confirm the fix once `loopRoutes` is wrapped in the authentication middleware.

### Citations

**File:** core/web/router.go (L78-85)
```go
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

**File:** core/web/router.go (L245-248)
```go
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

**File:** core/web/loop_registry.go (L53-81)
```go
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

**File:** core/web/loop_registry.go (L132-166)
```go
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
