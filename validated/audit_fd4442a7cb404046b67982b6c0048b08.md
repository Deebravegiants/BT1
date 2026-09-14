### Title
Unauthenticated LOOP Plugin Debug/Metrics/PPROF Endpoints Bypass the Node's Authentication Layer - (File: core/web/router.go)

### Summary
`monerod`'s ZMQ transport failed to inherit the `--restricted-rpc` policy enforced on the HTTP RPC surface, letting an unauthenticated remote client hit admin methods through a "second door" that had no auth check at all. Chainlink's `core/web/router.go` has the same class of defect: a second, parallel route group (`loopRoutes`) exposes plugin discovery, metrics, and pprof/profiling endpoints with no authentication middleware, while a functionally equivalent route group (`metricRoutes`, used for the node's own pprof) is deliberately wrapped in `auth.RequiresAdminRole`/session authentication.

### Finding Description
`NewRouter` builds an `api` group that only carries CORS/rate-limiting/session-cookie middleware — it does not itself enforce authentication [1](#0-0) . Individual route groups are expected to explicitly wrap themselves in `auth.Authenticate(...)`:

- `debugRoutes` wraps `/debug/vars` in `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` [2](#0-1) .
- `metricRoutes` (the node's own `/debug/pprof/*` endpoints — cmdline, profile, symbol, trace, allocs, block, goroutine, heap, mutex, threadcreate) is only ever mounted inside `authv2`, the group gated by `auth.Authenticate(..., auth.AuthenticateByToken, auth.AuthenticateBySession)`, and is explicitly commented as "Debug routes accessible via authentication" [3](#0-2) [4](#0-3) .

However, `loopRoutes` — which exposes the equivalent debug/metrics/pprof surface for LOOP (Long-Running Out-Of-Process) plugins — is registered directly on the bare `api` group in `NewRouter`, with no `auth.Authenticate` wrapper at all:

```go
debugRoutes(app, api)
healthRoutes(app, api)
sessionRoutes(app, api)
v2Routes(app, api)
loopRoutes(app, api)
``` [5](#0-4) 

```go
func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
}
``` [6](#0-5) 

This is precisely the ZMQ pattern from the report: two logically-parallel surfaces (`metricRoutes` vs `loopRoutes`, both serving `pprof`-class functionality) exist in the codebase, one is correctly gated behind the authentication/RBAC policy the operator expects to apply to the whole node ("the entire `/v2` and `/debug` surface requires a session or API token"), and the other silently inherits none of that policy because it is wired up at the top-level `NewRouter` function instead of inside the authenticated route builders.

### Impact Explanation
`/plugins/:name/debug/pprof/*profile` and `/plugins/:name/debug/pprof/symbol` map directly to Go's `net/http/pprof` handlers for each loaded LOOP plugin (the same handler set that `metricRoutes` protects with `auth.RequiresAdminRole`) [3](#0-2) . Unauthenticated pprof exposure allows a remote, unauthenticated client to:
- Pull CPU/heap/goroutine/mutex/block profiles and full stack traces (`/trace`, `/profile`, `/goroutine?debug=2`) of a plugin process, which can leak sensitive in-memory data (config, secrets held in memory, internal addresses, job/queue state).
- Enumerate loaded plugins and their addresses via `/discovery`.
- Potentially trigger resource exhaustion by requesting expensive profiles (`/debug/pprof/profile?seconds=N`) repeatedly, causing availability degradation of the plugin process — directly analogous to the `start_mining` CPU-theft impact in the Monero report, but here via forced profiling load instead of forced mining.

This crosses the same "documented restricted-vs-public" boundary the reporter flagged in Monero: the node's admin surface is intended to require authentication, but a second entry point into functionally the same class of operation (debug/profiling) was wired up without it.

### Likelihood Explanation
Likelihood is high for any deployment where the Chainlink node's HTTP API port is reachable by anyone other than the operator (which is common — the same `api`/`engine` router serves both the authenticated `/v2` API and these routes on the same listener/port). No credentials, tokens, or special network position are required — a single unauthenticated GET request is sufficient, exactly matching the report's "AV:N/AC:L/PR:N/UI:N" access vector. The only precondition is that one or more LOOP plugins are registered with the `LoopRegistryServer`, which is standard for OCR2/median/plugin-based EVM and non-EVM job types.

### Recommendation
Wrap `loopRoutes` in the same authentication middleware used for `debugRoutes`/`metricRoutes`, e.g. mount it inside `authv2` (or a dedicated group gated by `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` plus `auth.RequiresAdminRole`), rather than passing the unauthenticated `api` group into `loopRoutes` in `NewRouter`. Add a regression test analogous to the existing `TestRBAC_Routemap_*` suite in `core/web/auth/auth_test.go` [7](#0-6)  that asserts `/discovery`, `/plugins/:name/metrics`, and `/plugins/:name/debug/pprof/*` return 401/403 for unauthenticated and non-admin callers.

### Proof of Concept
Because this is a static-analysis finding derived from indexed code (I could not execute the Go binary in this environment), the PoC is a description of the expected request pattern to validate on a running node:

```
# No Authorization header, no session cookie
curl -s http://NODE_HOST:6688/discovery
curl -s http://NODE_HOST:6688/plugins/<plugin-name>/metrics
curl -s http://NODE_HOST:6688/plugins/<plugin-name>/debug/pprof/goroutine?debug=2
curl -s http://NODE_HOST:6688/plugins/<plugin-name>/debug/pprof/profile?seconds=30
```

Expected on a vulnerable build: HTTP 200 with plugin discovery data / pprof profile output, with no `401 Unauthorized` challenge — contrasting with the authenticated `/v2/debug/pprof/*` route which does require a valid session/token per `metricRoutes`'s placement inside `authv2` [4](#0-3) .

I was not able to fully inspect `core/web/loop_registry.go` (handler implementations for `discoveryHandler`, `pluginMetricHandler`, `pluginPPROFHandler`) within the indexed context beyond confirming their existence and route wiring; a full review of that file (not fully returned by the index) would be needed to confirm exactly what data each handler exposes. Given index size limits, I recommend a Devin session with full repository access to inspect `core/web/loop_registry.go` directly and confirm the precise data/plugin metadata exposed before finalizing severity.

### Citations

**File:** core/web/router.go (L78-91)
```go
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

**File:** core/web/router.go (L185-199)
```go
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

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/auth/auth_test.go (L213-341)
```go
// The following are admin only routes
var routesRolesMap = [...]routeRules{
	{"GET", "/v2/users", false, false, false},
	{"POST", "/v2/users", false, false, false},
	{"PATCH", "/v2/users", false, false, false},
	{"DELETE", "/v2/users/MOCK", false, false, false},
	{"PATCH", "/v2/user/password", true, true, true},
	{"POST", "/v2/user/token", true, true, true},
	{"POST", "/v2/user/token/delete", true, true, true},
	{"GET", "/v2/enroll_webauthn", true, true, true},
	{"POST", "/v2/enroll_webauthn", true, true, true},
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
	{"POST", "/v2/transfers", false, false, false},
	{"POST", "/v2/transfers/evm", false, false, false},
	{"POST", "/v2/transfers/cosmos", false, false, false},
	{"POST", "/v2/transfers/solana", false, false, false},
	{"GET", "/v2/config", true, true, true},
	{"GET", "/v2/config/v2", true, true, true},
	{"GET", "/v2/tx_attempts", true, true, true},
	{"GET", "/v2/tx_attempts/evm", true, true, true},
	{"GET", "/v2/transactions/evm", true, true, true},
	{"GET", "/v2/transactions/evm/MOCK", true, true, true},
	{"GET", "/v2/transactions", true, true, true},
	{"GET", "/v2/transactions/MOCK", true, true, true},
	{"POST", "/v2/replay_from_block/MOCK", false, true, true},
	{"GET", "/v2/keys/csa", true, true, true},
	{"POST", "/v2/keys/csa", false, false, true},
	{"POST", "/v2/keys/csa/import", false, false, false},
	{"POST", "/v2/keys/csa/export/MOCK", false, false, false},
	{"GET", "/v2/keys/eth", true, true, true},
	{"POST", "/v2/keys/eth", false, false, true},
	{"DELETE", "/v2/keys/eth/MOCK", false, false, false},
	{"POST", "/v2/keys/eth/import", false, false, false},
	{"POST", "/v2/keys/eth/export/MOCK", false, false, false},
	{"GET", "/v2/keys/ocr", true, true, true},
	{"POST", "/v2/keys/ocr", false, false, true},
	{"DELETE", "/v2/keys/ocr/:MOCKkeyID", false, false, false},
	{"POST", "/v2/keys/ocr/import", false, false, false},
	{"POST", "/v2/keys/ocr/export/MOCK", false, false, false},
	{"GET", "/v2/keys/ocr2", true, true, true},
	{"POST", "/v2/keys/ocr2/MOCK", false, false, true},
	{"DELETE", "/v2/keys/ocr2/MOCK", false, false, false},
	{"POST", "/v2/keys/ocr2/import", false, false, false},
	{"POST", "/v2/keys/ocr2/export/MOCK", false, false, false},
	{"GET", "/v2/keys/p2p", true, true, true},
	{"POST", "/v2/keys/p2p", false, false, true},
	{"DELETE", "/v2/keys/p2p/MOCK", false, false, false},
	{"POST", "/v2/keys/p2p/import", false, false, false},
	{"POST", "/v2/keys/p2p/export/MOCK", false, false, false},
	{"GET", "/v2/keys/solana", true, true, true},
	{"GET", "/v2/keys/cosmos", true, true, true},
	{"GET", "/v2/keys/starknet", true, true, true},
	{"GET", "/v2/keys/aptos", true, true, true},
	{"GET", "/v2/keys/stellar", true, true, true},
	{"GET", "/v2/keys/tron", true, true, true},
	{"GET", "/v2/keys/ton", true, true, true},
	{"POST", "/v2/keys/solana", false, false, true},
	{"POST", "/v2/keys/cosmos", false, false, true},
	{"POST", "/v2/keys/starknet", false, false, true},
	{"POST", "/v2/keys/aptos", false, false, true},
	{"POST", "/v2/keys/stellar", false, false, true},
	{"POST", "/v2/keys/tron", false, false, true},
	{"POST", "/v2/keys/ton", false, false, true},
	{"DELETE", "/v2/keys/solana/MOCK", false, false, false},
	{"DELETE", "/v2/keys/cosmos/MOCK", false, false, false},
	{"DELETE", "/v2/keys/starknet/MOCK", false, false, false},
	{"DELETE", "/v2/keys/aptos/MOCK", false, false, false},
	{"DELETE", "/v2/keys/stellar/MOCK", false, false, false},
	{"DELETE", "/v2/keys/tron/MOCK", false, false, false},
	{"DELETE", "/v2/keys/ton/MOCK", false, false, false},
	{"POST", "/v2/keys/solana/import", false, false, false},
	{"POST", "/v2/keys/cosmos/import", false, false, false},
	{"POST", "/v2/keys/starknet/import", false, false, false},
	{"POST", "/v2/keys/aptos/import", false, false, false},
	{"POST", "/v2/keys/stellar/import", false, false, false},
	{"POST", "/v2/keys/tron/import", false, false, false},
	{"POST", "/v2/keys/ton/import", false, false, false},
	{"POST", "/v2/keys/solana/export/MOCK", false, false, false},
	{"POST", "/v2/keys/cosmos/export/MOCK", false, false, false},
	{"POST", "/v2/keys/starknet/export/MOCK", false, false, false},
	{"POST", "/v2/keys/aptos/export/MOCK", false, false, false},
	{"POST", "/v2/keys/stellar/export/MOCK", false, false, false},
	{"POST", "/v2/keys/tron/export/MOCK", false, false, false},
	{"POST", "/v2/keys/ton/export/MOCK", false, false, false},
	{"GET", "/v2/keys/vrf", true, true, true},
	{"POST", "/v2/keys/vrf", false, false, true},
	{"DELETE", "/v2/keys/vrf/MOCK", false, false, false},
	{"POST", "/v2/keys/vrf/import", false, false, false},
	{"POST", "/v2/keys/vrf/export/MOCK", false, false, false},
	{"GET", "/v2/jobs", true, true, true},
	{"GET", "/v2/jobs/MOCK", true, true, true},
	{"POST", "/v2/jobs", false, false, true},
	{"DELETE", "/v2/jobs/MOCK", false, false, true},
	{"GET", "/v2/pipeline/runs", true, true, true},
	{"GET", "/v2/jobs/MOCK/runs", true, true, true},
	{"GET", "/v2/jobs/MOCK/runs/MOCK", true, true, true},
	{"GET", "/v2/features", true, true, true},
	{"DELETE", "/v2/pipeline/job_spec_errors/MOCK", false, false, true},
	{"GET", "/v2/log", true, true, true},
	{"PATCH", "/v2/log", false, false, false},
	{"GET", "/v2/chains/evm", true, true, true},
	{"GET", "/v2/chains/solana", true, true, true},
	{"GET", "/v2/chains/stellar", true, true, true},
	{"GET", "/v2/chains/cosmos", true, true, true},
	{"GET", "/v2/chains/evm/MOCK", true, true, true},
	{"GET", "/v2/chains/cosmos/MOCK", true, true, true},
	{"GET", "/v2/nodes/", true, true, true},
	{"GET", "/v2/nodes/evm", true, true, true},
	{"GET", "/v2/nodes/solana", true, true, true},
	{"GET", "/v2/nodes/stellar", true, true, true},
	{"GET", "/v2/nodes/cosmos", true, true, true},
	{"GET", "/v2/chains/evm/MOCK/nodes", true, true, true},
	{"GET", "/v2/chains/solana/MOCK/nodes", true, true, true},
	{"GET", "/v2/chains/stellar/MOCK/nodes", true, true, true},
	{"GET", "/v2/chains/cosmos/MOCK/nodes", true, true, true},
	{"GET", "/v2/nodes/evm/forwarders", true, true, true},
	{"POST", "/v2/nodes/evm/forwarders/track", false, false, true},
	{"DELETE", "/v2/nodes/evm/forwarders/MOCK", false, false, true},
	{"GET", "/v2/build_info", true, true, true},
	{"GET", "/v2/ping", true, true, true},
	{"POST", "/v2/jobs/MOCK/runs", false, true, true},
}
```
