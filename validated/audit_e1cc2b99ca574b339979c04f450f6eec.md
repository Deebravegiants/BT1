### Title
Missing role/permission check allows any authenticated user (including view-only) to access sensitive pprof debug endpoints - ([File: core/web/router.go])

### Summary
Chainlink's HTTP API implements a role-based access control (RBAC) system (`view` < `run` < `edit` < `admin`) enforced via middleware such as `auth.RequiresAdminRole`, `auth.RequiresEditRole`, and `auth.RequiresRunRole` on nearly every sensitive route. However, the `/v2/debug/pprof/*` routes registered by `metricRoutes` are mounted directly under the `authv2` group with **no role check at all** — any authenticated session or API token, regardless of role (including the lowest-privilege `view` role), can invoke them.

### Finding Description
The router wires role checks per-route in `v2Routes`, e.g.: [1](#0-0) 

But the debug/profiling routes are added without any `auth.RequiresXRole` wrapper: [2](#0-1) 

```go
// Debug routes accessible via authentication
metricRoutes(authv2)
```

`metricRoutes` registers the full set of Go `net/http/pprof` handlers (`/`, `/cmdline`, `/profile`, `/symbol`, `/trace`, `/allocs`, `/block`, `/goroutine`, `/heap`, `/mutex`, `/threadcreate`) with no additional gating beyond the base `authv2` group's session/token authentication: [3](#0-2) 

By contrast, every other mutating or sensitive-data route in the same function is explicitly wrapped with a role check (`RequiresAdminRole`, `RequiresEditRole`, or `RequiresRunRole`), e.g. key export/delete, job delete, transfers, replay: [4](#0-3) [5](#0-4) 

The RBAC test suite (`routesRolesMap` in `auth_test.go`) enumerates expected role restrictions per route for exactly this purpose, but the `/v2/debug/pprof/*` routes are absent from that map, so there is no automated test guaranteeing the intended access level for these endpoints: [6](#0-5) 

This mirrors the Jenkins Support Core Plugin bug class: a sensitive administrative/diagnostic action (in Jenkins, deleting support bundles; here, dumping live process internals) is reachable by an actor holding only the lowest privilege level (`Overall/Read` in Jenkins ≈ `view` role in Chainlink) because the specific handler omits the extra permission check that the rest of the API consistently applies.

### Impact Explanation
`goroutine`, `heap`, `cmdline`, and `trace` profiles can leak internal process state: goroutine stack traces (revealing internal logic/paths and potentially embedded parameters), heap dumps (can contain in-memory secrets, keys, or session tokens depending on GC timing and allocation patterns), and the process command-line (which can reveal file paths, flags, or environment configuration). `/debug/pprof/profile` and `/trace` can also be used to place sustained CPU/tracing load on the node. Any user provisioned with only `view` access — meant to be read-only over job/config data — can pull this diagnostic data or induce load, which is a confidentiality and, to a lesser extent, availability impact from an actor who should not have this level of access. This aligns with CWE-281 (Improper Handling of Insufficient Permissions) similarly to the CVE-2019-16539 analog.

### Likelihood Explanation
High likelihood of reachability: the endpoints require only a valid, currently-issued authenticated session or API token (any role) via the standard `authv2` group, with no extra role check, no separate feature flag, and no build-tag gating observed in the reviewed router code. Any user account with the lowest privilege tier can trivially call these endpoints once authenticated.

### Recommendation
Wrap the `/v2/debug/pprof/*` handlers registered by `metricRoutes` with an explicit role check consistent with other sensitive/administrative routes (e.g., `auth.RequiresAdminRole`), and add corresponding entries to the RBAC route enumeration test (`routesRolesMap`) in `core/web/auth/auth_test.go` so that future changes cannot silently regress the missing permission check.

### Proof of Concept
1. Provision (or use) a Chainlink node user account with role `view` (the most restricted API role) or a `view`-scoped API token, per `UserController.Create`/`UpdateRole`.
2. Authenticate as that user and issue: `GET /v2/debug/pprof/heap` (or `/goroutine`, `/cmdline`, `/trace`, `/profile`).
3. Observe that the request succeeds (HTTP 200 with pprof binary/text data) instead of the `403 Forbidden` that other `edit`/`admin`-restricted routes return for the same role, as verified by the pattern established in `TestRBAC_Routemap_ViewOnly`.

**Note on confidence**: I could not find an explicit prior classification (e.g., a CHANGELOG entry or security note) confirming whether this lack of role-gating on `/v2/debug/pprof/*` is an intentional design decision (the comment "Debug routes accessible via authentication" suggests it may be deliberate) or an oversight. Given the codebase's otherwise strict and consistent per-route RBAC enforcement pattern, and the absence of these routes from the RBAC test matrix, I assess this as the strongest plausible analog to the reported bug class, but recommend confirming intent with the Chainlink security team before treating it as a confirmed vulnerability.

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

**File:** core/web/router.go (L245-257)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	{
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)
```

**File:** core/web/router.go (L315-320)
```go
		ekc := NewETHKeysController(app)
		authv2.GET("/keys/eth", ekc.Index)
		authv2.POST("/keys/eth", auth.RequiresEditRole(ekc.Create))
		authv2.DELETE("/keys/eth/:keyID", auth.RequiresAdminRole(ekc.Delete))
		authv2.POST("/keys/eth/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/eth/export/:address", auth.RequiresAdminRole(ekc.Export))
```

**File:** core/web/router.go (L394-396)
```go
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))
```

**File:** core/web/router.go (L438-447)
```go
		buildInfo := BuildInfoController{app}
		authv2.GET("/build_info", buildInfo.Show)

		vault := VaultController{app}
		authv2.POST("/vault/dkg_results/verify", auth.RequiresEditRole(vault.VerifyDKGResult))
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/auth/auth_test.go (L213-299)
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
```
