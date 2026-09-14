## Finding [1](#0-0) 

### Title
Config endpoint exposes plaintext RPC endpoint credentials (embedded provider API keys) to lowest-privileged "View" role users - ([File: core/web/config_controller.go])

### Summary
The Grafana Tempo advisory describes a `/status/config` endpoint that returns the full effective configuration in plaintext, including a sensitive S3 SSE-C encryption key that should never be readable by unauthorized/low-trust callers. Chainlink has a structurally identical pattern: the `GET /v2/config` (and `/v2/config/v2`) endpoint dumps the node's full effective/user TOML configuration, and that configuration deliberately keeps `EVM.Nodes[].HTTPURL`/`WSURL` (and equivalent RPC URL fields for other chains) as plain, unredacted strings rather than `SecretURL`. Since RPC provider URLs commonly embed API keys/auth tokens directly in the path or query string (e.g. `https://mainnet.infura.io/v3/<API_KEY>`), this endpoint discloses those credentials in plaintext to any authenticated caller — including the lowest-privileged `View` role, which is not blocked by any role check on this route.

### Finding Description
The `ConfigController.Show` handler returns the node's TOML configuration (user or effective) directly to the caller: [2](#0-1) 

This handler is registered in the router with only generic authentication middleware and no role gate: [3](#0-2) 

Compare this to nearby routes on the same router group that explicitly wrap handlers with `auth.RequiresEditRole`/`auth.RequiresAdminRole` (e.g. bridge types, transfers, key management) — `cc.Show` has no such wrapper, so any authenticated session/token — even a `UserRoleView` account, the lowest role tier — can call it: [4](#0-3) 

The returned TOML is produced by `generalConfig.ConfigTOML()`, which returns `inputTOML`/`effectiveTOML` — distinct from the separately-redacted `secretsTOML`: [5](#0-4) 

Only fields modeled with `models.SecretURL`/`config.SecretString` are redacted to `xxxxx` on marshal, as seen for `Database.URL`, `Password.Keystore`, etc.: [6](#0-5) [7](#0-6) 

However, `EVM.Nodes[].HTTPURL`/`WSURL` are ordinary strings, not `SecretURL`, and are shown verbatim in the effective configuration output returned by both the CLI validate command and, identically, the `/v2/config` endpoint: [8](#0-7) [9](#0-8) 

Since operators commonly configure RPC providers using URLs with embedded API keys (a widely-used pattern for Infura/Alchemy/QuickNode/etc.), those keys are returned in plaintext by an endpoint reachable by the least-privileged role.

### Impact Explanation
A user provisioned with only the `View` role (intended for read-only dashboard access, not administrative or credential access) can call `GET /v2/config` and obtain the node's full effective configuration, including any RPC provider URLs with embedded API keys, LDAP/OIDC endpoint hints, and other operational details that were never modeled as secrets. This mirrors the Tempo class of bug: a config/status introspection endpoint unintentionally serves security-sensitive material to a caller that should not be trusted with it, enabling credential theft (e.g., theft of a paid RPC provider's API key, leading to quota abuse or billing fraud against the node operator) without requiring any elevated privilege or admin token.

### Likelihood Explanation
High. No special conditions are needed beyond obtaining any valid session or API token with the default/lowest `View` role (a role explicitly designed to be handed to less-trusted users), and then issuing a single unauthenticated-role-gated `GET /v2/config` request. The endpoint has been reachable this way since role checks were added to sibling routes but omitted here.

### Recommendation
- Wrap the `/v2/config` and `/v2/config/v2` routes with at minimum `auth.RequiresAdminRole` (or `RequiresEditRole` if operational tooling for lower roles is required), consistent with other sensitive routes in `v2Routes`.
- Change `EVM.Nodes[].HTTPURL`/`WSURL` (and analogous RPC URL fields for other chains, e.g. Starknet `URL`/`APIKey`, Cosmos/Solana node URLs) to use `commonconfig.SecretURL`/`SecretString` so any embedded credentials are redacted the same way `Database.URL` is, independent of endpoint access control.
- Audit `ConfigTOML()`/`generalConfig` for any other plain-string fields that may carry credentials by convention (URLs, headers) and enforce redaction at the type level rather than relying solely on endpoint-level authorization.

### Proof of Concept
1. Create/obtain a user with `UserRoleView` (lowest role) via normal node user management.
2. Authenticate as that user (session cookie or API token).
3. Send `GET /v2/config/v2` (or `/v2/config`).
4. Observe the JSON response's `config` field contains the effective TOML with `EVM.Nodes[].HTTPURL`/`WSURL` in plaintext, e.g. `HTTPURL = 'https://mainnet.infura.io/v3/<REDACTED_BY_OPERATOR_BUT_NOT_BY_CODE>'`, exposing the embedded provider API key to a low-privilege caller.

### Citations

**File:** core/web/router.go (L245-285)
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

		cc := ConfigController{app}
		authv2.GET("/config", cc.Show)
		authv2.GET("/config/v2", cc.Show)
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

**File:** core/store/models/secrets.go (L7-19)
```go
// Secret is a string that formats and encodes redacted, as "xxxxx".
// Deprecated
type Secret = config.SecretString

// Deprecated
func NewSecret(s string) *Secret { return config.NewSecretString(s) }

// SecretURL is a URL that formats and encodes redacted, as "xxxxx".
// Deprecated
type SecretURL = config.SecretURL

// Deprecated
func NewSecretURL(u *config.URL) *config.SecretURL { return (*config.SecretURL)(u) }
```

**File:** testdata/scripts/node/validate/valid.txtar (L32-39)
```text
-- out.txt --
# Secrets:
[Database]
URL = 'xxxxx'
AllowSimplePasswords = false

[Password]
Keystore = 'xxxxx'
```

**File:** testdata/scripts/nodes/evm/list/list.txtar (L31-40)
```text
[[EVM.Nodes]]
Name = 'Blue'
WSURL = 'wss://primaryfoo.bar/ws'
HTTPURL = 'https://primaryfoo.bar'

[[EVM.Nodes]]
Name = 'Yellow'
WSURL = 'wss://sendonlyfoo.bar/ws'
HTTPURL = 'https://sendonlyfoo.bar'
SendOnly = true
```

**File:** core/config/docs/chains-evm.toml (L572-588)
```text
[[EVM.Nodes]]
# Name is a unique (per-chain) identifier for this node.
Name = 'foo' # Example
# WSURL is the WS(S) endpoint for this node. Required for primary nodes when `LogBroadcasterEnabled` is `true`
WSURL = 'wss://web.socket/test' # Example
# HTTPURL is the HTTP(S) endpoint for this node. Required for all nodes.
HTTPURL = 'https://foo.web' # Example
# HTTPURLExtraWrite is the HTTP(S) endpoint used for chains that require a separate endpoint for writing on-chain.
HTTPURLExtraWrite = 'https://foo.web/extra' # Example
# SendOnly limits usage to sending transaction broadcasts only. With this enabled, only HTTPURL is required, and WSURL is not used.
SendOnly = false # Default
# Order of the node in the pool, will takes effect if `SelectionMode` is `PriorityLevel` or will be used as a tie-breaker for `HighestHead` and `TotalDifficulty`
Order = 100 # Default
# IsLoadBalancedRPC indicates whether the http/ws url above has multiple rpc's behind it.
# If true, we should try reconnecting to the node even when its the only node in the Nodes list.
# If false and its the only node in the nodes list, we will mark it alive even when its out of sync, because it might still be able to send txs.
IsLoadBalancedRPC = false # Default
```
