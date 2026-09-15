Based on the code review, the claims in the report are accurate: `loopRoutes` at [1](#0-0)  is mounted directly on the `api` group without any `auth.Authenticate` wrapper, unlike `debugRoutes` [2](#0-1)  and the `authv2` group [3](#0-2) . The `pluginPPROFHandler` does concatenate the raw `profile` wildcard directly into the forwarded URL string with no sanitization [4](#0-3) .

Audit Report

## Title
Unauthenticated LOOP plugin proxy routes forward unsanitized path segments to internal plugin host - (File: core/web/router.go, core/web/loop_registry.go)

## Summary
The `loopRoutes` group in `core/web/router.go` registers `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*profile`, and `/plugins/:name/debug/pprof/symbol` on the shared `api` router group with only rate-limiting and session middleware, omitting the `auth.Authenticate` wrapper applied to every sibling functional group (`debugRoutes`, `sessionRoutes`, `authv2`). `pluginPPROFHandler` further builds the forwarded request URL by directly concatenating the caller-controlled `profile` wildcard parameter into a `fmt.Sprintf` string with no `path.Clean` or allowlist check, allowing any unauthenticated network client with access to the node's HTTP listener to make the node issue requests to arbitrary paths on the plugin's internal host:port.

## Finding Description
`NewRouter` mounts `loopRoutes` on the same `api` group as `debugRoutes`, `sessionRoutes`, and `v2Routes`, but only `loopRoutes` is left unauthenticated: `debugRoutes` explicitly wraps its `/debug` group with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`, and the equivalent authenticated `/v2/debug/pprof` routes (`metricRoutes`) are nested inside the `authv2` group requiring `auth.AuthenticateByToken`/`AuthenticateBySession`. `loopRoutes`, by contrast, registers `discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, and `pluginPPROFPOSTSymbolHandler` directly on `api` with no additional authentication middleware.

In `pluginPPROFHandler`, the URL forwarded to the internal loop host is built as `fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), l.loopHostName, p.EnvCfg.PrometheusPort)`, directly splicing the unsanitized wildcard `profile` segment into the target URL before it is used by `doRequest` to issue an outbound `http.DefaultClient.Do` call whose response body is streamed straight back to the caller. There is no `path.Clean`, prefix confinement, or allowlist restricting `profile` to the known pprof sub-paths (`cmdline`, `profile`, `symbol`, `trace`, `allocs`, `block`, `goroutine`, `heap`, `mutex`, `threadcreate`), unlike the confinement pattern used elsewhere in the codebase (e.g. `newFileFetcher`'s `strings.HasPrefix` check in `core/services/workflows/syncer/v2/fetcher.go`).

## Impact Explanation
An unauthenticated client that can reach the node's HTTP listener can invoke these endpoints without any session, token, or role check, and can manipulate the `profile` wildcard to redirect the node's outbound proxied request to other paths served by the plugin's internal HTTP server at `loopHostName:PrometheusPort`. This breaks the authentication boundary consistently enforced on the equivalent authenticated pprof/debug routes elsewhere in the router and can expose plugin diagnostic/runtime information (goroutine stacks, heap profiles, environment-derived data) to unauthenticated network callers. Note that `loopHostName` defaults to `localhost` and the port comes from the registry's `EnvCfg.PrometheusPort` for a known registered plugin, so the blast radius is confined to the local plugin process's HTTP surface rather than arbitrary external hosts — this narrows but does not eliminate the impact, since it still allows unauthenticated disclosure of internal plugin diagnostic data that is elsewhere access-controlled.

## Likelihood Explanation
High for reachability: no credentials are needed, only network access to the node's HTTP port and a valid plugin name (itself enumerable via the also-unauthenticated `/discovery` endpoint). Exploiting the path-splicing only requires crafting the wildcard segment of a GET request.

## Recommendation
1. Wrap `loopRoutes` (or at minimum `pluginPPROFHandler`, `pluginPPROFPOSTSymbolHandler`, and `pluginMetricHandler`) with `auth.Authenticate(app.AuthenticationProvider(), ...)`, consistent with `debugRoutes` and the `authv2` metric routes.
2. In `pluginPPROFHandler`, validate `gc.Param("profile")` against an explicit allowlist of supported pprof sub-paths, or apply `path.Clean` plus a strict prefix/equality check before constructing `pluginURL`.

## Proof of Concept
```
# Enumerate a registered plugin name (unauthenticated)
curl http://<node>:<port>/discovery

# Unauthenticated pprof proxy forwarding with attacker-controlled path segment
curl "http://<node>:<port>/plugins/<plugin-name>/debug/pprof/../../some/internal/path?seconds=1"
```
No session cookie, API token, or credentials are supplied; the request succeeds because `loopRoutes` is mounted without `auth.Authenticate`, and the `profile` wildcard is forwarded unsanitized to the internal plugin host.

### Citations

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

**File:** core/web/loop_registry.go (L158-159)
```go
	// unlike discovery, this endpoint is internal btw the node and plugin
	pluginURL := fmt.Sprintf("http://%s:%d/debug/pprof/"+gc.Param("profile"), l.loopHostName, p.EnvCfg.PrometheusPort)
```
