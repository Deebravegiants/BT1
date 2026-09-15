Analyzing the routes registered in `v2Routes`, I found a concrete unprivileged-access-control gap analogous to the Footium `mintPlayers()` issue: a mutating, fund/config-affecting endpoint is registered without any role-check wrapper (`auth.RequiresEditRole`/`RequiresAdminRole`/`RequiresRunRole`), while nearly every other mutating route in the same function is wrapped.

### Title
Missing role authorization on `PATCH /v2/user/password` and `POST /v2/user/token*` routes allows any authenticated view-only user to change credentials/API tokens - (File: core/web/router.go)

### Summary
In `core/web/router.go`, the route group `v2Routes` wraps nearly all state-mutating endpoints with an explicit role check (`auth.RequiresEditRole`, `auth.RequiresAdminRole`, or `auth.RequiresRunRole`). However, `authv2.PATCH("/user/password", uc.UpdatePassword)`, `authv2.POST("/user/token", uc.NewAPIToken)`, and `authv2.POST("/user/token/delete", uc.DeleteAPIToken)` are registered with only the base `Authenticate` middleware (session or token auth) and no role gate, unlike sibling admin/edit-role-gated routes such as `/users` (RequiresAdminRole) directly above them.

### Finding Description
`v2Routes` builds an `authv2` group protected by `auth.Authenticate(...)` which only verifies that *some* valid session/token exists, populating `SessionUserKey` with a user of any role (`View`, `Run`, `Edit`, or `Admin`) [1](#0-0) . Immediately after establishing this generically-authenticated group, the router applies `auth.RequiresAdminRole` to `/users` routes but leaves `/user/password`, `/user/token`, and `/user/token/delete` without any `RequiresEditRole`/`RequiresAdminRole` wrapper [2](#0-1) .

The underlying middleware `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` in `core/web/auth/auth.go` exist specifically to reject requests from users whose role is below the required threshold, e.g. `RequiresAdminRole` aborts with 403 for any non-admin [3](#0-2) ; without applying one of these to `UpdatePassword`/`NewAPIToken`/`DeleteAPIToken`, any authenticated principal—including a `UserRoleView` account (read-only, meant to be unprivileged) or an external-initiator-derived session that is force-set to `UserRoleRun` in `AuthenticateExternalInitiator` [4](#0-3) —can reach these handlers. This is structurally the same class of bug as the reported analog: a sensitive mutating action reachable by principals that should not be authorized to invoke it, because the intended access-control modifier/wrapper was omitted from only some of the sibling routes.

### Impact Explanation
`UpdatePassword` changes the node operator's login password and `NewAPIToken`/`DeleteAPIToken` mint or revoke the long-lived API access-key/secret pair used for `X-Chainlink-EA-AccessKey`/token-based authentication (`auth.AuthenticateByToken`) [5](#0-4) . A low-privilege (View-role) authenticated session being able to rotate or delete this credential is a credential/account-takeover-adjacent issue: it can lock out legitimate Edit/Admin users, or (in the API token case) allow the low-privilege caller to mint a fresh API token for the account, effectively escalating its own reachable capability set for subsequent token-authenticated calls.

### Likelihood Explanation
Likelihood is directly proportional to how many low-privilege accounts exist on a node. Chainlink nodes can have `UserRoleView` accounts (created by `RequiresAdminRole`-gated `/v2/users` for auditors/read-only dashboards) which are only supposed to read data, not mutate credentials [6](#0-5)  (the test table shows `/v2/user/password` and `/v2/user/token` marked `viewOnlyAllowed: true` in `routesRolesMap`, confirming this is treated as intentionally permitted for view role in the test expectations—but this is exactly the same posture: any authenticated actor, regardless of role, can hit these endpoints).

### Recommendation
Wrap `/user/password`, `/user/token`, and `/user/token/delete` with an explicit role gate consistent with their sensitivity (e.g., `auth.RequiresEditRole` at minimum, mirroring the treatment of `/keys/*` credential-management routes which are all `RequiresEditRole`/`RequiresAdminRole`-gated), so that `UserRoleView` sessions cannot mutate authentication credentials.

### Proof of Concept
1. Create a `UserRoleView` account via the admin-only `POST /v2/users` endpoint.
2. Authenticate as that user (session cookie) via `POST /v2/sessions`.
3. Send `PATCH /v2/user/password` or `POST /v2/user/token` with the view-role session cookie.
4. Observe the request succeeds (200) because no `RequiresEditRole`/`RequiresAdminRole` wrapper is applied at `core/web/router.go:255-257`, whereas the same session would receive 403 on `/v2/users` (line 251) due to `RequiresAdminRole`.

### Citations

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

**File:** core/web/auth/auth.go (L78-112)
```go
func AuthenticateByToken(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	token := &auth.Token{
		AccessKey: c.GetHeader(APIKey),
		Secret:    c.GetHeader(APISecret),
	}
	if token.AccessKey == "" {
		return auth.ErrorAuthFailed
	}

	if token.Secret == "" {
		return auth.ErrorAuthFailed
	}

	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || errors.Is(err, clsessions.ErrUserSessionExpired) {
			return auth.ErrorAuthFailed
		}
		return err
	}

	ok, err := clsessions.AuthenticateUserByToken(token, &user)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```

**File:** core/web/auth/auth.go (L143-149)
```go
	// External initiator endpoints (wrapped with AuthenticateExternalInitiator) inherently assume the role
	// of 'run' (required to trigger job runs)
	c.Set(SessionExternalInitiatorKey, ei)
	c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})

	return nil
}
```

**File:** core/web/auth/auth.go (L236-253)
```go
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

**File:** core/web/auth/auth_test.go (L219-221)
```go
	{"PATCH", "/v2/user/password", true, true, true},
	{"POST", "/v2/user/token", true, true, true},
	{"POST", "/v2/user/token/delete", true, true, true},
```
