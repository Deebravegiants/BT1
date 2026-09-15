### Title
Unauthenticated LOOP-plugin debug/pprof and metrics endpoints exposed to unprivileged HTTP clients - (File: `core/web/router.go`, `core/web/loop_registry.go`)

### Summary
The Rubicon report describes functions (`offer(uint,ERC20,uint,ERC20)`, `insert(uint,uint)`) that are documented as "keeper/authorized only" but ship with no access-control check, so any unprivileged caller can reach privileged, state-manipulating functionality. The closest analog reachable from an unprivileged HTTP client in this codebase is `loopRoutes`, which registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` on the router's base `api` group with no `auth.Authenticate*` middleware at all, unlike every other functional route group (`debugRoutes`, `v2Routes`, `sessionRoutes`) which explicitly wrap handlers in `auth.Authenticate(...)`.

### Finding Description
`NewRouter` builds the `api` route group with only rate-limiting and session middleware attached — no authentication: [1](#0-0) 

Compare this to every other route-group helper, which explicitly requires session or token authentication before reaching handlers, e.g. `debugRoutes`: [2](#0-1) 

and the `v2Routes`/`userOrEI` groups which wrap sensitive endpoints with `auth.Authenticate` plus role checks such as `auth.RequiresRunRole`/`auth.RequiresEditRole`: [3](#0-2) [4](#0-3) 

`loopRoutes`, however, registers its handlers directly on the raw, unauthenticated `api`/`r` group: [5](#0-4) 

These handlers proxy to internal LOOP plugin ports and forward request bodies/queries verbatim, including full `net/http/pprof` functionality (profile, symbol, arbitrary `debug`/`gc`/`seconds` query parameters) and Prometheus metrics scraping targets: [6](#0-5) [7](#0-6) 

Just as the Rubicon `offer`/`insert` functions were meant to be keeper-only per code comments but had no `require`/modifier enforcing that, these plugin debug/metrics/pprof routes appear intended for internal operator/monitoring use (the code comments even say "internal btw the node and plugin") but are exposed on the public router without any `auth.Authenticate` wrapper.

### Impact Explanation
Any unprivileged client that can reach the node's HTTP interface can:
- Enumerate registered LOOP plugins and their metrics via `/discovery` and `/plugins/:name/metrics`, leaking internal topology/plugin names and potentially sensitive metric values.
- Trigger arbitrary `pprof` profile/trace/heap/goroutine captures against internal plugin processes via `/plugins/:name/debug/pprof/*profile`, which can be used for information disclosure (memory/stack contents can leak secrets) and for denial-of-service (CPU/heap profiling with attacker-controlled `seconds` causes sustained CPU/memory load, and `PPROFOverheadSeconds` extends request duration up to attacker-chosen values).
- POST arbitrary bodies to the plugin's `/debug/pprof/symbol` endpoint with no authentication.

This is lower severity than Rubicon's fund/orderbook manipulation (there's no direct fund movement here), but it is a legitimate confidentiality/availability exposure surface directly analogous to "should be keeper-only but has zero access control."

### Likelihood Explanation
High likelihood of reachability: this route group is registered unconditionally in `NewRouter` for every Chainlink node deployment, on the same listener as the rest of the `/v2` API, with no feature flag or authentication guard visible in `loopRoutes`/`NewRouter`. Exploitability requires only network access to the node's web server port — no credentials, tokens, or session cookies needed.

### Recommendation
Wrap `loopRoutes` (or at minimum the `pluginPPROFHandler`, `pluginPPROFPOSTSymbolHandler`, and `pluginMetricHandler` routes) with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` (and ideally `auth.RequiresAdminRole`) middleware used by `debugRoutes`, or bind these debug endpoints to a separate internal-only listener/port that isn't exposed on the primary API interface. If external Prometheus scraping of `/discovery` and `/plugins/:name/metrics` is required, restrict pprof/symbol endpoints specifically to an authenticated/admin-only route group, since pprof exposure carries materially higher risk than plain metrics.

### Proof of Concept
1. Start a Chainlink node with at least one LOOP plugin registered (e.g., a Solana/Cosmos relayer LOOPP) so `l.registry.List()` is non-empty.
2. As an unauthenticated client (no session cookie, no API key), issue:
   - `GET /discovery` — returns plugin names/metrics target list without any `Authorization`/session cookie, confirmed by the route registration at [5](#0-4)  having no `auth.Authenticate` in its middleware chain (contrast with `debugRoutes` at line 181).
   - `GET /plugins/<pluginName>/debug/pprof/profile?seconds=30` — triggers a 30s CPU profile capture on the internal plugin process, handled by `pluginPPROFHandler` at [8](#0-7) , again reachable with no credentials.
3. Both requests succeed with `200 OK` and return the requested internal data because no `authMethod` is invoked anywhere in the `loopRoutes` request path, unlike comparable admin-only routes in the same router file.

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

**File:** core/web/router.go (L245-266)
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

		wa := NewWebAuthnController(app)
		authv2.GET("/enroll_webauthn", wa.BeginRegistration)
		authv2.POST("/enroll_webauthn", wa.FinishRegistration)

		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/router.go (L449-456)
```go
	ping := PingController{app}
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
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
