Audit Report

## Title
Unauthenticated LOOP registry discovery, metrics-proxy, and pprof-proxy endpoints bypass Chainlink node API authentication - (File: core/web/router.go)

## Summary
`loopRoutes` is registered directly on the top-level `api` gin group in `NewRouter`, which applies only rate limiting and session middleware, with no authentication check, unlike `v2Routes`/`metricRoutes` which are explicitly wrapped in an `auth.Authenticate(...)` group. <cite repo="AYontt/chainlink--024" path="core/web/router.go" start="77-91" /> <cite repo="AYontt/chainlink--024" path="core/web/router.go" start="230-236" /> <cite repo="AYontt/chainlink--024" path="core/web/router.go" start="238-248" /> This exposes `/discovery`, `/plugins/:name/metrics`, and the LOOP plugin pprof proxy endpoints to any client that can reach the node's API port without credentials.

## Finding Description
`NewRouter` mounts `loopRoutes(app, api)` on the unauthenticated `api` group, while sensitive functionality (including the node's own pprof handlers via `metricRoutes`) is placed inside `authv2 := r.Group("/v2", auth.Authenticate(...))`. <cite repo="AYontt/chainlink--024" path="core/web/router.go" start="444-447" /> The `loop_registry.go` handlers confirm the reachable surface: `discoveryHandler` returns Prometheus service-discovery JSON with internal plugin hostnames/ports, <cite repo="AYontt/chainlink--024" path="core/web/loop_registry.go" start="52-65" /> `pluginMetricHandler` proxies to a LOOP plugin's `/metrics` endpoint, <cite repo="AYontt/chainlink--024" path="core/web/loop_registry.go" start="95-128" /> and `pluginPPROFHandler`/`pluginPPROFPOSTSymbolHandler` proxy arbitrary pprof profile/symbol requests (CPU/heap/goroutine/trace) to the internal plugin process. <cite repo="AYontt/chainlink--024" path="core/web/loop_registry.go" start="150-188" />

The existing test `TestLoopRegistry` confirms this is exercised via a plain `app.NewHTTPClient(nil)` client with no authentication headers or session, and both `/discovery` and the plugin metrics proxy return `200 OK` without any credentials. <cite repo="AYontt/chainlink--024" path="core/web/loop_registry_test.go" start="99-152" /> This strongly suggests the `/metrics`-style and `/discovery` endpoints are an intentional design choice mirroring the pattern of Prometheus scrape endpoints (which are conventionally unauthenticated and expected to be protected at the network layer, similar to how the node's primary Prometheus metrics port is typically also unauthenticated). However, the pprof proxy endpoints are a materially different case: unlike the primary node's pprof, which is explicitly placed behind `auth.Authenticate` in `authv2` via `metricRoutes(authv2)`, the LOOP plugin's pprof proxy has no such gate, allowing an unauthenticated caller to trigger CPU/heap/goroutine profiling and trace captures against the internal plugin process through `pluginPPROFHandler`.

## Impact Explanation
This maps to the "node API authentication bypass" impact category to the extent that unauthenticated actors gain access to functionality that requires authentication everywhere else. The concrete impacts are:
- Disclosure of internal plugin topology (hostnames/ports) via `/discovery`.
- Ability to pull LOOP plugin Prometheus metrics, which may include operational/internal state.
- Ability to repeatedly trigger CPU/heap/goroutine/trace profiling captures against LOOP plugin processes via the unauthenticated pprof proxy, which can be used for resource exhaustion or to extract runtime memory/stack data.

The severity is tempered by two factors: (1) `/discovery` and `/metrics`-style endpoints being open is consistent with how metrics-scraping endpoints are commonly designed across the industry and appears to be an intentional pattern in this codebase (mirrored by the also-unauthenticated core `/metrics` path in the same test), and (2) exploitation requires a LOOP plugin to actually be registered (`app.GetLoopRegistry().List()` non-empty), which depends on which OCR/relayer plugins are configured to run out-of-process — this is not universal to every node deployment.

## Likelihood Explanation
`loopRoutes(app, api)` is called unconditionally in `NewRouter` with no build-tag or feature-flag gating, so wherever LOOP plugins are enabled, these routes are always live and reachable by any network client that can hit the node's API port. <cite repo="AYontt/chainlink--024" path="core/web/router.go" start="87-91" /> No special credentials, roles, or preconditions beyond network reachability and at least one registered LOOP plugin are required, making the pprof-proxy DoS/information-disclosure path realistically triggerable by an unprivileged actor.

## Recommendation
Wrap the `/plugins/:name/debug/pprof/*` and `/plugins/:name/debug/pprof/symbol` routes in an `auth.Authenticate(...)` (with `auth.RequiresAdminRole` similar to primary node pprof gating) before registration, consistent with `metricRoutes(authv2)`. Consider whether `/discovery` and `/plugins/:name/metrics` should remain open (as consistent with existing `/metrics` scraping conventions) or also be restricted, and document this as an intentional exception if kept open, since the current behavior is directly confirmed by `TestLoopRegistry` as tested/expected without authentication.

## Proof of Concept
1. Start a Chainlink node with the default WebServer configuration and register a LOOP plugin.
2. Without any session cookie or `X-API-KEY`/`X-API-SECRET` headers, issue:
   - `GET http://<node-host>:6688/discovery` → returns 200 with plugin discovery JSON, as demonstrated by `TestLoopRegistry`'s "discovery endpoint" subtest. <cite repo="AYontt/chainlink--024" path="core/web/loop_registry_test.go" start="101-122" />
   - `GET http://<node-host>:6688/plugins/<plugin-name>/metrics` → returns 200 with plugin metrics, as demonstrated by the "plugin metrics OK" subtest. <cite repo="AYontt/chainlink--024" path="core/web/loop_registry_test.go" start="124-140" />
   - `GET http://<node-host>:6688/plugins/<plugin-name>/debug/pprof/heap?seconds=30` → forwards to the LOOP plugin's pprof endpoint per `pluginPPROFHandler` with no auth check applied. <cite repo="AYontt/chainlink--024" path="core/web/loop_registry.go" start="150-166" />
3. Compare against the equivalent authenticated node pprof route `GET /v2/debug/pprof/heap`, which requires session/token auth via `authv2`/`metricRoutes(authv2)` and returns 401 without credentials. <cite repo="AYontt/chainlink--024" path="core/web/router.go" start="444-447" />