### Title
Missing Role-Based Authorization on `/v2/debug/pprof/*` Endpoints - ([File: core/web/router.go])

### Summary
The Jenkins CVE describes missing permission checks that let any authenticated low-privilege ("Overall/Read") user reach sensitive internal HTTP endpoints (schema/plugin documentation) that should have required a higher permission level. The Chainlink node's web API has a direct analog: the `/v2/debug/pprof/*` routes are mounted behind only the generic `Authenticate` middleware (token or session), with no `RequiresEditRole`/`RequiresRunRole`/`RequiresAdminRole` gate applied, unlike essentially every other sensitive admin-style endpoint in the router.

### Finding Description
In `core/web/router.go`, `metricRoutes` registers Go's `net/http/pprof` handlers directly on the `authv2` router group: [1](#0-0) 

and it is wired into the authenticated group at: [2](#0-1) 

`authv2` itself only requires successful authentication (token or session) — no role check: [3](#0-2) 

Contrast this with the rest of the router where every state-changing or sensitive-read endpoint explicitly wraps its handler with `auth.RequiresEditRole`, `auth.RequiresRunRole`, or `auth.RequiresAdminRole` (e.g. `/keys/eth/export`, `/config`, `/replay_from_block`, `/vault/dkg_results/export`, etc.), as seen throughout `v2Routes`: [4](#0-3) 

The RBAC enforcement logic itself lives in `core/web/auth/auth.go`, where `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` are the only mechanisms that gate access beyond "is authenticated": [5](#0-4) 

Because `pprofGroup` in `metricRoutes` has none of these role wrappers, any authenticated user — including one holding only the lowest `UserRoleView` role (or an API token scoped to view-only) — can hit `/v2/debug/pprof/heap`, `/goroutine`, `/profile`, `/trace`, `/allocs`, `/block`, `/mutex`, `/threadcreate`, and `/cmdline`. This is the same bug class as the CVE: an endpoint exposing detailed internal runtime/application information is reachable by a user whose role should not grant access to it, because the specific endpoint was never wrapped in the role-check middleware that protects comparable endpoints elsewhere in the same router.

### Impact Explanation
`pprof` heap/goroutine/profile dumps can capture in-memory application state — potentially including key material, session tokens, or other secrets held in memory — cmdline reveals process invocation flags/paths, and `profile`/`trace` can be used to induce CPU load (a DoS primitive) by any low-privileged authenticated user. This mirrors the CVE's core harm category: read-only/low-privilege authenticated actors gain access to detailed internal information they should not be entitled to see.

### Likelihood Explanation
Any user who can obtain a valid session cookie or API token at the lowest role (`view`) can reach these routes with a simple `GET` request — no special conditions, timing, or race required. Because it is gated only by `Authenticate`, likelihood of exploitation by any legitimate but low-privileged account holder is high, though it does require possession of *some* valid credential (not a fully unauthenticated attacker).

### Recommendation
Wrap the `pprofGroup` routes in `metricRoutes` with `auth.RequiresAdminRole` (consistent with other operationally sensitive endpoints such as `/log` PATCH, `/keys/*/export`, `/keys/*/import`), or gate the entire `/debug/pprof` mount behind a build-time/config flag (similar to `InsecurePPROFHeap`) in addition to authentication, so that only admin-role users or explicitly-enabled debug builds can reach these diagnostics endpoints.

### Proof of Concept
1. Create or obtain a Chainlink node user/API-token with `UserRoleView` (the lowest role).
2. Authenticate via `/sessions` (or with an API token) as this view-only user.
3. Issue `GET /v2/debug/pprof/heap` (or `/goroutine`, `/profile`, `/cmdline`) using the view-only session/token.
4. Observe that the request succeeds (HTTP 200 with pprof profile data) instead of being rejected with `403 Forbidden`, because `metricRoutes`'s pprof handlers are not wrapped by any `auth.RequiresXRole` check, unlike comparable sensitive endpoints in `v2Routes`. [1](#0-0) [2](#0-1)

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

**File:** core/web/router.go (L309-320)
```go
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

**File:** core/web/auth/auth.go (L198-234)
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
```
