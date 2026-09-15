Audit Report

## Title
Unprivileged authenticated node users (View role) can disclose RPC provider credentials embedded in node configuration via `/v2/config` - (File: core/web/router.go, core/web/config_controller.go)

## Summary
`GET /v2/config` and `GET /v2/config/v2` are registered in the authenticated router group with no role-gating middleware, unlike every other sensitive endpoint in the same file (`bridge_types`, `external_initiators`, `transfers`, `users`, etc.), which are wrapped with `auth.RequiresEditRole` or `auth.RequiresAdminRole`. Any authenticated user, including one provisioned with the lowest-privilege `view` role, can call this endpoint to retrieve the node's full effective/input TOML configuration, which frequently includes RPC provider URLs (`EVM.Nodes[].WSURL`/`HTTPURL`) with embedded API keys.

## Finding Description
The route registration confirms the missing role check: [1](#0-0) 

Compare this to the immediately surrounding routes in the same block, all of which use `auth.RequiresEditRole` or `auth.RequiresAdminRole`: [2](#0-1) 

The `auth.RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` middleware implementations confirm that `view`-role users are the lowest tier and are explicitly blocked from `run`/`edit`/`admin`-gated routes, but `/config` has no such wrapper applied at all — only the base `auth.Authenticate` (session or token) is enforced: [3](#0-2) 

The handler returns the full input/effective configuration TOML with no field-level filtering: [4](#0-3) 

Only `Secrets` (DB URL, keystore password) are redacted via `Secrets.TOMLString()`; ordinary `Config` fields such as `EVM.Nodes[].WSURL`/`HTTPURL` are not part of `Secrets` and are serialized unfiltered by `ConfigTOML()`, so any embedded provider API key in those URLs is exposed as-is.

## Impact Explanation
This is a genuine authorization gap: a `view`-role authenticated API user — a role that is supposed to be restricted from write/administrative operations — can read the node's full configuration TOML, including RPC endpoint URLs that commonly embed third-party API keys (Alchemy/Infura/QuickNode-style URLs), OIDC client IDs, and other operator-supplied values. This maps to the in-scope "key/secret exfiltration" impact category: an unprivileged (relative to admin) but authenticated actor can exfiltrate credentials that were not intended for their privilege tier, enabling unauthorized consumption of the operator's third-party API quota/credits and potential DoS via rate-limit exhaustion.

## Likelihood Explanation
High. Exploitation requires only that a `view`-role API user/session exist (a normal, expected low-privilege account type per the node's own role model) and a single unauthenticated-role-but-authenticated `GET /v2/config` request — no admin or edit privileges, no additional exploitation steps, and no reliance on host/DB access. This is fully within the "unprivileged authenticated actor" threat model applicable to node API role-bypass findings.

## Recommendation
- Wrap `authv2.GET("/config", cc.Show)` and `authv2.GET("/config/v2", cc.Show)` with `auth.RequiresAdminRole` (or, at minimum, `auth.RequiresEditRole`), consistent with the role-gating pattern used for other sensitive configuration/management routes in `core/web/router.go`.
- Additionally consider redacting known-sensitive substrings (e.g., query-string API keys) from `WSURL`/`HTTPURL` before serialization in `ConfigTOML()`, since even `edit`/`admin` users' exposure to raw provider keys may be undesirable from an operational-security standpoint (though that is a secondary hardening measure beyond the core role-check fix).

## Proof of Concept
1. Configure a node with `[[EVM.Nodes]]` `HTTPURL = 'https://eth-mainnet.g.alchemy.com/v2/<API_KEY>'`.
2. As an admin, create an API user with role `view` (`POST /v2/users` with `role=view`), which is permitted by the existing admin-only user-management routes: [5](#0-4) 
3. Authenticate as the `view` user (session cookie or `X-API-KEY`/`X-API-SECRET` token) and call `GET /v2/config`.
4. Observe that the JSON response's `config` field contains the full TOML, including the `[[EVM.Nodes]]` block with the embedded API key, confirmed by the unguarded handler at [4](#0-3)  — no `403 Forbidden`/`401` is returned, unlike calling e.g. `POST /v2/bridge_types` as the same `view` user, which is blocked by `auth.RequiresEditRole`.

**Note on residual uncertainty**: The full `routesRolesMap` table in `core/web/auth/auth_test.go` (which encodes intended role expectations per route for test coverage) could not be retrieved in this session due to search/tooling limits — I was only able to confirm the route wiring in `router.go` and the middleware definitions in `auth.go`, not whether a route-role expectation test exists and is passing/failing for `/config`. This does not change the conclusion, since the router wiring itself is unambiguous evidence of the missing role check, but a full review of `auth_test.go`'s route table would further corroborate whether this was a known gap already tracked by the test suite.

### Citations

**File:** core/web/router.go (L250-254)
```go
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
```

**File:** core/web/router.go (L263-281)
```go
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
