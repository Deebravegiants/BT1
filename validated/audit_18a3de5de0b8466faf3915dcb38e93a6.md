Audit Report

## Title
Missing Role-Based Authorization on Debug/Profiling Endpoints Allows Any Authenticated Non-Admin User to Access Runtime Memory, Goroutine, and Heap Data - (File: core/web/router.go)

## Summary
`metricRoutes` and `debugRoutes` in `core/web/router.go` register the pprof profiling endpoints (`/v2/debug/pprof/*`) and `/debug/vars` behind only session/token authentication (`auth.Authenticate`), with no role check applied, unlike essentially all other sensitive `/v2` routes in the same file which are wrapped in `auth.RequiresAdminRole` or `auth.RequiresEditRole`. [1](#0-0)  This lets any authenticated user — including one provisioned with the lowest-privilege `view` role — retrieve heap dumps, goroutine stacks, and expvar runtime data. [2](#0-1) 

## Finding Description
`v2Routes` authenticates the `/v2` group only via `auth.Authenticate(..., AuthenticateByToken, AuthenticateBySession)`, with no role restriction applied at the group level; role checks are instead applied per-route (e.g., `RequiresAdminRole`, `RequiresEditRole`) throughout the file. [3](#0-2)  `metricRoutes(authv2)` is called directly inside this group with no wrapping role middleware, registering `heap`, `goroutine`, `allocs`, `block`, `mutex`, `threadcreate`, `profile`, `trace`, `cmdline`, and `symbol` pprof handlers unguarded by any role check. [4](#0-3)  Similarly, `debugRoutes` exposes `/debug/vars` (Go's `expvar.Handler()`) behind session authentication only, again without any role gate. [5](#0-4)  This is confirmed inconsistent with the codebase's established pattern — e.g. the log-level PATCH endpoint and all key-export endpoints require `RequiresAdminRole`. [6](#0-5) 

The role hierarchy is `UserRoleView` (lowest) < `UserRoleRun` < `UserRoleEdit` < `UserRoleAdmin`, confirmed in `core/sessions/user.go`, and `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` in `core/web/auth/auth.go` show that a `view`-role user is fully authenticated but intended to be denied access to non-read-only or sensitive operations. [7](#0-6)  Because pprof/debug routes omit any of these checks, a `view`-role account can reach them with nothing more than a valid session/token — the same low bar as reading a dashboard.

## Impact Explanation
Heap dumps and goroutine profiles from a running node process can, in the worst case, contain in-memory secrets (decrypted keys, tokens, credentials) as well as internal file paths, function names, and full stack traces of live goroutines. This is a legitimate authorization gap (CWE-862) — a user with only `view`-level intended access can pull data intended to require at least `admin`/`edit`-level privileges, based on the codebase's own established sensitivity conventions (e.g., `/v2/log` PATCH and key-export routes require admin). However, the project's own `SECURITY.md` explicitly places "server-side non-confidential information disclosure, such as ... most stack traces" out of scope for the Websites/Apps category, and the claim's PoC does not demonstrate actual extraction of secret material from the heap dump — it only demonstrates that the endpoints are reachable with a `view`-role session. The theoretical possibility that secrets *could* appear in a heap dump is not concretely proven here.

## Likelihood Explanation
Reaching this endpoint requires holding a valid authenticated session or API token for the node, i.e., being an already-provisioned user (even at `view` role) — this is not an anonymous/unauthenticated attack surface. Provisioning of any user account (including `view`) is itself an admin-controlled action, narrowing the practical attacker population to insiders/already-trusted low-privilege accounts. Given a `view`-role account exists, the exploit is trivial to reproduce (single authenticated `GET`).

## Recommendation
Wrap `metricRoutes` and the `/debug/vars` route with `auth.RequiresAdminRole` (or at minimum `auth.RequiresEditRole`), consistent with other sensitive `/v2` routes such as key-export and `/v2/log` PATCH, so that only privileged roles can access runtime introspection endpoints.

## Proof of Concept
As submitted: authenticate as a `view`-role user (`POST /sessions`), then issue `GET /v2/debug/pprof/heap`, `GET /v2/debug/pprof/goroutine?debug=2`, and `GET /debug/vars` with the session cookie — all succeed with no role check, confirmed by direct code inspection of `debugRoutes`/`metricRoutes`/`v2Routes` in `core/web/router.go`. No further exploitation (e.g., extraction of an actual secret) was demonstrated.

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

**File:** core/web/router.go (L443-447)
```go
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/auth/auth.go (L198-253)
```go
// RequiresRunRole extracts the user object from the context, and asserts the user's role is at least
// 'run'
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```
