The claim is verified against the actual code. `NewRouter` creates the `api` group with only rate limiting and session middleware, no authentication, and `loopRoutes(app, api)` is registered on it directly with no `auth.Authenticate` wrapper, unlike `debugRoutes` (line 181) and `v2Routes`'s `authv2` group (line 245-248) in the same file.

<cite repo="AYontt/chainlink--006" path="core/web/router.go" start="77-91" />
<cite repo="AYontt/chainlink--006" path="core/web/router.go" start="180-183" />
<cite repo="AYontt/chainlink--006" path="core/web/router.go" start="230-236" />
<cite repo="AYontt/chainlink--006" path="core/web/router.go" start="245-248" />

The handlers in `LoopRegistryServer` — `discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, and `pluginPPROFPOSTSymbolHandler` — perform no authentication check themselves; they only validate that the named plugin exists in the registry, then proxy the request to the plugin's internal metrics/pprof port.

<cite repo="AYontt/chainlink--006" path="core/web/loop_registry.go" start="96-128" />
<cite repo="AYontt/chainlink--006" path="core/web/loop_registry.go" start="150-188" />

This confirms the exact root cause claimed: an unprivileged, unauthenticated network client reaching the node's operator API port can hit `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*`, and POST to `/plugins/:name/debug/pprof/symbol` without any token or session cookie, while the functionally equivalent core-process pprof endpoints (`metricRoutes`) are gated behind the `authv2` authenticated group. `pluginPPROFHandler` also forwards the `seconds` query parameter unchecked into a live CPU-profile duration request, which is a concrete resource-exhaustion vector, and heap/goroutine dumps can leak process memory contents of the plugin. This is a genuine CWE-306 missing-authentication bug on routes handling sensitive diagnostic data, reachable by any network client with no special privileges — it maps cleanly to the in-scope "node API authentication bypass" / information-disclosure impact class, and there is no evidence in the repository (SECURITY.md, commit history) that this was already fixed, acknowledged, or is an intentional design decision (comments in the code even note "unlike discovery, this endpoint is internal btw the node and plugin", indicating the intent was that it be treated as sensitive, yet no auth guard is applied at the router level).

Audit Report

## Title
Missing Authentication on LOOP Plugin Debug/Metrics/pprof Endpoints Exposes Internal Diagnostics and Runtime Profiling to Any Unauthenticated Client - (File: core/web/router.go)

## Summary
`loopRoutes` in `core/web/router.go` is registered on the base `api` gin group, which only applies rate-limiting and session middleware, with no call to `auth.Authenticate(...)`. This leaves the LOOP plugin `/discovery`, `/plugins/:name/metrics`, `/plugins/:name/debug/pprof/*`, and `/plugins/:name/debug/pprof/symbol` endpoints reachable by any unauthenticated client that can reach the node's operator HTTP port.

## Finding Description
`NewRouter` builds the `api` group with only `rateLimiter` and `sessions.Sessions` middleware and then calls `loopRoutes(app, api)` directly, with no authentication wrapper. In contrast, `debugRoutes` explicitly re-wraps its `/debug` subgroup with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)`, and `v2Routes` creates an `authv2` group wrapped with `auth.Authenticate(..., auth.AuthenticateByToken, auth.AuthenticateBySession)` before mounting the equivalent core-process `metricRoutes` (pprof) inside it. `loopRoutes` has no such wrapper, and the underlying handlers in `core/web/loop_registry.go` (`discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`, `pluginPPROFPOSTSymbolHandler`) perform no authentication or role checks of their own — they only look up the plugin by name in the registry and proxy the request to the plugin's internal port. This is a clear, verifiable asymmetry within the same file where the equivalent sensitive functionality (pprof/metrics) is otherwise consistently authenticated.

## Impact Explanation
An unauthenticated network client reaching the node's operator API port can enumerate all registered LOOP plugins and their internal Prometheus targets via `/discovery`, pull plugin Prometheus metrics, and trigger/retrieve `pprof` profiles (heap, goroutine, CPU profile with attacker-controlled `seconds` duration) and submit POST bodies to `/debug/pprof/symbol` for any named plugin. This is an information-disclosure risk (potential leakage of in-memory operational data via heap/goroutine dumps) and a resource-exhaustion vector (attacker-controlled long CPU profile duration), falling under CWE-306 missing authentication for a critical function, and it maps to the in-scope "node API authentication bypass" impact category.

## Likelihood Explanation
High. No credentials, tokens, or session cookies are required — only network reachability to the same port serving `/v2/*` routes, which is always active whenever LOOP plugins are configured, since `loopRoutes(app, api)` is registered unconditionally in `NewRouter`.

## Recommendation
Wrap the `loopRoutes` group with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` middleware used for `authv2`/`debugRoutes`, and apply `auth.RequiresAdminRole` (or an equivalent role check) consistent with how `metricRoutes` is protected for the core node's own pprof endpoints.

## Proof of Concept
Against a running node with LOOP plugins configured, issue with no cookies/tokens:
```
GET /discovery
GET /plugins/<plugin-name>/metrics
GET /plugins/<plugin-name>/debug/pprof/heap
GET /plugins/<plugin-name>/debug/pprof/profile?seconds=60
POST /plugins/<plugin-name>/debug/pprof/symbol
```
All succeed and return plugin-internal data because `loopRoutes(app, api)` in `NewRouter` is registered on the `api` group without any `auth.Authenticate` middleware, unlike `debugRoutes` and `v2Routes` in the same file (`core/web/router.go`).