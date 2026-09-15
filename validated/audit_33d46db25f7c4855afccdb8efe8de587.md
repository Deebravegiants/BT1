Audit Report

## Title
Unauthenticated Disclosure of Internal Node Info and Full pprof Debug Data via LOOP Registry Routes - (File: core/web/router.go, core/web/loop_registry.go)

## Summary
`loopRoutes` in `core/web/router.go` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` on the bare `api` group with no `auth.Authenticate` wrapper, unlike `/debug/vars` (wrapped in `debugRoutes`) and most of `/v2/*` (wrapped in `authv2`). [1](#0-0) [2](#0-1)  The `/discovery` and `/plugins/:name/metrics` portion of this is intentional, documented behavior for Prometheus service discovery/scraping, but the pprof-forwarding endpoints riding on the same unauthenticated route group is a genuine gap that exposes full plugin process debug data (heap, goroutine, profile, symbol) to any unauthenticated caller.

## Finding Description
`core/web/router.go` mounts `loopRoutes` on the top-level `api` group, which only has rate limiting and session middleware, no auth: [3](#0-2)  This is inconsistent with `debugRoutes`, which wraps `/debug/vars` in `auth.Authenticate(...)`, [1](#0-0)  and with `v2Routes`, which splits into `unauthedv2` (only the resume webhook) and `authv2` (everything else). [4](#0-3) 

However, `plugins/README.md` documents `/discovery` and `/plugins/<name>/metrics` as intentionally-exposed Prometheus service-discovery/scrape-proxy endpoints, explicitly stating the node "route[s] external prom scraping to the plugins without exposing them directly," with a sample scrape config pointing directly at the plugain node's HTTP port with no auth token. This confirms the discovery/metrics endpoints are unauthenticated by design, matching how the core node's own `/metrics` endpoint behaves (gated only by an optional `Prometheus.AuthToken`, not session auth). [5](#0-4)  This is corroborated by `core/web/loop_registry_test.go`, which explicitly exercises `/discovery` and `/plugins/<name>/metrics` using an unauthenticated HTTP client (`app.NewHTTPClient(nil)`) and asserts success, confirming this is expected, tested behavior rather than an oversight.

The pprof-forwarding handlers, however, are not mentioned in the documented design and carry materially higher risk: `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler` proxy the full Go `pprof` debug surface (heap, goroutine, profile, symbol) from the plugin's internal port to any caller, with source comments noting the channel is meant to be "internal btw the node and plugin." [6](#0-5)  Unlike the metrics/discovery case, there is no test, documentation, or design note establishing that unauthenticated pprof access was an intentional tradeoff — it appears to have been added under the same route group as the (intentionally open) discovery/metrics endpoints without separately considering that pprof output is far more sensitive (heap contents, goroutine stacks with argument values, CPU profiles) than a Prometheus metrics page.

## Impact Explanation
An unauthenticated remote client can enumerate plugin names via `/discovery` and then pull full `pprof` debug data (`heap`, `goroutine?debug=2`, `profile`, `symbol`) for any named LOOP plugin process. Depending on what the plugin holds in memory, this could disclose internal operational state, configuration, or other sensitive data embedded in the plugin's runtime. This maps to an information-disclosure impact category, though it is distinctly narrower than the report's framing: it does not disclose data from the core Chainlink node process itself (keys, wallet data, job configs), only from the separate LOOP plugin subprocess's `/debug/pprof` surface, and the `/discovery` and `/metrics` portions of the report are not a vulnerability at all — they are documented, tested, intended behavior consistent with standard Prometheus scraping design.

## Likelihood Explanation
High for reachability (no credentials needed, plugin name discoverable via `/discovery`), but the severity of what's actually exposed depends heavily on what runs inside the LOOP plugin process and whether operators run LOOP plugins in production (the feature is marked "Experimental" in `plugins/README.md`). No evidence was found that this specific pprof-forwarding gap has been separately reported, fixed, or acknowledged as a known issue — the metrics/discovery unauthenticated behavior is provably intentional and in-scope-excluded ("server-side non-confidential information disclosure" per `SECURITY.md`), but the pprof-forwarding piece stands on separate, more concerning footing that the provided evidence does not fully resolve as either intentional or already mitigated elsewhere (e.g., network segmentation of the plugin process, which is outside the scope of what this index can confirm).

## Recommendation
Keep `/discovery` and `/plugins/:name/metrics` unauthenticated (consistent with existing Prometheus scraping design and the core `/metrics` pattern gated by an optional bearer token), but gate the `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` routes behind the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` middleware used by `debugRoutes`, or require a `Prometheus.AuthToken`-style bearer token specifically for the pprof proxy paths.

## Proof of Concept
```
# No credentials required, plugin name obtained from GET /discovery
curl "http://<node-host>:<web-port>/plugins/<plugin-name>/debug/pprof/heap?debug=1"
curl "http://<node-host>:<web-port>/plugins/<plugin-name>/debug/pprof/goroutine?debug=2"
```
Confirmed via `core/web/router.go` L230-236 (no auth wrapper on `loopRoutes`) and `core/web/loop_registry.go` L150-188 (`pluginPPROFHandler`/`pluginPPROFPOSTSymbolHandler` proxy raw pprof bytes with no session/token check). A Go integration test analogous to the existing `TestLoopRegistry` in `core/web/loop_registry_test.go`, but hitting `/plugins/<name>/debug/pprof/heap` with an unauthenticated `app.NewHTTPClient(nil)` and asserting `200 OK` with pprof payload bytes, would demonstrate the gap concretely.

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

**File:** core/web/router.go (L660-700)
```go
// prometheusUse is adapted from ginprom.Prometheus.Use
// until merged upstream: https://github.com/Depado/ginprom/pull/48
func prometheusUse(p *ginprom.Prometheus, e *gin.Engine, handlerOpts promhttp.HandlerOpts) {
	var (
		r prometheus.Registerer = p.Registry
		g prometheus.Gatherer   = p.Registry
	)
	if p.Registry == nil {
		r = prometheus.DefaultRegisterer
		g = prometheus.DefaultGatherer
	}
	h := promhttp.InstrumentMetricHandler(r, promhttp.HandlerFor(g, handlerOpts))
	e.GET(p.MetricsPath, prometheusHandler(p.Token, h))
	p.Engine = e
}

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
