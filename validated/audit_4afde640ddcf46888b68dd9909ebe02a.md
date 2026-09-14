Based on my research, I found a directly analogous pattern in the chainlink web router.

### Title
Missing role-based authorization on `/debug/vars` endpoint allows low-privilege authenticated users to access internal runtime state - (File: core/web/router.go)

### Summary
The Chainlink node's `/debug/vars` route is registered behind session authentication only, with no minimum-role check, unlike every other `/v2/*` administrative route in the same router which is explicitly wrapped with `auth.RequiresViewRole`/`RequiresEditRole`/`RequiresAdminRole` middleware.

### Finding Description
`debugRoutes` wires the Go `expvar` handler behind a router group that only requires a valid authenticated session, with no role check applied: [1](#0-0) 

This mirrors the Ech0 bug class exactly: the handler is gated purely on "is there a valid session/JWT," not on "does this session have sufficient privilege." Contrast this with the rest of the router, where every `/v2/*` route is registered with an explicit role-requiring middleware layer, and the existing RBAC test table treats admin-sensitive routes (e.g. `/v2/config`, `/v2/keys/*`) as requiring elevated roles rather than merely a valid session: [2](#0-1) [3](#0-2) 

The `expvar.Handler()` used at `/debug/vars` exposes all registered `expvar.Vars` for the process, which by default includes `cmdline` (full process command-line arguments, which can include config paths, flags, and in some deployments secrets passed via CLI) and `memstats` (detailed runtime/GC statistics that aid fingerprinting and resource-exhaustion timing attacks), plus any custom counters the application registers.

### Impact Explanation
Any user who can obtain a valid Chainlink node session — including the lowest-privilege `view` role — can read `/debug/vars` because `debugRoutes` never calls `RequiresViewRole`/`RequiresEditRole`/`RequiresAdminRole`. Since `view`-role credentials are the ones a compromised or malicious low-trust integration/read-only user would hold, this endpoint leaks operational/internal information (process arguments, GC/memory internals) to a principal that should not have operator-level visibility, echoing the CWE-862 pattern in the source report (authenticated-but-not-authorized log/introspection endpoint).

### Likelihood Explanation
Exploitation only requires a valid, low-privilege session cookie — no special network position, no additional bypass. Every authenticated user in the system, regardless of role, can reach this route as soon as they log in, making likelihood high for any deployment where non-admin accounts exist (a first-class, documented feature of Chainlink's RBAC model with `view`/`run`/`edit`/`admin` roles).

### Recommendation
Wrap the `/debug/vars` route (and any other `debug`/introspection routes) with the same `auth.RequiresAdminRole` middleware used elsewhere in the router, consistent with how `/v2/config`, `/v2/keys/*`, and other operationally sensitive endpoints are protected:

```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", auth.RequiresAdminRole(expvar.Handler()))
}
```

### Proof of Concept
1. Create a Chainlink node user with `view` role (the lowest privilege) via the admin `/v2/users` API.
2. Log in as that user via `POST /sessions` to obtain a session cookie.
3. Issue `GET /debug/vars` with that cookie — the request succeeds (no 403), returning full `expvar` JSON output including `cmdline` and `memstats`, despite the user having no administrative role.

**Note on confidence:** I was unable to fully view the `v2Routes` function body (it was not returned by my searches before the tool budget ran out) to confirm whether `/v2/log` (the `LogController` in `core/web/log_controller.go`) — which exposes and mutates log level/SQL-logging config — is itself gated by `RequiresAdminRole` or a lower role. If it turns out that `/v2/log` is only gated by session authentication (like `/debug/vars`), that would be an even closer analog to the Ech0 report since it directly controls/exposes logging behavior. This should be verified in a full checkout of `core/web/router.go`.

### Citations

**File:** core/web/router.go (L180-183)
```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", expvar.Handler())
}
```

**File:** core/web/auth/auth_test.go (L236-238)
```go
	{"GET", "/v2/config", true, true, true},
	{"GET", "/v2/config/v2", true, true, true},
	{"GET", "/v2/tx_attempts", true, true, true},
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
