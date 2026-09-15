Based on the codebase investigation, there is a genuine analog to this Juju bug class in the Chainlink node's HTTP web server: **debug/profiling endpoints that require only generic authentication but no role-based authorization check**, exposing sensitive runtime data to any authenticated user regardless of role (including the lowest-privilege `view` role).

### Title
Authenticated-but-unauthorized disclosure of sensitive runtime data via `/v2/debug/pprof/*` and `/debug/vars` endpoints - (File: core/web/router.go)

### Summary
The Chainlink node web server exposes Go's `net/http/pprof` profiling endpoints and the `expvar` debug endpoint behind session/token authentication only, without any per-role permission check. Any user account that can authenticate — including accounts with the lowest privilege `UserRoleView` — can pull heap dumps, goroutine stacks, CPU/execution traces, and process variable dumps.

### Finding Description
In `NewRouter`, `debugRoutes` wraps the `/debug/vars` (`expvar`) endpoint only with `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession)` and applies no role check: [1](#0-0) 

Similarly, `metricRoutes`, which registers the full set of `net/http/pprof` handlers (`/`, `/cmdline`, `/profile`, `/symbol`, `/trace`, `/allocs`, `/block`, `/goroutine`, `/heap`, `/mutex`, `/threadcreate`), is invoked at the very end of `v2Routes` on the already-authenticated `authv2` group with the comment "Debug routes accessible via authentication" — but no `auth.RequiresEditRole`/`auth.RequiresAdminRole` wrapper is applied, unlike every other sensitive route in that same group (e.g. key management, transfers, user management): [2](#0-1) [3](#0-2) 

By contrast, comparably sensitive routes in the same file are explicitly gated by role, e.g. `RequiresAdminRole` for transfers and user management, `RequiresEditRole` for keys/bridges: [4](#0-3) 

The authorization primitives that should be applied — `RequiresRunRole`, `RequiresEditRole`, `RequiresAdminRole` — exist and are used elsewhere in the router but are absent from the pprof/expvar registration: [5](#0-4) 

This mirrors the Juju CVE-2025-53512 pattern exactly: the endpoint checks only that *some* authenticated identity is attached to the request (`auth.Authenticate(...)`), but omits the subsequent, endpoint-specific authorization/role check that other equally-sensitive routes enforce.

### Impact Explanation
`pprof`'s `/heap`, `/goroutine`, `/allocs`, and `/profile` outputs can leak in-memory secrets (API keys, private keys held by the keystore, session tokens, decrypted config values) and internal application state, satisfying CWE-200 (Information Exposure) with confidentiality impact and no integrity/availability impact — consistent with the CVSS vector in the referenced advisory (`C:H/I:N/A:N`). `/debug/vars` exposes internal counters and Go runtime memstats that can aid further attacks (e.g., timing/DoS reconnaissance). Any account with only `view` role — the lowest privilege tier intended for read-only dashboard access — can reach these endpoints, which is a privilege-boundary violation.

### Likelihood Explanation
Likelihood is high for any deployment where multiple users/roles share a node (a common multi-operator setup), since exploitation requires only a valid low-privilege session or API token and a single unauthenticated-but-authorized HTTP GET — no additional conditions, timing, or race requirements. The existing RBAC test suite in `auth_test.go` (`routesRolesMap`) does not include `/v2/debug/pprof/*` or `/debug/vars` paths, indicating these routes are not exercised by the RBAC regression tests and the gap could persist undetected. [6](#0-5) 

### Recommendation
Wrap `metricRoutes(authv2)` and the `/debug/vars` route with an explicit role check (e.g. `auth.RequiresAdminRole`), consistent with how other sensitive internal endpoints (transfers, key export/import, user management) are protected. Add corresponding entries to the `routesRolesMap` RBAC test table so future regressions are caught automatically.

### Proof of Concept
1. Create a low-privilege user: `POST /v2/users` with role `view` (as admin).
2. Authenticate as that user via `POST /sessions` to obtain a session cookie (or an API token pair).
3. Issue `GET /v2/debug/pprof/heap?debug=1` (or `/v2/debug/pprof/goroutine?debug=2`, `/debug/vars`) using only the `view` session/token — no admin/edit role.
4. Observe HTTP 200 with a full heap/goroutine dump or `expvar` JSON returned, despite the account holding only view-level privileges, confirming the missing authorization check identified in `core/web/router.go`.

### Citations

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

**File:** core/web/router.go (L441-447)
```go
		vault := VaultController{app}
		authv2.POST("/vault/dkg_results/verify", auth.RequiresEditRole(vault.VerifyDKGResult))
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))

		// Debug routes accessible via authentication
		metricRoutes(authv2)
	}
```

**File:** core/web/auth/auth.go (L217-253)
```go
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

**File:** core/web/auth/auth_test.go (L203-215)
```go
// Test RBAC (Role based access control) of each route and their required user roles
// Admin is omitted from the fields here since admin should be able to access all routes
type routeRules struct {
	verb               string
	path               string
	viewOnlyAllowed    bool
	editMinimalAllowed bool
	EditAllowed        bool
}

// The following are admin only routes
var routesRolesMap = [...]routeRules{
	{"GET", "/v2/users", false, false, false},
```
