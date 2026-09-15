Audit Report

## Title
Unauthenticated path/URL injection via unsanitized `profile` parameter in LOOP pprof proxy - (File: core/web/loop_registry.go)

## Summary
`loopRoutes` registers `/plugins/:name/debug/pprof/*profile` on the top-level `api` router group in `core/web/router.go`, which is only wrapped with rate-limiting and session-cookie-parsing middleware — no `auth.Authenticate(...)` wrapper, unlike `debugRoutes`, `sessionRoutes`, and the authenticated half of `v2Routes` in the same file. `pluginPPROFHandler` takes the gin wildcard `*profile` route parameter directly from the URL and concatenates it, unsanitized, into an outbound backend request URL built with `fmt.Sprintf`, letting any unauthenticated caller control the path/query suffix of a server-side request the node makes to the internal LOOP plugin process.

## Finding Description
`core/web/router.go` mounts `loopRoutes` on the shared `api` group with no per-route or per-group authentication: [1](#0-0) 

Compare this to sibling route groups that explicitly wrap sensitive routes in `auth.Authenticate(...)`: [2](#0-1) [3](#0-2) [4](#0-3) 

`loopRoutes` performs no such wrapping, confirming the route group is unauthenticated except for the rate limiter and session-cookie middleware applied to the whole `api` group.

Inside `pluginPPROFHandler`, the wildcard `profile` param is concatenated directly into the backend request URL string, and is even embedded inside the first argument to `fmt.Sprintf` (used as part of the format string itself): [5](#0-4) 

There is no validation, escaping, or allowlisting of `profile` against expected pprof sub-paths (`cmdline`, `profile`, `symbol`, `trace`, `heap`, etc.) before the request is forwarded via `l.doRequest` to `http://<loopHostName>:<PrometheusPort>/debug/pprof/<attacker-controlled-suffix>`, and the raw backend response bytes are returned to the caller: [6](#0-5) 

## Impact Explanation
This is a genuine broken-access-control issue on a Chainlink node's HTTP API surface: an unauthenticated network client that can reach the node's web server can force the node to issue arbitrary GET requests (with an attacker-chosen path/query suffix) to the internal LOOP plugin process at `loopHostName:PrometheusPort`, and read back the raw response. This is an internal-service request-forgery/proxy issue enabled purely by missing authentication middleware on the `loopRoutes` group, which the code comment ("unlike discovery, this endpoint is internal btw the node and plugin") confirms was an unintended oversight rather than a deliberate design choice. It maps to the "node API authentication bypass" impact class since the route is reachable by any unprivileged client without a session or API token, unlike essentially every comparable internal/debug route in the same router (`debugRoutes`, `sessionRoutes` DELETE, authenticated `v2Routes`).

That said, the severity is bounded: the destination host and port (`loopHostName:PrometheusPort`) are fixed by server-side configuration, not attacker-controlled, so this is not a classic SSRF to arbitrary hosts — the attacker can only vary the path/query sent to that one already-known internal endpoint, which is itself a debug/metrics-class internal service (LOOP plugin's pprof/metrics listener), not a source of secrets, funds, or privileged actions by itself.

## Likelihood Explanation
High reachability: the route requires no credentials, tokens, or session, and is exposed on the same top-level router as all other API traffic. Exploitation only requires that a LOOP plugin be registered/running with a resolvable `PrometheusPort`, which is a normal operating configuration, not a special privilege requirement on the attacker's part.

## Recommendation
- Wrap `loopRoutes` (or at minimum `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler`) with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, consistent with `debugRoutes` and the authenticated `v2Routes` group.
- Validate/allowlist the `profile` wildcard against the fixed set of pprof sub-paths instead of directly concatenating user input into the backend URL.
- Avoid embedding untrusted input inside a `fmt.Sprintf` format string; build the URL via `url.URL{Path: path.Join(...)}` with explicit escaping.

## Proof of Concept
1. Run a node with a LOOP plugin registered (`PrometheusPort` configured).
2. As an unauthenticated client, send:
   ```
   GET /plugins/<plugin-name>/debug/pprof/../metrics HTTP/1.1
   Host: <node-host>:<web-port>
   ```
3. Observe `pluginPPROFHandler` forwards the request to `http://<loopHostName>:<PrometheusPort>/debug/pprof/../metrics` (or any attacker-chosen suffix) with no authentication check, per `core/web/loop_registry.go` lines 150-166, and returns the response body to the unauthenticated caller via `gc.Data(http.StatusOK, "text/plain", b)`.
4. Contrast with `GET /v2/users` on the same server, which requires `auth.Authenticate(...)` per `core/web/router.go` lines 245-248, demonstrating the inconsistency and confirming the missing auth wrapper on `loopRoutes` is the root cause.

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
