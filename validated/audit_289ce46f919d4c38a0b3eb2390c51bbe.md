### Title
Missing role-based permission check on `/v2/config` allows any authenticated user (including lowest "View" role) to read full node configuration - ([File: core/web/config_controller.go])

### Summary
The Jenkins CVE describes a missing permission check that lets a lower-privileged actor (Computer/Create without Computer/Extended Read) perform an action that discloses sensitive agent configuration. The Chainlink analog is the `/v2/config` route, which is the only sensitive read-side node-configuration endpoint in `v2Routes` that is registered with **no** `auth.RequiresRunRole` / `RequiresEditRole` / `RequiresAdminRole` wrapper, unlike virtually every other sensitive endpoint (keys, users, transfers, jobs, etc.).

### Finding Description
`ConfigController.Show` returns the node's full effective (or user-supplied) TOML configuration: [1](#0-0) 

It is wired into the router without any role-check middleware, while every other route touching configuration/secrets in the same file is gated behind at least `RequiresEditRole` or `RequiresAdminRole`: [2](#0-1) 

Compare this to the surrounding routes, all of which explicitly enforce elevated roles for anything security-sensitive (keys, users, transfers): [3](#0-2) 

The role hierarchy itself is `View < Run < Edit < Admin`, enforced via `RequiresRunRole`, `RequiresEditRole`, and `RequiresAdminRole` helpers: [4](#0-3) 

Because `/v2/config` sits only behind the generic `Authenticate` middleware (session or API token) and has no role assertion, **any** authenticated user — even one provisioned with the minimal `View` role, which is meant only for read-only dashboards — can pull the complete node TOML configuration (chain RPC endpoints, database/queue tuning, feature flags, and any other fields serialized by `ConfigTOML()`), mirroring the Jenkins pattern where a technically-permitted but under-privileged actor obtains configuration data intended to require a higher/extended permission.

I was not able to fully verify from the indexed code whether `ConfigTOML()` (in `core/services/chainlink/config_general.go`) redacts every secret-tagged field before serialization — I could only locate the function signature, not its full redaction logic, before running out of search iterations. This is a material uncertainty: if redaction is complete, the impact is limited to unauthorized visibility into non-secret configuration (still a role-bypass); if any field is missed by the redaction logic, this becomes a direct secret-disclosure issue.

### Impact Explanation
At minimum, this is a role/permission-check bypass: a `View`-role user (the lowest privilege tier, analogous to Jenkins' unprivileged Computer/Create actor) can read data that the codebase's own RBAC model treats as sensitive everywhere else (config-adjacent operations like key export/import/chain updates all require `Edit`/`Admin`). If the TOML redaction is incomplete for any config field, the impact escalates to secret disclosure.

### Likelihood Explanation
High likelihood of reachability: the endpoint is reachable by any authenticated user via a simple `GET /v2/config` request, with no additional role check, and is exercised directly in RBAC tests without expecting a `Forbidden` response for lower roles: [5](#0-4) 

### Recommendation
Wrap `authv2.GET("/config", cc.Show)` (and `/config/v2`) with an explicit role check (at minimum `auth.RequiresEditRole`, matching the sensitivity of other configuration-mutating routes), and audit `ConfigTOML()`'s redaction coverage to confirm all secret-tagged fields are stripped before being returned to any role, including `Edit`/`Admin`, to defend in depth.

### Proof of Concept
1. Create a user with the `View` role: `POST /v2/users` (as admin) with role `view`.
2. Authenticate as that user (session cookie or API token).
3. Issue `GET /v2/config` (or `/v2/config/v2`).
4. Observe the request succeeds (HTTP 200) and returns the full node TOML — no `403 Forbidden` is returned, unlike other sensitive routes gated by `RequiresEditRole`/`RequiresAdminRole`. [2](#0-1) [1](#0-0)

### Citations

**File:** core/web/config_controller.go (L19-42)
```go
// Show returns the whitelist of config variables
// Example:
//
//	"<application>/config"
func (cc *ConfigController) Show(c *gin.Context) {
	cfg := cc.App.GetConfig()
	var userOnly bool
	if s, has := c.GetQuery("userOnly"); has {
		var err error
		userOnly, err = strconv.ParseBool(s)
		if err != nil {
			jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("invalid bool for userOnly: %w", err))
			return
		}
	}
	var toml string
	user, effective := cfg.ConfigTOML()
	if userOnly {
		toml = user
	} else {
		toml = effective
	}
	jsonAPIResponse(c, ConfigV2Resource{toml}, "config")
}
```

**File:** core/web/router.go (L250-282)
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

```

**File:** core/web/router.go (L283-285)
```go
		cc := ConfigController{app}
		authv2.GET("/config", cc.Show)
		authv2.GET("/config/v2", cc.Show)
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

**File:** core/web/auth/auth_test.go (L236-237)
```go
	{"GET", "/v2/config", true, true, true},
	{"GET", "/v2/config/v2", true, true, true},
```
