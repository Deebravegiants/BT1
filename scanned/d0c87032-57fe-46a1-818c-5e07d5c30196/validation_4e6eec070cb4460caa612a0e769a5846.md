Based on the investigation, I found something worth flagging: the `metricRoutes` pprof group is mounted **without any authentication middleware**, unlike `debugRoutes`. [1](#0-0) 

Note the contrast:
- `debugRoutes` wraps `/debug/vars` in `auth.Authenticate(...)` [2](#0-1) 
- `metricRoutes` (mounted at `/v2/debug/pprof/*`) builds its `pprofGroup` directly from the group passed in with **no auth middleware applied to the group itself** — it relies entirely on the caller already being inside an authenticated group. [3](#0-2) 

Checking the call site confirms `metricRoutes(authv2)` is called on the already-authenticated `authv2` group, which requires token/session auth via `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, and none of the pprof sub-routes have any `auth.RequiresXRole` wrapper. [4](#0-3) [5](#0-4) 

This means any authenticated user — including a `UserRoleView` (view-only) user — can hit `/v2/debug/pprof/profile`, `/v2/debug/pprof/cmdline`, `/v2/debug/pprof/trace`, etc. These pprof endpoints can leak memory contents, goroutine stacks, command-line arguments (which may contain secrets), and full heap dumps. This is analogous in spirit to the Jenkins bug (a low-privileged actor reaching a sensitive diagnostic/introspection endpoint that should require a higher permission), but here the impact is more severe than mere file-existence disclosure — it's potential secret/heap disclosure to any authenticated low-privilege node user.

However, per the rules, I need to check whether this is truly "unprivileged" — in chainlink, all users of `/v2/*` routes are already authenticated node operators (not truly unprivileged/anonymous actors), so this may not qualify as a "missing permission check" analog exactly matching an unprivileged-actor class as strictly as the Jenkins CVE (Overall/Read is the lowest built-in permission, analogous to `UserRoleView`). Given `UserRoleView` is the lowest role and the pprof routes require no role check at all (unlike essentially every other admin-sensitive route in this file, which is wrapped in `RequiresAdminRole`/`RequiresEditRole`/`RequiresRunRole`), this is a legitimate role-bypass finding: a `view`-role user gets a capability that should require `admin`.

### Title
Missing role-based permission check on node pprof/debug endpoints allowing low-privilege user to access sensitive diagnostics - (File: core/web/router.go)

### Summary
The `/v2/debug/pprof/*` routes registered by `metricRoutes` in `core/web/router.go` are mounted on the already-authenticated `authv2` group but, unlike virtually every other sensitive route in the same file, are not wrapped with any `auth.RequiresAdminRole`/`RequiresEditRole`/`RequiresRunRole` check. Any authenticated user, including the lowest-privileged `UserRoleView` account, can access full Go `pprof` introspection (heap dumps, goroutine stacks, command-line, CPU/execution traces).

### Finding Description
`v2Routes` builds an authenticated group `authv2` requiring only session or token authentication (no role restriction) [4](#0-3) . Almost every sensitive controller action registered on `authv2` is explicitly wrapped with a role-check middleware such as `auth.RequiresAdminRole`, `auth.RequiresEditRole`, or `auth.RequiresRunRole` (e.g., key export/import, user management, transfers) [6](#0-5) .

However, `metricRoutes(authv2)` is called unconditionally at the end of the authenticated block and internally registers the pprof handlers with zero role-check wrapping: [3](#0-2) [5](#0-4) 

This is the direct analog of the Jenkins Script Security bug class: a form-validation-adjacent (here, diagnostic/introspection) endpoint that should require an elevated permission level but instead only checks that *some* authentication occurred, omitting the role/permission check entirely.

### Impact Explanation
A user provisioned with only `UserRoleView` (read-only, the lowest role in the RBAC model defined in `core/sessions`) can hit `GET /v2/debug/pprof/heap`, `/v2/debug/pprof/goroutine`, `/v2/debug/pprof/cmdline`, and `/v2/debug/pprof/profile`/`trace` (with attacker-controlled `seconds` query param). These can leak: full process memory contents (potentially containing decrypted secrets, private keys held in memory, database credentials), goroutine stacks (revealing internal architecture/data), and process command-line arguments. It can also be used as a limited DoS vector by forcing CPU/trace profiling for extended durations.

### Likelihood Explanation
Likelihood is high for any deployment that provisions view-only API users (e.g., for monitoring dashboards or read-only integrations) — a documented, supported role in the product. No additional social engineering or vulnerability chain is needed; a single authenticated HTTP GET is sufficient.

### Recommendation
Wrap the pprof route group registered by `metricRoutes` with an explicit `auth.RequiresAdminRole` (or at minimum `RequiresEditRole`) middleware, consistent with how every other sensitive `/v2` endpoint in `core/web/router.go` is protected. Also consider adding these routes to the `routesRolesMap` RBAC test table in `core/web/auth/auth_test.go` so future regressions are caught by `TestRBAC_Routemap_*`.

### Proof of Concept
1. As an admin, create a user with `UserRoleView` (e.g., via `POST /v2/users` with role `view`).
2. Log in as that view-only user (`POST /v2/sessions`).
3. Issue `GET /v2/debug/pprof/heap?debug=1` (or `/v2/debug/pprof/cmdline`, `/v2/debug/pprof/goroutine?debug=2`) using the view-only session cookie.
4. Observe `200 OK` with full pprof output, despite the view role being unable to access far less sensitive endpoints elsewhere in the RBAC map (compare to `TestRBAC_Routemap_ViewOnly` in `core/web/auth/auth_test.go`, which does not currently include pprof paths).

### Citations

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

**File:** core/web/router.go (L250-356)
```go
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)

		wa := NewWebAuthnController(app)
		authv2.GET("/enroll_webauthn", wa.BeginRegistration)
		authv2.POST("/enroll_webauthn", wa.FinishRegistration)

		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))

		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))

		ets := EVMTransfersController{app}
		authv2.POST("/transfers", auth.RequiresAdminRole(ets.Create))
		authv2.POST("/transfers/evm", auth.RequiresAdminRole(ets.Create))
		tts := CosmosTransfersController{app}
		authv2.POST("/transfers/cosmos", auth.RequiresAdminRole(tts.Create))
		sts := SolanaTransfersController{app}
		authv2.POST("/transfers/solana", auth.RequiresAdminRole(sts.Create))

		cc := ConfigController{app}
		authv2.GET("/config", cc.Show)
		authv2.GET("/config/v2", cc.Show)

		tas := TxAttemptsController{app}
		authv2.GET("/tx_attempts", paginatedRequest(tas.Index))
		authv2.GET("/tx_attempts/evm", paginatedRequest(tas.Index))

		txs := TransactionsController{app}
		authv2.GET("/transactions/evm", paginatedRequest(txs.Index))
		authv2.GET("/transactions/evm/:TxHash", txs.Show)
		authv2.GET("/transactions", paginatedRequest(txs.Index))
		authv2.GET("/transactions/:TxHash", txs.Show)

		rc := ReplayController{app}
		authv2.POST("/replay_from_block/:number", auth.RequiresRunRole(rc.ReplayFromBlock))
		lcaC := LCAController{app}
		authv2.GET("/find_lca", auth.RequiresRunRole(lcaC.FindLCA))
		lpSkipC := LPSkipController{app}
		authv2.POST("/lp_skip_to_block", auth.RequiresRunRole(lpSkipC.LPSkipToBlock))

		if build.IsDev() {
			capContr := CapabilityController{app}
			authv2.POST("/execute_capability", auth.RequiresRunRole(capContr.ExecuteCapability))
		}

		csakc := CSAKeysController{app}
		authv2.GET("/keys/csa", csakc.Index)
		authv2.POST("/keys/csa", auth.RequiresEditRole(csakc.Create))
		authv2.POST("/keys/csa/import", auth.RequiresAdminRole(csakc.Import))
		authv2.POST("/keys/csa/export/:ID", auth.RequiresAdminRole(csakc.Export))

		ekc := NewETHKeysController(app)
		authv2.GET("/keys/eth", ekc.Index)
		authv2.POST("/keys/eth", auth.RequiresEditRole(ekc.Create))
		authv2.DELETE("/keys/eth/:keyID", auth.RequiresAdminRole(ekc.Delete))
		authv2.POST("/keys/eth/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/eth/export/:address", auth.RequiresAdminRole(ekc.Export))
		// duplicated from above, with `evm` instead of `eth`
		// legacy ones remain for backwards compatibility

		ethKeysGroup := authv2.Group("", auth.Authenticate(app.AuthenticationProvider(),
			auth.AuthenticateByToken,
			auth.AuthenticateBySession,
		))

		ethKeysGroup.Use(ekc.formatETHKeyResponse())
		authv2.GET("/keys/evm", ekc.Index)
		ethKeysGroup.POST("/keys/evm", auth.RequiresEditRole(ekc.Create))
		ethKeysGroup.DELETE("/keys/evm/:address", auth.RequiresAdminRole(ekc.Delete))
		ethKeysGroup.POST("/keys/evm/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/evm/export/:address", auth.RequiresAdminRole(ekc.Export))
		ethKeysGroup.POST("/keys/evm/chain", auth.RequiresAdminRole(ekc.Chain))

		ocrkc := OCRKeysController{app}
		authv2.GET("/keys/ocr", ocrkc.Index)
		authv2.POST("/keys/ocr", auth.RequiresEditRole(ocrkc.Create))
		authv2.DELETE("/keys/ocr/:keyID", auth.RequiresAdminRole(ocrkc.Delete))
		authv2.POST("/keys/ocr/import", auth.RequiresAdminRole(ocrkc.Import))
		authv2.POST("/keys/ocr/export/:ID", auth.RequiresAdminRole(ocrkc.Export))

		ocr2kc := OCR2KeysController{app}
		authv2.GET("/keys/ocr2", ocr2kc.Index)
		authv2.POST("/keys/ocr2/:chainType", auth.RequiresEditRole(ocr2kc.Create))
		authv2.DELETE("/keys/ocr2/:keyID", auth.RequiresAdminRole(ocr2kc.Delete))
		authv2.POST("/keys/ocr2/import", auth.RequiresAdminRole(ocr2kc.Import))
		authv2.POST("/keys/ocr2/export/:ID", auth.RequiresAdminRole(ocr2kc.Export))

		p2pkc := P2PKeysController{app}
		authv2.GET("/keys/p2p", p2pkc.Index)
		authv2.POST("/keys/p2p", auth.RequiresEditRole(p2pkc.Create))
		authv2.DELETE("/keys/p2p/:keyID", auth.RequiresAdminRole(p2pkc.Delete))
		authv2.POST("/keys/p2p/import", auth.RequiresAdminRole(p2pkc.Import))
		authv2.POST("/keys/p2p/export/:ID", auth.RequiresAdminRole(p2pkc.Export))
```

**File:** core/web/router.go (L443-447)
```go
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```
