This confirms the claim. The code at `core/web/router.go` shows `metricRoutes(authv2)` is called with no role wrapper, unlike every other route in the same group which uses `auth.RequiresAdminRole`, `auth.RequiresEditRole`, or `auth.RequiresRunRole`.Confirmed: `/v2/debug/pprof/*` routes have no test coverage in `routesRolesMap`, and no `SECURITY.md` exclusion exists for this. The claim is fully supported by the code.

Audit Report

## Title
Debug/pprof endpoints reachable by any authenticated role (no RBAC check) - ([File: core/web/router.go])

## Summary
`metricRoutes` mounts the full `net/http/pprof` handler set (`Index`, `Cmdline`, `Profile`, `Symbol`, `Trace`, and per-profile handlers) under the `authv2` route group with only session/token authentication and no role check, while nearly every other sensitive route in that same group is wrapped with `auth.RequiresAdminRole`, `auth.RequiresEditRole`, or `auth.RequiresRunRole`. Any authenticated user regardless of role (including the lowest-privilege `view` role) can access `/v2/debug/pprof/*` to dump heap/goroutine data or trigger CPU profiling/tracing.

## Finding Description
`metricRoutes(r *gin.RouterGroup)` registers pprof handlers directly on a sub-group with no authorization wrapper: [1](#0-0) . It is invoked as `metricRoutes(authv2)` inside `v2Routes`, where `authv2` is only protected by `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)`, which merely validates that the caller is *some* authenticated user and sets the user in context, without checking role: [2](#0-1) [3](#0-2) [4](#0-3) .

By contrast, virtually all other routes in the `authv2` group are explicitly wrapped, e.g. user management (`auth.RequiresAdminRole`), key import/export, and transfers: [5](#0-4) [6](#0-5) . The role hierarchy is `UserRoleView` (lowest) through `UserRoleAdmin`, and `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` in `core/web/auth/auth.go` enforce the corresponding minimum role via explicit checks against `user.Role`: [7](#0-6) . None of this role-checking logic is applied to `metricRoutes`. The regression test suite `routesRolesMap`/route-role table in `core/web/auth/auth_test.go` (which enumerates most `/v2/*` routes and asserts required roles) contains no entries for `/v2/debug/pprof/*`, confirming these routes are excluded from RBAC test coverage.

## Impact Explanation
A user holding only the `view` role (or any authenticated role, including tokens issued to low-trust integrations) can access `/v2/debug/pprof/heap`, `/goroutine`, `/allocs`, etc., potentially exposing in-memory runtime state, and can invoke `/v2/debug/pprof/profile?seconds=N` or `/trace?seconds=N` to force CPU-intensive profiling for attacker-controlled duration. On a Chainlink node, whose availability underpins time-sensitive OCR round participation and on-chain transaction submission, this is a concrete availability/information-disclosure issue mapping to the node API authorization/role-bypass impact category (privileged debug functionality reachable by an under-privileged authenticated principal).

## Likelihood Explanation
This requires only a single authenticated HTTP request with valid, low-privilege credentials (session cookie or `X-API-KEY`/`X-API-SECRET` token) — no race condition, chaining, or additional exploit primitive is needed. Since `view`-role tokens are the normal credential issued for read-only/monitoring integrations in multi-user Chainlink deployments, the precondition (an authenticated but non-admin user) is realistic and commonly present.

## Recommendation
Wrap `metricRoutes(authv2)` with an explicit role requirement consistent with the rest of the group (e.g., `auth.RequiresAdminRole`), and add `/v2/debug/pprof/*` route entries to the `routesRolesMap`/route-role table in `core/web/auth/auth_test.go` to prevent future regression of this access control gap.

## Proof of Concept
1. Create/obtain a Chainlink node user with `view` role and a valid session cookie or API token.
2. `GET /v2/debug/pprof/heap?debug=1` using the `view`-role credentials — expect HTTP 200 with heap data returned (no `401`/`403`), unlike calling an admin-only endpoint such as `GET /v2/users` with the same credentials, which returns `403 Forbidden` via `auth.RequiresAdminRole`.
3. `GET /v2/debug/pprof/profile?seconds=30` with the same credentials to confirm forced CPU profiling is possible for a non-admin, non-edit, non-run role user.
4. As a Go integration test: extend `core/web/auth/auth_test.go`'s route-role table with `{"GET", "/v2/debug/pprof/heap", false, false, false}` (admin-only expectation) and observe it currently fails because the route imposes no role restriction at all.

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

**File:** core/web/router.go (L276-281)
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

**File:** core/web/auth/auth.go (L153-173)
```go
// Authenticate is middleware which authenticates the request by attempting to
// authenticate using all the provided methods.
func Authenticate(store Authenticator, methods ...authMethod) gin.HandlerFunc {
	return func(c *gin.Context) {
		var err error
		for _, method := range methods {
			err = method(c, store)
			if !errors.Is(err, auth.ErrorAuthFailed) {
				break
			}
		}
		if err != nil {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, err)

			return
		}

		c.Next()
	}
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
