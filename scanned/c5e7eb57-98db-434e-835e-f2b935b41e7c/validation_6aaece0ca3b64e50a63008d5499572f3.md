The Zen Cart CVE's root cause is an unvalidated, attacker-controlled string being passed into a sensitive sink (a PHP `include`) without any authentication check. The closest concrete analog in this codebase is the LOOP-plugin debug/metrics proxy in `core/web`, which forwards unvalidated, attacker-controlled path/URL data to an internal service **with no authentication middleware applied at all**, unlike virtually every other route in the router.

### Title
Unauthenticated LOOP-plugin pprof/metrics proxy endpoints allow unvalidated path injection into internal debug requests - (File: `core/web/router.go`, `core/web/loop_registry.go`)

### Summary
The `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` routes are registered without any authentication middleware, unlike all other sensitive routes in the router (`debugRoutes`, `authv2`, etc.), and they forward attacker-controlled path/query data directly into an internally constructed HTTP request URL.

### Finding Description
In `core/web/router.go`, `loopRoutes(app, api)` is called directly on the base `api` group with no `auth.Authenticate(...)` wrapper, in contrast to `debugRoutes` which explicitly requires `auth.AuthenticateBySession`: [1](#0-0) [2](#0-1) 

`pluginPPROFHandler` takes the wildcard route parameter `profile` directly from the URL and concatenates it, unsanitized, into the target URL string via `fmt.Sprintf`, then dispatches the request: [3](#0-2) 

The dispatch itself builds an `http.Request` from attacker-influenced `url`/`body`/`urlVals` and executes it against an internal host with no further validation of the constructed path: [4](#0-3) 

The only gate is that `pluginName` must match an entry in `l.registry.Get(pluginName)` — a fixed, internally-controlled set of running plugin names, not a secret. Since there is no authentication requirement on these routes, any unauthenticated remote client that knows (or enumerates via `/discovery`) a running plugin name can reach this handler and control the appended request path/segments and POST body forwarded to the plugin's internal `/debug/pprof/*` and `/metrics` endpoints.

### Impact Explanation
This is analogous in bug-class terms to the Zen Cart issue: user-supplied path data reaches a sensitive request-construction sink without authentication or path validation. Here the impact is unauthenticated access to internal Go `pprof` debug endpoints (goroutine dumps, heap/cpu profiles, `/debug/pprof/trace`) proxied through the node's public API, which can leak sensitive in-memory data and enable resource-exhaustion DoS (e.g., attacker-controlled `seconds` param feeding into profiling duration), and to the plugin's `/metrics` endpoint contents. [5](#0-4) 

### Likelihood Explanation
High: the routes are reachable by any network client with no authentication token or session, the plugin name is discoverable via the also-unauthenticated `/discovery` endpoint, and the handler performs no further input validation on `profile`.

### Recommendation
Wrap `loopRoutes(app, api)` with the same `auth.Authenticate(...)` middleware used for `debugRoutes`/`authv2`, or at minimum require the Prometheus bearer-token gate (already used for `prometheusHandler`) uniformly across `/discovery` and `/plugins/*` routes. Additionally validate/allowlist the `profile` wildcard value before constructing the forwarded URL.

### Proof of Concept
1. Start a chainlink node with a LOOP plugin registered (e.g., median/relayer plugin running with a known name).
2. Without any session cookie or API token, issue: `GET /discovery` to enumerate the running plugin name.
3. Issue `GET /plugins/<name>/debug/pprof/profile?seconds=60` unauthenticated — the node proxies this straight to the plugin's internal pprof endpoint, returning a CPU profile capture, or use `seconds` to hold a goroutine/connection open for extended DoS. [6](#0-5) [2](#0-1)

### Citations

**File:** core/web/router.go (L91-91)
```go
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

**File:** core/web/loop_registry.go (L132-148)
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
