# [M] Nginx-UI Settings API Exposes Protected Secrets

## Summary
Severity: Medium
Advisory: GHSA-q4w7-56hr-83rm
CVE: CVE-2026-42223
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-q4w7-56hr-83rm
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/nginx-ui` — affected >=0 <2.3.8

## Details
### Summary
The `GetSettings` API handler (`api/settings/settings.go:24-65`) serializes all settings structs to JSON and returns them to authenticated users. Many sensitive fields are tagged with `protected:"true"` - however, this tag is only enforced during writes (via `ProtectedFill` in `SaveSettings`) and is completely ignored during reads. This exposes 40+ protected fields including `JwtSecret` (enabling auth token forgery), `NodeSecret` (enabling cluster node impersonation), OIDC `ClientSecret` (enabling OAuth account takeover), and the IP whitelist configuration.

### Details
#### Vulnerable Code

**`api/settings/settings.go:49-64` - GetSettings serializes all fields**

```go
c.JSON(http.StatusOK, gin.H{
    "app":       cSettings.AppSettings,
    "server":    cSettings.ServerSettings,
    "database":  settings.DatabaseSettings,
    "auth":      settings.AuthSettings,
    "casdoor":   settings.CasdoorSettings,
    "oidc":      settings.OIDCSettings,
    "cert":      settings.CertSettings,
    "http":      settings.HTTPSettings,
    "logrotate": settings.LogrotateSettings,
    "nginx":     settings.NginxSettings,
    "node":      settings.NodeSettings,
    "openai":    settings.OpenAISettings,
    "terminal":  settings.TerminalSettings,
    "webauthn":  settings.WebAuthnSettings,
})
```

Go's `json.Marshal` serializes all exported fields with `json:` tags. The `protected:"true"` struct tag is a custom tag - it has no effect on JSON serialization.

#### Protection is Write-Only

**`api/settings/settings.go:126-135` - ProtectedFill only used during saves**

```go
cSettings.ProtectedFill(cSettings.AppSettings, &json.App)
cSettings.ProtectedFill(cSettings.ServerSettings, &json.Server)
cSettings.ProtectedFill(settings.AuthSettings, &json.Auth)
// ... etc
```

`ProtectedFill` prevents overwriting protected fields during `SaveSettings`, but `GetSettings` has no corresponding filter. The protection is asymmetric - secrets can be read but not overwritten.

#### Exposed Protected Fields

**`settings/node.go`:**
- `Secret` (protected) - used for cluster node authentication
- `SkipInstallation` (protected), `Demo` (protected)

**`settings/oidc.go` (all protected):**
- `ClientId`, `ClientSecret`, `Endpoint`, `RedirectUri`, `Scopes`, `Identifier`

**`settings/casdoor.go` (all protected):**
- `Endpoint`, `ExternalUrl`, `ClientId`, `ClientSecret`, `CertificatePath`, `Organization`, `Application`, `RedirectUri`

**`settings/auth.go`:**
- `IPWhiteList` (protected) - exposes security configuration

#### Attack Scenario

1. Low-privilege authenticated user calls `GET /api/settings`
2. Response includes `NodeSecret` - attacker can impersonate cluster nodes
3. Response includes OIDC `ClientSecret` - attacker can perform OAuth flows as the application
4. Response includes `IPWhiteList` - attacker learns network security configuration
5. If `JwtSecret` is in app settings (via cosy framework), attacker can forge authentication tokens for any user

### PoC
**1. `GetSettings` serializes all fields** without filtering `protected:"true"` tags. From `api/settings/settings.go:49-64`:

```go
c.JSON(http.StatusOK, gin.H{
    "app":       cSettings.AppSettings,
    "server":    cSettings.ServerSettings,
    "database":  settings.DatabaseSettings,
    "auth":      settings.AuthSettings,
    "casdoor":   settings.CasdoorSettings,
    "oidc":      settings.OIDCSettings,
    "cert":      settings.CertSettings,
    "http":      settings.HTTPSettings,
    "logrotate": settings.LogrotateSettings,
    "nginx":     settings.NginxSettings,
    "node":      settings.NodeSettings,
    "openai":    settings.OpenAISettings,
    "terminal":  settings.TerminalSettings,
    "webauthn":  settings.WebAuthnSettings,
})
```

Go's `json.Marshal` serializes all exported fields. The custom `protected:"true"` tag has no effect on serialization.

**2. Protected secrets are defined** across `settings/*.go`. High-impact examples:

```go
// settings/server_v1.go:19
JwtSecret string `json:"jwt_secret" protected:"true"`

// settings/node.go:5
Secret string `json:"secret" protected:"true"`

// settings/oidc.go
ClientSecret string `json:"client_secret" protected:"true"`

// settings/auth.go
IPWhiteList []string `json:"ip_white_list" protected:"true"`
```

**3. `ProtectedFill` is write-only.** It appears 10 times in `SaveSettings` (lines 126-135) but 0 times in `GetSettings`:

```go
// api/settings/settings.go:126-135 - Only used during writes
cSettings.ProtectedFill(cSettings.AppSettings, &json.App)
cSettings.ProtectedFill(cSettings.ServerSettings, &json.Server)
cSettings.ProtectedFill(settings.AuthSettings, &json.Auth)
// ... 7 more calls
```

**4. Exploit request.** Any authenticated user can retrieve all secrets:

```http
GET /api/settings HTTP/1.1
Authorization: Bearer <any-valid-jwt>
```

Response includes (among 45 protected fields):
```json
{
  "app": {"jwt_secret": "<the-actual-jwt-signing-key>", ...},
  "node": {"secret": "<node-authentication-secret>", ...},
  "oidc": {"client_secret": "<oidc-client-secret>", ...},
  "casdoor": {"client_secret": "<casdoor-client-secret>", ...},
  "auth": {"ip_white_list": ["10.0.0.1", ...], ...},
  "nginx": {"reload_cmd": "nginx -s reload", "restart_cmd": "...", ...}
}
```


### Impact
- **Authentication bypass via JwtSecret**: An attacker who obtains the `JwtSecret` can forge valid JWT tokens for any user, including admin accounts. This provides permanent, independent access that survives password changes and session revocations.
- **Cluster compromise via NodeSecret**: The `NodeSecret` is used for inter-node authentication in nginx-ui clusters. An attacker can impersonate any cluster node, push malicious configurations to all nodes, and intercept cluster synchronization traffic.
- **Third-party OAuth takeover**: Leaked OIDC `ClientSecret` and Casdoor `ClientSecret` allow the attacker to perform OAuth flows as the nginx-ui application, potentially gaining access to user accounts on the identity provider.
- **Security configuration disclosure**: The `IPWhiteList`, `ReloadCmd`, `RestartCmd`, `ConfigDir`, `SbinPath`, and other protected fields reveal the security posture and infrastructure layout, enabling more targeted attacks.
- **Low barrier to exploitation**: Any authenticated user (not just admins) can access `GET /api/settings`. In multi-user deployments, a low-privilege operator can escalate to full admin access.

### Remediation

Filter out `protected:"true"` fields before serialization.

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-q4w7-56hr-83rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-42223
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.8
