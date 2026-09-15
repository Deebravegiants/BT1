This confirms the code exactly as claimed. `loopRoutes(app, api)` is registered on the base `api` group at [1](#0-0) , which only has rate limiting and session middleware, no auth: [2](#0-1) . Meanwhile `metricRoutes` (the equivalent pprof endpoints for the node itself) is only ever mounted under `authv2`, which requires authentication: [3](#0-2) [4](#0-3) . The `loopRoutes` function registers the pprof proxy routes with no auth middleware applied: [5](#0-4) .Audit Report

## Title
Unauthenticated pprof profiling proxy for LOOP plugins enables remote CPU/heap/trace resource-exhaustion DoS and internal infrastructure disclosure - (File: `core/web/router.go`, `core/web/loop_registry.go`)

## Summary
The `/plugins/:name/debug/pprof/*profile` and `/plugins/:name/debug/pprof/symbol` routes are registered via `loopRoutes(app, api)` on the base `api` gin group, which only carries rate-limiting and session middleware and no authentication. This lets any unauthenticated remote client trigger CPU/heap/goroutine/trace profiling against LOOP plugin processes for an attacker-chosen duration, and can leak internal plugin hostnames/ports in error responses.

## Finding Description
In `NewRouter`, the `api` group is created with only rate limiting and cookie session middleware — no auth check: [2](#0-1) . `loopRoutes(app, api)` is mounted directly on this group alongside other routes: [1](#0-0) .

`loopRoutes` registers the pprof proxy handlers with no additional auth middleware applied at the group or route level: [5](#0-4) .

This is inconsistent with the equivalent host-level pprof endpoints. `metricRoutes`, which exposes the same class of `net/http/pprof` handlers for the node itself, is only ever mounted under `authv2`, a group gated by `auth.Authenticate(... auth.AuthenticateByToken, auth.AuthenticateBySession)`: [3](#0-2) [4](#0-3) . No equivalent gate exists for `loopRoutes`.

The handler `pluginPPROFHandler` builds a proxy URL to the plugin's internal pprof endpoint using the client-supplied `profile` path parameter and forwards query values including `seconds`, which is also used to compute the request timeout: [6](#0-5) [7](#0-6) . There is no upper bound on `seconds`, and no authentication has been performed prior to this handler executing. `doRequest` performs the outbound HTTP call, and on failure paths returns the internal plugin URL/hostname/port directly in the plaintext HTTP response body: [8](#0-7) .

The code comments ("this endpoint is internal btw the node and plugin") reflect an assumption that is not enforced by any actual authentication check on the exposed route, so the assumption is broken.

## Impact Explanation
This maps to a service-unavailability/resource-exhaustion impact: an unauthenticated client can force sustained CPU consumption in plugin processes by supplying a large `seconds` value to `/plugins/:name/debug/pprof/profile` (or `trace`), and can repeat/parallelize this across all registered plugin names to amplify the effect. Additionally, error responses from `doRequest` can leak internal plugin hostnames and ports (LOOP inter-process communication topology) to an unauthenticated caller, which is a concrete information-disclosure side effect of the same missing-auth root cause.

## Likelihood Explanation
Likelihood is high — the vulnerable route requires no credentials, no session, and no special headers; a single unauthenticated GET request against the node's default webserver port reaching `NewRouter`'s `api` group is sufficient. The `seconds` parameter is attacker-controlled and passed through unvalidated in `pprofURLVals`, and the request can be trivially repeated or parallelized across plugin names.

## Recommendation
Apply the same authentication middleware used for `authv2`/`metricRoutes` (`auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`) to `loopRoutes`, or at minimum wrap the `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` routes in an authenticated group, mirroring `metricRoutes`'s gating under `authv2`. Additionally, bound the `seconds` query parameter to a sane maximum in `pprofURLVals`, and avoid echoing internal plugin URLs/hostnames in error response bodies returned by `doRequest`.

## Proof of Concept
1. Start a chainlink node with at least one LOOP plugin registered in `plugins.LoopRegistry`.
2. Without any session cookie or API token, send:
   `GET http://<node>/plugins/<plugin-name>/debug/pprof/profile?seconds=60`
3. Observe the request is proxied by `pluginPPROFHandler` -> `doRequest` to the plugin's internal `/debug/pprof/profile` endpoint with a `60+30` second timeout computed in `pprofURLVals`, with no `401 Unauthorized` returned at any point since the `api` group applied via `loopRoutes(app, api)` carries no authentication middleware.
4. Repeat concurrently across plugin names/`seconds` values to demonstrate amplification, and trigger a request against a non-plugin backend/misconfigured port to observe the internal `pluginURL` (hostname:port) being echoed in the plaintext error response from `doRequest`.

### Citations

**File:** core/web/router.go (L77-85)
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
```

**File:** core/web/router.go (L87-91)
```go
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

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/router.go (L445-446)
```go
		// Debug routes accessible via authentication
		metricRoutes(authv2)
```

**File:** core/web/loop_registry.go (L130-148)
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
```

**File:** core/web/loop_registry.go (L150-166)
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
```

**File:** core/web/loop_registry.go (L190-215)
```go
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
