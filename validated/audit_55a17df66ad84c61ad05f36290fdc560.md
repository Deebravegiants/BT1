### Title
Missing role-based authorization on `/v2/config` allows any authenticated user (including lowest-privilege `view` role) to read the full node configuration - ([File: core/web/router.go])

### Summary
The Jenkins PRQA CVE is a class of "sensitive configuration disclosed to an actor who should not have access to it." The closest reachable analog in this codebase is the `ConfigController.Show` handler, registered without any role gate, unlike virtually every other sensitive route in the router.

### Finding Description
In `core/web/router.go`, the `/v2/config` and `/v2/config/v2` routes are registered only inside the `authv2` group, which requires session/token authentication via `auth.Authenticate`, but they are **not** wrapped in any of the role-escalation middlewares (`auth.RequiresRunRole`, `auth.RequiresEditRole`, `auth.RequiresAdminRole`) that guard nearly every other operational endpoint in the same block (e.g. key export, transfers, bridge/job mutation): [1](#0-0) 

Compare this to adjacent routes such as key export or transfers, which are explicitly `RequiresAdminRole`: [2](#0-1) 

The handler itself returns the full effective (or user-supplied) TOML configuration to any caller that reaches it: [3](#0-2) 

The role hierarchy in this codebase is `view < run < edit < admin`, and `view` is explicitly the lowest-privilege, read-only role: [4](#0-3) 

The RBAC test suite (`TestRBAC_Routemap_ViewOnly`, `TestRBAC_Routemap_Run`) demonstrates that the codebase's intended pattern is to explicitly enumerate which routes are safe for `view`/`run` roles via a `routesRolesMap` and assert `Forbidden`/`Unauthorized` for the rest: [5](#0-4) 

Because `/v2/config` has no role check at all (not even `RequiresRunRole`), a `view`-role user (or any authenticated API token) can retrieve the full effective node configuration, which is intended to be an operationally sensitive artifact — I was not able to fully verify within the available index whether operational values embedded in the effective config (e.g., chain RPC node URLs that commonly embed provider API keys as URL path segments) are included in `ConfigTOML()`'s output, since `Database`, `Password`, `WebServer.LDAP/OIDC`, and `Mercury.Credentials` are stored in the separate `Secrets` struct/`secrets.toml` and are not part of `g.inputTOML`/`g.effectiveTOML` per `core/services/chainlink/config_general.go`: [6](#0-5) 

### Impact Explanation
If the effective/user config includes any sensitive operational data outside the `Secrets` struct (e.g., RPC/node URLs with embedded provider credentials, or other non-`SecretString`-wrapped fields), a `view`-role or otherwise minimally-privileged authenticated user could read the entire node configuration via a single unauthenticated-for-role GET request, which contradicts the codebase's own RBAC design intent (most sensitive reads/exports require `edit` or `admin`). This is analogous to the CVE class: sensitive configuration disclosed to an actor without the privilege level normally required for such data.

### Likelihood Explanation
Likelihood is moderate-to-uncertain: exploitation requires only a valid session or API token of any role (including the lowest `view` role, which is often issued broadly for dashboards/monitoring), and no additional privilege is needed to hit `GET /v2/config` or `/v2/config/v2`. However, the actual sensitivity of the disclosed data depends on what remains in `Config` outside the `Secrets` struct, which I could not conclusively enumerate from the indexed code.

### Recommendation
Gate `/v2/config` and `/v2/config/v2` behind at minimum `auth.RequiresEditRole` (matching the sensitivity level applied to other config/key-adjacent routes), and audit all fields serialized via `ConfigTOML()` to ensure no operationally sensitive values (e.g., RPC URLs with embedded API keys) are present outside the already-redacted `Secrets`/`SecretString` types.

### Proof of Concept
1. Provision a user with `UserRoleView` (lowest role) or an API token scoped to `view`.
2. Authenticate and call `GET /v2/config/v2?userOnly=false`.
3. Observe the endpoint returns HTTP 200 with the full effective TOML configuration, since `authv2.GET("/config/v2", cc.Show)` has no role middleware, unlike other sensitive `authv2` routes.

### Citations

**File:** core/web/router.go (L283-285)
```go
		cc := ConfigController{app}
		authv2.GET("/config", cc.Show)
		authv2.GET("/config/v2", cc.Show)
```

**File:** core/web/router.go (L312-320)
```go
		authv2.POST("/keys/csa/import", auth.RequiresAdminRole(csakc.Import))
		authv2.POST("/keys/csa/export/:ID", auth.RequiresAdminRole(csakc.Export))

		ekc := NewETHKeysController(app)
		authv2.GET("/keys/eth", ekc.Index)
		authv2.POST("/keys/eth", auth.RequiresEditRole(ekc.Create))
		authv2.DELETE("/keys/eth/:keyID", auth.RequiresAdminRole(ekc.Delete))
		authv2.POST("/keys/eth/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/eth/export/:address", auth.RequiresAdminRole(ekc.Export))
```

**File:** core/web/config_controller.go (L23-42)
```go
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

**File:** core/sessions/user.go (L29-34)
```go
const (
	UserRoleAdmin UserRole = "admin"
	UserRoleEdit  UserRole = "edit"
	UserRoleRun   UserRole = "run"
	UserRoleView  UserRole = "view"
)
```

**File:** core/web/auth/auth_test.go (L484-530)
```go
func TestRBAC_Routemap_ViewOnly(t *testing.T) {
	t.Parallel()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(t.Context()))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	// Create a test run user to work with
	u := &cltest.User{Role: sessions.UserRoleView}
	client := app.NewHTTPClient(u)

	// Assert all view only routes
	for i, route := range routesRolesMap {
		t.Run(fmt.Sprintf("%d-%s-%s", i, route.verb, route.path), func(t *testing.T) {
			t.Parallel()
			var resp *http.Response
			var cleanup func()

			switch route.verb {
			case "GET":
				resp, cleanup = client.Get(route.path)
			case "POST":
				resp, cleanup = client.Post(route.path, nil)
			case "DELETE":
				resp, cleanup = client.Delete(route.path)
			case "PATCH":
				resp, cleanup = client.Patch(route.path, nil)
			case "PUT":
				resp, cleanup = client.Put(route.path, nil)
			default:
				t.Fatalf("Unknown HTTP verb %s\n", route.verb)
			}
			defer cleanup()

			// If this route only allows view only, don't expect an unauthorized response
			switch {
			case route.viewOnlyAllowed:
				assert.NotEqual(t, http.StatusUnauthorized, resp.StatusCode)
				assert.NotEqual(t, http.StatusForbidden, resp.StatusCode)
			case !route.EditAllowed:
				assert.Equal(t, http.StatusForbidden, resp.StatusCode)
			default:
				assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
			}
		})
```

**File:** core/services/chainlink/config_general.go (L278-290)
```go
func (g *generalConfig) LogConfiguration(log, warn coreconfig.LogfFn) {
	log("# Secrets:\n%s\n", g.secretsTOML)
	log("# Input Configuration:\n%s\n", g.inputTOML)
	log("# Effective Configuration, with defaults applied:\n%s\n", g.effectiveTOML)
	if g.warning != nil {
		warn("# Configuration warning:\n%s\n", g.warning)
	}
}

// ConfigTOML implements chainlink.ConfigV2
func (g *generalConfig) ConfigTOML() (user, effective string) {
	return g.inputTOML, g.effectiveTOML
}
```
