Audit Report

## Title
Unauthenticated path-confusion in LOOP pprof proxy allows redirecting internal requests outside `/debug/pprof/` - (File: `core/web/loop_registry.go`)

## Summary
`pluginPPROFHandler` builds the outbound URL to a LOOP plugin's internal pprof/metrics server by directly concatenating the unescaped `profile` route parameter into a `fmt.Sprintf` format string, and this route is registered without any authentication middleware, unlike essentially every other stateful endpoint in the router. This allows any unauthenticated network client that can reach the node's HTTP API to make the node issue proxied requests to arbitrary paths on the internal LOOP plugin host/port, not just under `/debug/pprof/`.

## Finding Description
`pluginPPROFHandler` reads `gc.Param("profile")` and splices it into the URL as part of the format string itself, not as an argument: [1](#0-0) 
The route is registered as a wildcard `*profile` (matches everything after `/debug/pprof/`, including a leading `/`): [2](#0-1) 
Critically, `loopRoutes(app, api)` is invoked directly on the base `api` router group in `NewRouter`, alongside `debugRoutes`/`v2Routes`/etc., but — unlike `debugRoutes` (wrapped in `auth.Authenticate(...)`) and `authv2` (wrapped in token/session auth) — `loopRoutes` applies **no authentication middleware at all**: [3](#0-2) [4](#0-3) 
Because gin does not clean `..` segments from the wildcard match before it reaches the handler, and the value is concatenated as a raw format string, a crafted `profile` value containing `../` sequences can cause `pluginURL` to resolve outside the intended `/debug/pprof/` namespace once passed through `http.NewRequestWithContext`/`http.DefaultClient.Do` and normalized on the wire to the internal LOOP plugin's HTTP listener on `p.EnvCfg.PrometheusPort`: [5](#0-4) . The plugin's own `NewLoopRegistry`/`Register` code only allocates a port and passes config to the plugin process — it does not constrain what that internal HTTP listener exposes — [6](#0-5) , so what is reachable at other paths on that internal listener depends on the specific LOOP plugin binary (outside this repo).

## Impact Explanation
The `/plugins/:name/debug/pprof/*profile` route being unauthenticated is the more serious and clearly provable part of this finding: any unprivileged network client that can reach the node's web port can invoke this proxy without a session or API token, which the code base treats as a security boundary everywhere else (`auth.Authenticate`, `auth.RequiresAdminRole`, etc. gate essentially all other stateful/debug routes). Combined with the unescaped `fmt.Sprintf` concatenation, an attacker can attempt to redirect the proxied request to paths other than the intended pprof sub-profile on the internal LOOP plugin's metrics/pprof HTTP listener. This maps to an internal-SSRF/path-confusion primitive reachable without authentication. However, the concrete blast radius is bounded and not fully provable here: the target internal listener (`p.EnvCfg.PrometheusPort`) is, based on this repo's code, only known to expose `/metrics` and the standard `/debug/pprof/*` handlers — both already low-sensitivity debug/metrics data with no evident state-changing or secret-disclosing endpoints on that specific listener. I could not confirm from this repository whether the actual LOOP plugin binaries (external to this repo, e.g. relayer/median/mercury LOOPPs) expose anything more sensitive on that same port, which is necessary to establish a concrete high-impact result (e.g., key/secret exfiltration) rather than just re-reaching `/metrics` or other pprof endpoints that are already exposed by the route's own wildcard design.

## Likelihood Explanation
Triggering the request requires no credentials — the route sits on the unauthenticated `api` group, no session, token, or role check is present, and `profile` is taken verbatim from the URL path. Any client able to reach the node's web server can send this request; exploitation of the routing/handler logic itself is trivial and repeatable.

## Recommendation
- Wrap `loopRoutes` (or at minimum the pprof/metrics proxy handlers) in the same authentication middleware used elsewhere (e.g., `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`), or otherwise clarify/restrict this to a genuinely internal-only listener if it must remain open for external Prometheus scraping.
- Validate `profile` against an allowlist of pprof profile names, and build the outbound request via `url.URL{Path: ...}` with `url.PathEscape`, never folding user input into the `fmt.Sprintf` format string.

## Proof of Concept
Send, without any session cookie or API token:
```
GET /plugins/<validPluginName>/debug/pprof/../../metrics
```
This is dispatched by `pluginPPROFHandler` (reachable with no auth per `core/web/router.go` L87-92, L230-236) and builds `pluginURL = "http://<loopHostName>:<port>/debug/pprof/../../metrics"`, which is sent unauthenticated via `l.doRequest` (`core/web/loop_registry.go` L190-204) to the internal LOOP plugin host. A full end-to-end PoC proving disclosure of something more sensitive than `/metrics`/`/debug/pprof/*` would require inspecting the actual LOOP plugin binary's HTTP mux on `PrometheusPort`, which is outside this repository and was not verified in this pass.

### Citations

**File:** core/web/loop_registry.go (L158-159)
```go
	// unlike discovery, this endpoint is internal btw the node and plugin
	pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), l.loopHostName, p.EnvCfg.PrometheusPort)
```

**File:** core/web/loop_registry.go (L190-204)
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
```

**File:** core/web/router.go (L87-92)
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

**File:** plugins/loop_registry.go (L76-96)
```go
// Register creates a port of the plugin. It is not idempotent. Duplicate calls to Register will return [ErrExists]
// Safe for concurrent use.
func (m *LoopRegistry) Register(id string) (*RegisteredLoop, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	if _, exists := m.registry[id]; exists {
		return nil, ErrExists
	}
	ports, err := freeport.Take(1)
	if err != nil {
		return nil, fmt.Errorf("failed to get free port: %w", err)
	}
	if len(ports) != 1 {
		return nil, errors.New("failed to get free port: no ports returned")
	}
	envCfg := loop.EnvConfig{
		AppID:            m.appID,
		FeatureLogPoller: m.featureLogPoller,
		PrometheusPort:   ports[0],
	}
```
