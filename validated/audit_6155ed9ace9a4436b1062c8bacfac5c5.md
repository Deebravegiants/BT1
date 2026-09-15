Audit Report

## Title
Unauthenticated pprof/debug and metrics proxy for LOOP plugins - (File: core/web/router.go, core/web/loop_registry.go)

## Summary
`loopRoutes` in `core/web/router.go` registers `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `POST /plugins/:name/debug/pprof/symbol` directly on the bare `api` router group with no authentication middleware. This is inconsistent with every other debug/profiling surface in the same file, which is explicitly wrapped in `auth.Authenticate`.

## Finding Description
In `NewRouter`, `loopRoutes(app, api)` is called on the unauthenticated `api` group alongside `debugRoutes`, `healthRoutes`, `sessionRoutes`, and `v2Routes` [1](#0-0) . Unlike `loopRoutes`, `debugRoutes` explicitly wraps its `/debug/vars` endpoint in session authentication [2](#0-1) , and the standard Go pprof handlers (`metricRoutes`) are only mounted under the authenticated `authv2` group [3](#0-2) . `loopRoutes` itself adds no such middleware [4](#0-3) .

This means `pluginPPROFHandler` and `pluginPPROFPOSTSymbolHandler`, which proxy live requests to the internal LOOP plugin's `/debug/pprof/...` endpoint, are reachable by any client that can reach the node's HTTP port with no session cookie or API token [5](#0-4) . The unauthenticated `discoveryHandler` further enumerates all registered plugin names, letting an attacker discover valid `:name` values needed to hit the pprof proxy [6](#0-5) . By default, `ListenIP` is `0.0.0.0` and `HTTPPort` is `6688`, so this surface is bound to all interfaces out of the box [7](#0-6) . This is a genuine asymmetry in the router: every comparable debug/profiling endpoint requires authentication except this one.

## Impact Explanation
An unauthenticated remote actor reachable on the node's main port can enumerate installed LOOP plugins and pull `heap`, `goroutine`, `profile`, `trace`, `allocs`, `block`, `mutex`, and `cmdline` pprof output from the internal plugin process. Heap/goroutine dumps of a running process can incidentally capture in-memory secrets, key material, or sensitive request data, which maps to the "key/secret exfiltration" impact class. The same path also allows repeated CPU/time-bounded `profile`/`trace` calls against the plugin, which is a resource-exhaustion vector, though pure DoS impacts are explicitly listed as out of scope per `SECURITY.md` ("Impacts that only require DDoS") [8](#0-7) . The information-disclosure angle (heap/memory content leakage) is the concrete, in-scope impact here, distinct from mere non-confidential info disclosure (IPs/server names) which is separately excluded [9](#0-8) .

## Likelihood Explanation
Likelihood is high for any node running LOOP plugins with the default `ListenIP = '0.0.0.0'`, since `loopRoutes` is registered unconditionally in `NewRouter` with no feature flag, and no credential is required to reach `/discovery` or `/plugins/:name/debug/pprof/*`.

## Recommendation
Wrap `loopRoutes` in the same `auth.Authenticate` middleware used by `debugRoutes` and `authv2`, e.g., register `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` under an authenticated router group rather than the bare `api` group, so that pprof/debug access to LOOP plugins requires the same session/token authentication as core node pprof access.

## Proof of Concept
1. Run a Chainlink node with default config (`ListenIP = '0.0.0.0'`, `HTTPPort = 6688`) and at least one LOOP plugin registered.
2. From a remote unauthenticated client:
   ```
   curl http://<node-ip>:6688/discovery
   ```
   Confirm plugin names are returned without any `Cookie` or `Authorization` header.
3. Using a discovered plugin name:
   ```
   curl http://<node-ip>:6688/plugins/<plugin-name>/debug/pprof/heap -o heap.out
   curl "http://<node-ip>:6688/plugins/<plugin-name>/debug/pprof/profile?seconds=30"
   ```
   Confirm both return `200 OK` with pprof binary data and no authentication challenge, in contrast to `curl http://<node-ip>:6688/v2/debug/pprof/heap`, which requires a valid session/API token via `authv2`.

### Citations

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

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/loop_registry.go (L52-65)
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

**File:** core/config/docs/core.toml (L195-208)
```text
# HTTPPort is the port used for the Chainlink Node API, [CLI](/docs/configuration-variables/#cli-client), and GUI.
HTTPPort = 6688 # Default
# SecureCookies requires the use of secure cookies for authentication. Set to false to enable standard HTTP requests along with `TLSPort = 0`.
SecureCookies = true # Default
# SessionTimeout determines the amount of idle time to elapse before session cookies expire. This signs out GUI users from their sessions.
SessionTimeout = '15m' # Default
# SessionReaperExpiration represents how long an API session lasts before expiring and requiring a new login.
SessionReaperExpiration = '240h' # Default
# HTTPMaxSize defines the maximum size for HTTP requests and responses made by the node server.
HTTPMaxSize = '32768b' # Default
# StartTimeout defines the maximum amount of time the node will wait for a server to start.
StartTimeout = '15s' # Default
# ListenIP specifies the IP to bind the HTTP server to
ListenIP = '0.0.0.0' # Default
```

**File:** SECURITY.md (L40-40)
```markdown
- Server-side non-confidential information disclosure, such as IPs, server names, and most stack traces.
```

**File:** SECURITY.md (L44-44)
```markdown
- Impacts that only require DDoS.
```
