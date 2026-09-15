This confirms the claim precisely. `loopRoutes` is called directly on the base `api` group without any authentication wrapper, unlike `v2Routes` which creates a separate `authv2` sub-group with `auth.Authenticate(...)` middleware, or `debugRoutes`/`sessionRoutes` which explicitly wrap sensitive routes with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`. The `metricRoutes` function (native pprof) is only invoked inside the `authv2` block, confirming the deliberate pattern that debug/metrics endpoints should be authenticated — a pattern not applied to `loopRoutes`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

The handlers themselves (`discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, `pluginPPROFPOSTSymbolHandler`) contain no auth checks of their own, relying entirely on the router group for access control, which is absent here.

Audit Report

## Title
Unauthenticated LOOP Plugin Discovery, Metrics, and pprof Endpoints Expose Internal Debug Data - ([File: core/web/router.go])

## Summary
The `loopRoutes` function is registered directly on the unauthenticated `api` route group in `NewRouter`, exposing `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` to any network client without requiring a session or token. This contrasts with the equivalent native pprof routes (`metricRoutes`) which are deliberately wired only into the authenticated `authv2` group, and with other sensitive routes (`debugRoutes`, `sessionRoutes` DELETE) that explicitly wrap themselves with `auth.Authenticate(...)`.

## Finding Description
In `NewRouter`, the `api` group is created with only rate limiting and gin session middleware (no authentication requirement), and `loopRoutes(app, api)` is invoked directly on it. The handlers in `loop_registry.go` (`discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, `pluginPPROFPOSTSymbolHandler`) perform no independent authentication/authorization checks — they assume the router group already gated access, which it does not for these routes. This is confirmed by contrast with `v2Routes`, which splits into `unauthedv2` (only for the specific `/resume/:runID` webhook callback) and `authv2` (wrapped with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`), and where `metricRoutes(authv2)` — the equivalent native pprof endpoint — is deliberately called only inside the authenticated block with an explicit comment "Debug routes accessible via authentication." No equivalent authentication wrapper exists for `loopRoutes`.

## Impact Explanation
An unauthenticated network client can enumerate all registered LOOP plugins and internal Prometheus target metadata via `/discovery`, pull full Prometheus metrics text for any plugin via `/plugins/:name/metrics`, and pull pprof profiling data (heap dumps, goroutine stacks, CPU profiles, symbol tables) from internal LOOP plugin processes via `/plugins/:name/debug/pprof/*`. This is an information-disclosure vulnerability; heap/goroutine dumps from plugin processes could reveal sensitive internal state, and metrics/discovery data reveal internal topology and configuration, falling under the node API authentication/information-disclosure impact class.

## Likelihood Explanation
The routes are registered unconditionally on every node start whenever the web server is enabled and are reachable by any client that can reach the node's API port, requiring no credentials. The only requirement is knowledge of a plugin name, which is itself enumerable via the unauthenticated `/discovery` endpoint, making exploitation straightforward and repeatable.

## Recommendation
Move `loopRoutes(app, api)` to be registered under an authenticated group (mirroring the pattern used for `metricRoutes(authv2)`), or wrap the `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` routes with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` (and consider `auth.RequiresAdminRole` for pprof endpoints) before they reach the `LoopRegistryServer` handlers.

## Proof of Concept
1. Start a Chainlink node with at least one LOOP plugin registered.
2. Without any session cookie or API token, send `GET /discovery` and observe a `200 OK` response listing internal plugin names, hostnames, and metrics paths.
3. Send `GET /plugins/<plugin_name>/metrics` without credentials and observe `200 OK` with raw Prometheus metrics text.
4. Send `GET /plugins/<plugin_name>/debug/pprof/heap?debug=1` without credentials and observe `200 OK` with a full heap profile dump, contrasted with `GET /v2/debug/pprof/heap` which requires authentication and returns `401 Unauthorized` without a valid session/token.

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

**File:** core/web/router.go (L180-236)
```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", expvar.Handler())
}

func metricRoutes(r *gin.RouterGroup) {
	pprofGroup := r.Group("/debug/pprof")
	pprofGroup.GET("/", ginHandlerFromHTTP(pprof.Index))
	pprofGroup.GET("/cmdline", ginHandlerFromHTTP(pprof.Cmdline))
	pprofGroup.GET("/profile", ginHandlerFromHTTP(pprof.Profile))
	pprofGroup.POST("/symbol", ginHandlerFromHTTP(pprof.Symbol))
	pprofGroup.GET("/symbol", ginHandlerFromHTTP(pprof.Symbol))
	pprofGroup.GET("/trace", ginHandlerFromHTTP(pprof.Trace))
	pprofGroup.GET("/allocs", ginHandlerFromHTTP(pprof.Handler("allocs").ServeHTTP))
	pprofGroup.GET("/block", ginHandlerFromHTTP(pprof.Handler("block").ServeHTTP))
	pprofGroup.GET("/goroutine", ginHandlerFromHTTP(pprof.Handler("goroutine").ServeHTTP))
	pprofGroup.GET("/heap", ginHandlerFromHTTP(pprof.Handler("heap").ServeHTTP))
	pprofGroup.GET("/mutex", ginHandlerFromHTTP(pprof.Handler("mutex").ServeHTTP))
	pprofGroup.GET("/threadcreate", ginHandlerFromHTTP(pprof.Handler("threadcreate").ServeHTTP))
}

func ginHandlerFromHTTP(h http.HandlerFunc) gin.HandlerFunc {
	return func(c *gin.Context) {
		h.ServeHTTP(c.Writer, c.Request)
	}
}

func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
}

func healthRoutes(app chainlink.Application, r *gin.RouterGroup) {
	hc := HealthController{app}
	r.GET("/readyz", hc.Readyz)
	r.GET("/public-readyz", hc.PublicReadyz)
	r.GET("/health", hc.Health)
	r.GET("/health.txt", func(context *gin.Context) {
		context.Request.Header.Set("Accept", gin.MIMEPlain)
	}, hc.Health)
}

func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
}
```

**File:** core/web/router.go (L238-247)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
```

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```
