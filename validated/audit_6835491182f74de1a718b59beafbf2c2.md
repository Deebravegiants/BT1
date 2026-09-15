Confirmed the root cause: `AuditLogger.Headers` (`toml.AuditLogger.Headers`, type `models.ServiceHeaders` in `core/config/toml/types.go`) is a plain, unredacted `[]string` field that is part of the main `Config` struct — not `Secrets`. It commonly carries an `Authorization: <token>` value used to authenticate outbound audit-log POST requests, as documented in `docs/CONFIG.md:397-401` and used at `core/logger/audit/audit_logger.go:235-237` where `req.Header.Add(header.Header, header.Value)`. Unlike `models.Secret`/`SecretString` (which marshal as `xxxxx`, see `core/store/models/secrets.go:7-12`), this field has no redaction wrapper.

This value is exposed via `GET /v2/config` (`core/web/config_controller.go:23-42`, `ConfigController.Show`), which calls `cfg.ConfigTOML()` (`core/services/chainlink/config_general.go:288-290`) returning the raw `inputTOML`/`effectiveTOML` — the same TOML blob containing `[AuditLogger] Headers = [...]`. Per the RBAC test map, this route is accessible to **any authenticated role including view-only** (`core/web/auth/auth_test.go:236`: `{"GET", "/v2/config", true, true, true}` — `viewOnlyAllowed=true`), and is served over plain HTTP unless the operator explicitly configures TLS/HTTPS.

This is a direct analog to the Kylin advisory: a "show config" API exposes an in-transit credential (an `Authorization` header value) to any authenticated user regardless of privilege level, and if the endpoint is accessed over HTTP, the token is exposed to network sniffers exactly as described in the report.

### Title
Audit Logger `Authorization` Header Credential Exposed via Unprivileged `/v2/config` Endpoint - (File: core/web/config_controller.go)

### Summary
The `AuditLogger.Headers` configuration field, which typically contains an `Authorization` bearer token used to authenticate outbound audit-log HTTP requests, is stored unredacted as part of the general node `Config` (not `Secrets`) and is returned in full by the `GET /v2/config` API endpoint to any authenticated user, including users with the lowest ("view") role.

### Finding Description
Chainlink's configuration system separates sensitive values into a dedicated `Secrets` struct (`core/services/chainlink/config.go`) whose fields use `models.Secret`/`SecretString` wrapper types that always marshal as `xxxxx` (`core/store/models/secrets.go:7-12`), ensuring credentials like DB passwords, keystore passwords, and OIDC client secrets are redacted anywhere the config is serialized or logged.

However, `AuditLogger.Headers` (`core/config/toml/types.go`, wired through `core/services/chainlink/config_audit_logger.go:33-35`) lives in the non-secret `Config` struct as a plain `models.ServiceHeaders` (`[]string`-like) type with no redaction. Its documented purpose is to carry credential material: `docs/CONFIG.md:397-401` gives the canonical example `Headers = ['Authorization: token', ...]`, and `core/logger/audit/audit_logger.go:235-237` shows this header is added verbatim to every outbound audit-log HTTP request (`req.Header.Add(header.Header, header.Value)`).

`ConfigController.Show` (`core/web/config_controller.go:23-42`) serves the full effective (or user-input) config TOML — including the `[AuditLogger]` section with its `Headers` values — via `cfg.ConfigTOML()` (`core/services/chainlink/config_general.go:288-290`). This route is registered at `authv2.GET("/config", cc.Show)` (`core/web/router.go:284`) inside the generic authenticated group that only requires *any* valid session or API token — no role check (`auth.RequiresEditRole`/`auth.RequiresAdminRole`) is applied. The RBAC test suite confirms this explicitly: `{"GET", "/v2/config", true, true, true}` in `core/web/auth/auth_test.go:236` marks the route as `viewOnlyAllowed`, meaning the lowest-privilege `UserRoleView` role (or any API token scoped similarly) can retrieve it.

### Impact Explanation
Any authenticated node user — even one restricted to read-only/view access, which is the intended low-trust tier for dashboards/monitoring — can retrieve the operator's outbound audit-logging `Authorization` credential via a simple GET request. That token can then be used to impersonate the node when POSTing forged/fabricated audit events to the configured `ForwardToUrl` SIEM/logging endpoint, or, if the token is reused elsewhere (a common operational practice), to access whatever other system the token was issued for. This is a credential-disclosure/impersonation vector reachable purely through the node's own authenticated API with the minimum privilege level.

### Likelihood Explanation
Exploitation requires only: (1) `AuditLogger` enabled with an `Authorization` header configured (a documented, explicitly recommended pattern in `CONFIG.md`), and (2) any valid session/API-token credential of the lowest role. No additional privilege escalation, admin access, or network position is needed — a single authenticated GET request to `/v2/config` suffices, making this trivially reachable for any user or leaked low-privilege API token.

### Recommendation
Redact the `AuditLogger.Headers` values (or at minimum header values that look like `Authorization`/credential-bearing headers) before they are included in `ConfigTOML()`/`LogConfiguration()` output, mirroring the `models.Secret` redaction pattern already used for `Database.URL`, `Password.Keystore`, `WebServer.OIDC.ClientSecret`, etc. Alternatively, move `AuditLogger.Headers` (or just header *values*) into the `Secrets` struct, and/or restrict `GET /v2/config` to `auth.RequiresAdminRole`.

### Proof of Concept
1. Configure a node with:
```toml
[AuditLogger]
Enabled = true
ForwardToUrl = 'https://siem.example.com/ingest'
Headers = ['Authorization: Bearer sk_live_supersecret123']
```
2. Create/obtain a session or API token for a user with `UserRoleView` (lowest role).
3. Send `GET /v2/config` (or `/v2/config/v2`) with that credential:
```
curl -H "Cookie: <view-role session>" https://node-host/v2/config
```
4. Observe the JSON response's `config` field contains the full TOML including `Headers = ['Authorization: Bearer sk_live_supersecret123', ...]`, disclosing the audit-log credential to a low-privilege user (or, if the node is running the endpoint over unencrypted HTTP as warned against in the original advisory, to any network sniffer). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

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

**File:** core/services/chainlink/config_general.go (L288-290)
```go
func (g *generalConfig) ConfigTOML() (user, effective string) {
	return g.inputTOML, g.effectiveTOML
}
```

**File:** core/web/router.go (L283-285)
```go
		cc := ConfigController{app}
		authv2.GET("/config", cc.Show)
		authv2.GET("/config/v2", cc.Show)
```

**File:** core/web/auth/auth_test.go (L236-236)
```go
	{"GET", "/v2/config", true, true, true},
```

**File:** core/logger/audit/audit_logger.go (L235-237)
```go
	for _, header := range l.headers {
		req.Header.Add(header.Header, header.Value)
	}
```

**File:** core/services/chainlink/config_audit_logger.go (L33-35)
```go
func (a auditLoggerConfig) Headers() (models.ServiceHeaders, error) {
	return *a.c.Headers, nil
}
```

**File:** core/store/models/secrets.go (L7-12)
```go
// Secret is a string that formats and encodes redacted, as "xxxxx".
// Deprecated
type Secret = config.SecretString

// Deprecated
func NewSecret(s string) *Secret { return config.NewSecretString(s) }
```

**File:** docs/CONFIG.md (L397-401)
```markdown
### Headers
```toml
Headers = ['Authorization: token', 'X-SomeOther-Header: value with spaces | and a bar+*'] # Example
```
Headers is the set of headers you wish to pass along with each request
```
