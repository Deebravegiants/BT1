## Finding: Chainlink node exposes pprof and plugin-metrics proxy endpoints without authentication

### Title
Unauthenticated exposure of pprof profiling and plugin metrics proxy endpoints via `loopRoutes` - (File: `core/web/router.go`)

### Summary
Chainlink's web router mounts LOOP (plugin) discovery, metrics-proxy, and pprof-proxy handlers on the same top-level API group used by unauthenticated endpoints, without wrapping them in the `auth.Authenticate` middleware that protects other debug/session routes. This is directly analogous to the Pomerium GHSA-q98f-2x4p-prjr issue, where `/debug` and `/metrics` handlers were reachable by untrusted traffic due to missing auth on the Authenticate service.

### Finding Description
In `NewRouter`, the top-level `api` group only applies rate-limiting and session-cookie middleware — it does not require authentication by default: [1](#0-0) 

Compare this to how other sensitive routes are explicitly protected. `debugRoutes` wraps `/debug/vars` in a dedicated authenticated sub-group: [2](#0-1) 

and `sessionRoutes` splits its group into an unauthenticated group (for login) and a separately authenticated group for session destruction: [3](#0-2) 

However, `loopRoutes` — which registers a service-discovery endpoint, a plugin-metrics proxy, and a plugin-pprof proxy — is registered directly on the unauthenticated `api` group with no auth middleware at all: [4](#0-3) [5](#0-4) 

The handlers themselves proxy requests to internal LOOP plugin processes' `/metrics` and `/debug/pprof/*` endpoints and stream the response bodies back to the caller: [6](#0-5) [7](#0-6) 

For contrast, the node's own top-level Prometheus `/metrics` endpoint is properly protected by an optional bearer-token check via `prometheusHandler`: [8](#0-7) 
No equivalent protection exists for the `loopRoutes` handlers, which are separate from that top-level `/metrics` route and from the standard-library pprof handlers registered by `metricRoutes` (which is defined but is not called from `NewRouter`, and so unlike `loopRoutes` does not appear to be reachable in production wiring). [9](#0-8) 

### Impact Explanation
An unauthenticated client that can reach the Chainlink node's web API can:
- Call `GET /discovery` to enumerate all registered LOOP plugins and their metrics paths/ports.
- Call `GET /plugins/:name/metrics` to fetch a given plugin's raw Prometheus metrics (potentially leaking internal environment/runtime information), matching the CWE-200 information disclosure class in the advisory.
- Call `GET /plugins/:name/debug/pprof/*profile` (including `profile`, `trace`, `heap`, etc., with attacker-controlled `seconds` query param) to trigger CPU/heap/goroutine profiling against internal plugin processes, which can leak internal state and consume CPU/memory for the configured duration — a limited denial-of-service vector, matching the "C:L/A:L" impact in the original CVSS vector.

### Likelihood Explanation
Likelihood is high for any deployment where the node's web/API port is reachable by untrusted clients (the same port serving the GraphQL API, sessions, and health routes), since no credentials, session cookie, or API key are required to hit `/discovery`, `/plugins/:name/metrics`, or `/plugins/:name/debug/pprof/*` — this only requires network reachability to the node's HTTP port.

### Recommendation
Wrap `loopRoutes(app, api)` registration behind the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` middleware used by `debugRoutes`/the authenticated `sessionRoutes` group, or move these plugin-discovery/metrics/pprof-proxy handlers to a dedicated internal-only listener that is not exposed on the public-facing API port.

### Proof of Concept
1. Deploy a Chainlink node with at least one LOOP plugin registered.
2. Without any session cookie or API credentials, issue:
   - `GET http://<node>:6688/discovery` → returns JSON listing plugin metrics targets.
   - `GET http://<node>:6688/plugins/<plugin-name>/metrics` → returns the plugin's raw Prometheus metrics.
   - `GET http://<node>:6688/plugins/<plugin-name>/debug/pprof/profile?seconds=30` → triggers a 30-second CPU profile against the internal plugin process and returns the pprof binary payload, all without authentication.

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

**File:** core/web/router.go (L185-199)
```go
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
```

**File:** core/web/router.go (L207-218)
```go
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
