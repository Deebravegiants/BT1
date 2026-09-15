### Title
Debug/pprof endpoints reachable by any authenticated role (no RBAC check) - ([File: core/web/router.go])

### Summary
Chainlink's node API mounts `net/http/pprof` handlers under the authenticated `/v2` route group but does not enforce any role check on them, unlike nearly every other privileged route in the same group. Any user who can authenticate (session cookie or API token), regardless of assigned role, can reach `/v2/debug/pprof/*` and trigger CPU/heap/goroutine/trace profiling and view runtime internals — the same bug class as Fleet's GHSA-4r5r-ccr6-q6f6 (debug/pprof reachable by any authenticated user, including the lowest-privilege role).

### Finding Description
`metricRoutes` registers the full set of `net/http/pprof` handlers (`Index`, `Cmdline`, `Profile`, `Symbol`, `Trace`, and per-profile handlers for `allocs`, `block`, `goroutine`, `heap`, `mutex`, `threadcreate`) directly with no wrapping authorization middleware: [1](#0-0) 

This function is invoked as `metricRoutes(authv2)` inside `v2Routes`, where `authv2` is a router group protected only by `auth.Authenticate(..., AuthenticateByToken, AuthenticateBySession)` — i.e., it validates that the caller is *some* authenticated user, but performs no role check: [2](#0-1) [3](#0-2) 

Contrast this with virtually every other sensitive handler in the same `authv2` group, which is explicitly wrapped with `auth.RequiresAdminRole`, `auth.RequiresEditRole`, or `auth.RequiresRunRole` (e.g. user management, key export/import, EVM transfers, capability execution): [4](#0-3) [5](#0-4) 

Chainlink defines four roles with strictly increasing privilege — `UserRoleView`, `UserRoleRun`, `UserRoleEdit`, `UserRoleAdmin` — with `view` being the lowest-privilege role analogous to Fleet's "Observer": [6](#0-5) 

Because `metricRoutes` sits inside `authv2` with no `Requires*Role` wrapper, a user with only `view` role (or any role) who has valid session/token credentials can hit `/v2/debug/pprof/profile`, `/v2/debug/pprof/heap`, `/v2/debug/pprof/trace`, etc. The project's own RBAC regression test suite (`routesRolesMap` in `core/web/auth/auth_test.go`), which enumerates nearly every `/v2/*` route and asserts the correct role is required, does not include any `/v2/debug/pprof/*` entries — confirming these routes are excluded from role-enforcement testing entirely: [7](#0-6) 

### Impact Explanation
A low-privilege authenticated user (e.g. `view` role, which per Chainlink's role model should only have read access to non-sensitive data) can:
- Read runtime internals via `/v2/debug/pprof/heap`, `/goroutine`, `/allocs` — potentially leaking memory contents, stack traces, and internal state that could include sensitive in-memory data (keys, secrets, config) processed by the node.
- Trigger CPU-intensive `/v2/debug/pprof/profile` and `/v2/debug/pprof/trace` with attacker-controlled `seconds` parameter, consuming CPU resources and potentially degrading or denying service on a node that is also responsible for time-sensitive job execution (OCR rounds, transaction submission), which has real availability/financial impact for a blockchain oracle node.

This mirrors the Fleet CVE-2026-23517 impact of unauthorized diagnostics access plus DoS risk, but on a node whose availability is tied to job execution and fund movement.

### Likelihood Explanation
Any user with valid, low-privilege credentials (session or API token) can exploit this with a single unauthenticated-role HTTP request — no special conditions, race, or additional bypass required. Given that `view`-role tokens are commonly issued to monitoring/read-only integrations, this is straightforward to reach in a typical multi-user Chainlink node deployment.

### Recommendation
Wrap `metricRoutes(authv2)` with an explicit role check consistent with the rest of the `authv2` group (e.g., `auth.RequiresAdminRole`), and add `/v2/debug/pprof/*` entries to the `routesRolesMap` regression test in `core/web/auth/auth_test.go` so future changes cannot silently regress this access control.

### Proof of Concept
1. Create or obtain a Chainlink node user with `view` role and a valid session cookie or API token (`X-API-KEY`/`X-API-SECRET`).
2. Issue: `GET /v2/debug/pprof/heap?debug=1` with the `view`-role credentials.
3. Observe HTTP 200 with full heap dump returned, despite the route sitting in the same authenticated group as admin-only routes — no `403 Forbidden` is returned as it would be for `RequiresAdminRole`-protected endpoints.
4. Repeat with `GET /v2/debug/pprof/profile?seconds=30` to confirm the same low-privilege user can force 30 seconds of CPU profiling on the node.

### Citations

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

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/router.go (L251-254)
```go
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
```

**File:** core/web/router.go (L276-282)
```go
		authv2.POST("/transfers", auth.RequiresAdminRole(ets.Create))
		authv2.POST("/transfers/evm", auth.RequiresAdminRole(ets.Create))
		tts := CosmosTransfersController{app}
		authv2.POST("/transfers/cosmos", auth.RequiresAdminRole(tts.Create))
		sts := SolanaTransfersController{app}
		authv2.POST("/transfers/solana", auth.RequiresAdminRole(sts.Create))

```

**File:** core/web/router.go (L444-447)
```go

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/sessions/user.go (L29-34)
```go
const (
	UserRoleAdmin UserRole = "admin"
	UserRoleEdit  UserRole = "edit"
	UserRoleRun   UserRole = "run"
	UserRoleView  UserRole = "view"
)
```

**File:** core/web/auth/auth_test.go (L309-340)
```go
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
```
