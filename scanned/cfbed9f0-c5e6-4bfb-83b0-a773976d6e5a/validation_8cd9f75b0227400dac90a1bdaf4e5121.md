Confirmed: `loopRoutes` is registered directly on the base `api` group (line 91 of `core/web/router.go`) with no auth middleware, unlike `debugRoutes` which wraps its group with `auth.Authenticate` [1](#0-0) , and unlike the main node's pprof endpoints which are mounted via `metricRoutes(authv2)` inside the authenticated `authv2` group [2](#0-1) . This gives unauthenticated pprof access to LOOPP plugin processes.

### Title
Unauthenticated Information Disclosure and DoS via Missing Auth on LOOPP Plugin pprof/metrics Routes - (File: core/web/router.go)

### Summary
The `loopRoutes` function registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` directly on the base `api` router group, which only has rate limiting and CORS/session middleware — no authentication middleware is applied [3](#0-2) [4](#0-3) .

### Finding Description
Every sibling debug/introspection surface in the same router enforces authentication before exposure:
- `debugRoutes` wraps `/debug/vars` with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` [5](#0-4) .
- The main node's own pprof endpoints (`/v2/debug/pprof/*`) are mounted via `metricRoutes(authv2)`, inside the `authv2` group that requires `auth.AuthenticateByToken` or `auth.AuthenticateBySession` [6](#0-5) [7](#0-6) .

However `loopRoutes(app, api)` is invoked directly on the top-level `api` group before any of the authenticated sub-groups are established [3](#0-2) , and the handlers it registers proxy directly to plugin-process debug/metrics endpoints without any session/token check: `pluginPPROFHandler` forwards arbitrary `gc.Param("profile")` sub-paths to the plugin's `/debug/pprof/<profile>` endpoint [8](#0-7) , `pluginPPROFPOSTSymbolHandler` forwards to `/debug/pprof/symbol` with the raw POST body [9](#0-8) , and `pluginMetricHandler`/`discoveryHandler` expose Prometheus metrics and service-discovery target metadata (plugin names, ports, hostnames) [10](#0-9) [11](#0-10) . This is architecturally identical to the AVideo bug class: a debug/log-exposing endpoint that omits the authentication check applied to all its sibling endpoints.

### Impact Explanation
An unauthenticated remote client can pull full pprof profiles (`heap`, `goroutine`, `allocs`, `cmdline`, `trace`, `profile`) from any registered LOOPP plugin process (e.g. Median, Solana, Starknet relayer plugins). Heap and goroutine dumps frequently contain in-memory secrets, keys, or internal state, and `cmdline`/`trace` reveal internal configuration and topology. The `/profile` and `/trace` endpoints with an attacker-controlled `seconds` parameter can also be abused for a low-cost denial of service by holding plugin-process CPU/goroutines busy for the configured window [12](#0-11) . `/discovery` and `/plugins/:name/metrics` also leak internal hostnames, ports, and plugin names to unauthenticated callers [13](#0-12) .

### Likelihood Explanation
High: any client that can reach the node's HTTP web-server port can hit these endpoints with a plain unauthenticated GET/POST — no session, API token, or role is checked at any layer, and the routes are unconditionally registered whenever LOOPP plugins are enabled.

### Recommendation
Wrap `loopRoutes` registration with the same authentication middleware used for `debugRoutes`/`metricRoutes` (at minimum `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, ideally gated behind `auth.RequiresAdminRole` given the sensitivity of pprof access), or restrict these routes to a private/internal listener not reachable by unauthenticated external clients.

### Proof of Concept
```bash
# No credentials required
curl "https://<node-host>:6688/discovery"
curl "https://<node-host>:6688/plugins/median/metrics"
curl "https://<node-host>:6688/plugins/median/debug/pprof/heap" -o heap.pprof
curl "https://<node-host>:6688/plugins/median/debug/pprof/profile?seconds=30" -o cpu.pprof
```
Each request succeeds without any `Authorization`/session cookie, in contrast to the equivalent `/v2/debug/pprof/*` route which returns `401 Unauthorized` without credentials.

### Citations

**File:** core/web/router.go (L87-92)
```go
	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)

```

**File:** core/web/router.go (L180-199)
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

**File:** core/web/router.go (L445-447)
```go
		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/loop_registry.go (L52-93)
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

func pluginGroup(hostName string, port int, path string) *targetgroup.Group {
	return &targetgroup.Group{
		Targets: []model.LabelSet{
			// target address will be called by external prometheus
			{model.AddressLabel: model.LabelValue(fmt.Sprintf("%s:%d", hostName, port))},
		},
		Labels: map[model.LabelName]model.LabelValue{
			model.MetricsPathLabel: model.LabelValue(path),
		},
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

**File:** core/web/loop_registry.go (L168-188)
```go
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
