### Title
Sensitive `AuditLogger` forwarding credentials exposed to any authenticated (including view-only) user via `GET /v2/config` - (File: core/web/config_controller.go)

### Summary
The Airflow CVE-2023-46288 class of bug is: a configuration-exposure API that is supposed to redact/exclude sensitive values still leaks them because the exclusion logic is incomplete. Chainlink has an analogous config-dump endpoint, `/v2/config` / `/v2/config/v2`, that dumps the node's full effective TOML configuration to any authenticated user regardless of role, and the redaction of "sensitive" values in that dump is type-based rather than content-based — only fields explicitly typed as `SecretString`/`SecretURL` are masked. Fields that legitimately hold credentials but are not wrapped in those secret types (e.g. `AuditLogger.Headers`, which is documented to carry `Authorization` tokens) are returned in cleartext.

### Finding Description
`ConfigController.Show` serves the node's general (non-secrets) configuration as TOML in response to `GET /v2/config` and `GET /v2/config/v2`: [1](#0-0) 

This route is registered under the generic `authv2` group with only session/token authentication — no `auth.RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` wrapper is applied, unlike most mutating endpoints in the same file: [2](#0-1) 

The project's own RBAC route map explicitly documents that `/v2/config` and `/v2/config/v2` are `viewOnlyAllowed: true`, i.e. reachable by the lowest privilege role: [3](#0-2) 

The node's redaction mechanism only masks fields whose Go type is `config.SecretString` / `config.SecretURL` (rendered as `xxxxx`), which is how `Database.URL` and `Password.Keystore` in `secrets.toml` are protected: [4](#0-3) [5](#0-4) 

However, the value returned by `/v2/config` comes from `ConfigTOML()`, which is the *general* config (not `secrets.toml`), built from `inputTOML`/`effectiveTOML`: [6](#0-5) 

The general config includes `AuditLogger.Headers`, which per the changelog is explicitly designed to carry authorization credentials for the audit-log forwarding webhook, e.g. `AUDIT_LOGGER_HEADERS="Authorization||{{token}}"`: [7](#0-6)  and is rendered verbatim (not the `Secret` type) in effective-config test fixtures, e.g. `Headers = ['Authorization: token', ...]`: [8](#0-7) 

Because `Headers` is a plain `[]string` field (not `SecretString`), it is not redacted by the TOML marshaler's secret-masking logic and is returned in full to any authenticated user who calls `GET /v2/config`, including a `view`-role user.

### Impact Explanation
A user with only the lowest ("view") role — who is intended to have read-only, non-administrative access — can retrieve the node's `AuditLogger.Headers`, which may contain an `Authorization` bearer token or API key used to authenticate to the external audit-log forwarding endpoint. This credential can be replayed against that external system, or used to impersonate the node's audit forwarder, i.e. credential/secret disclosure to an under-privileged authenticated actor — directly analogous to the Airflow "non-sensitive-only" config leak.

### Likelihood Explanation
Likelihood depends on whether an operator has actually configured `AuditLogger.Headers` (or another similarly plaintext-but-sensitive general-config field) with a live credential — this is an opt-in feature (`AuditLogger.Enabled`), so exposure only manifests in deployments using the audit-forwarding feature with an `Authorization` header. Any node operator who follows the documented example (`AUDIT_LOGGER_HEADERS="Authorization||{{token}}"`) is affected, and exploitation requires only a valid low-privilege session/API token, which is a normal, unprivileged authenticated capability in multi-user Chainlink nodes.

### Recommendation
Wrap `AuditLogger.Headers` (and audit any other general-config field capable of holding credentials, e.g. webhook URLs with embedded basic-auth) in the existing `config.SecretString`/`config.SecretURL` type so it is redacted by the TOML marshaler exactly like `Database.URL`/`Password.Keystore`. Alternatively, restrict `GET /v2/config` and `/v2/config/v2` to `RequiresAdminRole` (or at minimum `RequiresEditRole`), consistent with how other configuration-mutating/sensitive endpoints are gated.

### Proof of Concept
1. Configure a node with `[AuditLogger] Enabled = true`, `Headers = ['Authorization: Bearer supersecrettoken']`.
2. Create/obtain a session or API token for a user with `Role = view`.
3. Call `GET /v2/config` (or `/v2/config/v2?userOnly=true`) with that low-privilege credential.
4. Observe the response JSON (`ConfigV2Resource.Config`) contains the `[AuditLogger] Headers = ['Authorization: Bearer supersecrettoken']` line in cleartext, disclosing the credential to a user who should not have visibility into it.

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

**File:** core/web/router.go (L283-286)
```go
		cc := ConfigController{app}
		authv2.GET("/config", cc.Show)
		authv2.GET("/config/v2", cc.Show)

```

**File:** core/web/auth/auth_test.go (L236-237)
```go
	{"GET", "/v2/config", true, true, true},
	{"GET", "/v2/config/v2", true, true, true},
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

**File:** core/services/chainlink/config.go (L448-455)
```go
// TOMLString returns a TOML encoded string with secret values redacted.
func (s *Secrets) TOMLString() (string, error) {
	b, err := gotoml.Marshal(s)
	if err != nil {
		return "", err
	}
	return string(b), nil
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

**File:** CHANGELOG.md (L3014-3026)
```markdown
When set, this environment variable configures and enables an optional HTTP logger which is used specifically to send audit log events. Audit logs events are emitted when specific actions are performed by any of the users through the node's API. The value of this variable should be a full URL. Log items will be sent via POST

There are audit log implemented for the following events:

- Auth & Sessions (new session, login success, login failed, 2FA enrolled, 2FA failed, password reset, password reset failed, etc.)
- CRUD actions for all resources (add/create/delete resources such as bridges, nodes, keys)
- Sensitive actions (keys exported/imported, config changed, log level changed, environment dumped)

A full list of audit log enum types can be found in the source within the `audit` package (`audit_types.go`).

The following `AUDIT_LOGGER_*` environment variables below configure this optional audit log HTTP forwarder.

##### AUDIT_LOGGER_HEADERS
```

**File:** core/web/resolver/testdata/config-full.toml (L54-58)
```text
[AuditLogger]
Enabled = true
ForwardToUrl = 'http://localhost:9898'
JsonWrapperKey = 'event'
Headers = ['Authorization: token', 'X-SomeOther-Header: value with spaces | and a bar+*']
```
