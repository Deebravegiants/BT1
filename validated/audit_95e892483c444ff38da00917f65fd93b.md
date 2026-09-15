Audit Report

## Title
Missing role-based permission check on `/v2/config` and `/v2/config/v2` allows any authenticated user, including the lowest "View" role, to read full node configuration - ([File: core/web/router.go])

## Summary
The `ConfigController.Show` handler is registered in `v2Routes` behind only the generic `auth.Authenticate` middleware, with no `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` wrapper, unlike every other configuration-related route in the same router setup. This lets any authenticated user, including one with the minimal `View` role, retrieve the node's full effective/user TOML configuration.

## Finding Description
`ConfigController.Show` reads the node's config via `cfg.ConfigTOML()` and returns either the user-supplied or effective TOML depending on the `userOnly` query parameter: [1](#0-0) 

In `v2Routes`, the route is registered with no role check at all: [2](#0-1) 

This is inconsistent with essentially every other sensitive route registered in the same function/group, which is wrapped in `auth.RequiresEditRole` or `auth.RequiresAdminRole`: [3](#0-2) 

The `authv2` route group itself only enforces authentication (session or API token), not any minimum role: [4](#0-3) 

The role hierarchy (`View < Run < Edit < Admin`) and its enforcement helpers are defined explicitly, confirming `View` is treated as the lowest, read-only-dashboard tier everywhere else: [5](#0-4) 

The existing RBAC test suite confirms the observed behavior — `/v2/config` and `/v2/config/v2` are expected to succeed for all three privilege tiers (`view`, `run`, `edit`) with no forbidden response, unlike admin/edit-gated routes: [6](#0-5) 

Note that `ConfigTOML()` returns the non-secret `Config` object serialized to TOML (`user`/`effective`), while secrets are tracked in a separate `secretsTOML` field on `generalConfig` and are not part of what `Show` returns: [7](#0-6) 
This confirms the disclosed data is limited to non-secret configuration (chain RPC endpoints, tuning parameters, feature flags, etc.), not credentials/secrets — the report's own uncertainty about "incomplete redaction" is not corroborated because secrets never flow through the returned config in the first place.

## Impact Explanation
This is a genuine authorization-model inconsistency: a `View`-role user, the tier explicitly intended for read-only dashboards, can access an endpoint that reveals full node configuration (RPC URLs, DB/queue tuning, feature flags) which every architecturally-similar endpoint (keys, users, bridges, transfers, external initiators) requires `Edit` or `Admin` to touch. This maps to the in-scope "node API ... role bypass" impact category. However, the disclosed data does not include secrets (those live in the separate `secretsTOML`/`Secrets` struct, not `ConfigTOML()`), so the practical severity is configuration-disclosure/role-inconsistency rather than secret exfiltration.

## Likelihood Explanation
High likelihood/trivial reachability: any authenticated user (including the lowest `View` role, obtainable via normal `/v2/users` provisioning by an admin, or via an API token for such a user) can issue `GET /v2/config` and receive a 200 response with the full TOML, with no additional role check standing in the way, as directly confirmed by the router wiring and the existing RBAC test expectations.

## Recommendation
Wrap `authv2.GET("/config", cc.Show)` and `authv2.GET("/config/v2", cc.Show)` with at least `auth.RequiresEditRole` (or `RequiresRunRole` at minimum) to match the sensitivity level applied to other configuration-adjacent routes, restoring consistency with the rest of the RBAC model.

## Proof of Concept
1. As an admin, create a user with the `View` role via `POST /v2/users`.
2. Authenticate as that user (session cookie or API token).
3. Issue `GET /v2/config` or `GET /v2/config/v2`.
4. Observe HTTP 200 with the full node TOML configuration returned, with no `403 Forbidden`, confirmed by the router registration in `core/web/router.go` lines 283-285 and the RBAC table entry in `core/web/auth/auth_test.go` lines 236-237 expecting success (`true, true, true`) across `view/run/edit` roles for this route, unlike admin/edit-gated routes in the same table.

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

**File:** core/web/router.go (L245-249)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	{
```

**File:** core/web/router.go (L250-279)
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

**File:** core/services/chainlink/config_general.go (L28-46)
```go
// generalConfig is a wrapper to adapt Config to the config.GeneralConfig interface.
type generalConfig struct {
	inputTOML     string // user input, normalized via de/re-serialization
	effectiveTOML string // with default values included
	secretsTOML   string // with env overrides includes, redacted

	c       *Config // all fields non-nil (unless the legacy method signature return a pointer)
	secrets *Secrets

	warning error // warnings about inputTOML, e.g. deprecated fields

	logLevelDefault zapcore.Level

	appIDOnce sync.Once

	logMu sync.RWMutex // for the mutable fields Log.Level & Log.SQL

	passwordMu sync.RWMutex // passwords are set after initialization
}
```
