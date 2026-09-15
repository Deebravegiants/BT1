All claims are verified against the code.

Audit Report

## Title
Sensitive `AuditLogger.Headers` credentials exposed to any authenticated (including view-only) user via `GET /v2/config` - (File: core/web/config_controller.go)

## Summary
`ConfigController.Show` returns the full effective/input TOML configuration (via `cfg.ConfigTOML()`) to any authenticated caller, and the route is registered without any role gate, making it reachable by `view`-role users. Because `AuditLogger.Headers` is stored as `models.ServiceHeaders` (a plain `[]ServiceHeader` with a `MarshalText` that renders `Header||Value` verbatim), not as `config.SecretString`/`config.SecretURL`, it is not redacted by the TOML marshaler's type-based secret-masking, so any `Authorization` header value configured for the audit-log forwarder leaks in cleartext to low-privilege users.

## Finding Description
`ConfigController.Show` calls `cfg.ConfigTOML()` and returns the resulting TOML string unfiltered: [1](#0-0) 
`ConfigTOML()` returns `g.inputTOML`/`g.effectiveTOML`, the general (non-secrets) configuration: [2](#0-1) 

The route is registered in the generic authenticated group with no `RequiresEditRole`/`RequiresAdminRole` wrapper, unlike most other mutating/sensitive routes registered nearby: [3](#0-2) 
The project's own RBAC test table confirms `GET /v2/config` and `/v2/config/v2` are `viewOnlyAllowed: true`, i.e., reachable by the lowest-privilege role: [4](#0-3) 

The redaction mechanism for secrets is type-based: only `config.SecretString`/`config.SecretURL` fields are masked (as used for `Database.URL`, `Password.Keystore` in `secrets.toml`), confirmed by the `Secrets.TOMLString()` marshaling path: [5](#0-4) [6](#0-5) 

`AuditLogger.Headers` is exposed via `auditLoggerConfig.Headers()` as `models.ServiceHeaders`: [7](#0-6) 
`models.ServiceHeaders`/`ServiceHeader` marshal their `Header` and `Value` verbatim via `MarshalText`, with no secret type or masking logic applied: [8](#0-7) 
This is confirmed by test fixtures that render `Headers` in cleartext, e.g. `Headers = ['Authorization: token', ...]`, in the general effective-config TOML (not `secrets.toml`):

Because `Headers` is not wrapped in `config.SecretString`, it bypasses the only redaction mechanism the codebase has, and `ConfigController.Show`—reachable without any role check beyond authentication—returns it verbatim to any authenticated session, including `view`-role users.

## Impact Explanation
This constitutes credential/secret disclosure to an under-privileged authenticated actor: a `view`-role user, who should have read-only, non-administrative visibility, can retrieve the `Authorization` header/token configured for the audit-log forwarding webhook. That credential can be replayed against the external audit endpoint or used to impersonate the node's audit forwarder. This is analogous to a config-dump endpoint failing to redact a legitimately sensitive but improperly-typed field, mapping to an in-scope "key/secret exfiltration" impact class, though the exposed secret pertains to an external audit-forwarding service rather than node keys/funds directly, and requires the operator to have opted into `AuditLogger.Enabled` with header-based auth.

## Likelihood Explanation
The exploit requires only a low-privilege authenticated session (`view` role via API token/session), which is a normal capability in multi-user Chainlink node deployments—no admin/edit privilege, host access, or social engineering is needed. Exposure is conditioned on the operator having configured `AuditLogger.Headers` with a credential (an opt-in feature, per `AUDIT_LOGGER_HEADERS` documented in the changelog), but for any node that follows the documented example, the leak is deterministic and repeatable on every call to `GET /v2/config`/`GET /v2/config/v2`.

## Recommendation
Wrap `AuditLogger.Headers` values (specifically credential-bearing header values, e.g. `Authorization`) using `config.SecretString` semantics so `MarshalText`/TOML marshaling redacts them consistently with `Database.URL`/`Password.Keystore`, or at minimum mask header values matching known credential header names (`Authorization`, `X-Api-Key`, etc.) before including them in `ConfigTOML()` output. Additionally, consider restricting `GET /v2/config` and `/v2/config/v2` to `RequiresEditRole`/`RequiresAdminRole` for defense in depth, since general config can carry other operationally sensitive (if not strictly "secret") data.

## Proof of Concept
1. Configure a node with `[AuditLogger] Enabled = true` and `Headers` containing `Authorization||Bearer supersecrettoken` (per `AUDIT_LOGGER_HEADERS` env var format documented in the changelog).
2. Create a session or API token for a user with `Role = view`.
3. Send `GET /v2/config` (or `/v2/config/v2?userOnly=true`) authenticated as that user — reaching `ConfigController.Show` at [1](#0-0) , which has no role wrapper per [3](#0-2) .
4. Inspect the JSON response's `data.attributes.config` field for the `[AuditLogger] Headers = ['Authorization: Bearer supersecrettoken', ...]` line, confirming cleartext disclosure of the configured credential to a `view`-role user.

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

**File:** core/web/router.go (L283-285)
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

**File:** core/services/chainlink/config_audit_logger.go (L33-35)
```go
func (a auditLoggerConfig) Headers() (models.ServiceHeaders, error) {
	return *a.c.Headers, nil
}
```

**File:** core/store/models/common.go (L274-293)
```go
// ServiceHeader is an HTTP header to include in POST to log service.
type ServiceHeader struct {
	Header string
	Value  string
}

func (h *ServiceHeader) UnmarshalText(input []byte) error {
	parts := strings.SplitN(string(input), ":", 2)
	h.Header = parts[0]
	if len(parts) > 1 {
		h.Value = strings.TrimSpace(parts[1])
	}
	return h.Validate()
}

func (h *ServiceHeader) MarshalText() ([]byte, error) {
	var b bytes.Buffer
	fmt.Fprintf(&b, "%s: %s", h.Header, h.Value)
	return b.Bytes(), nil
}
```
