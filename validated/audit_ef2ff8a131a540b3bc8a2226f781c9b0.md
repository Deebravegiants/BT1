### Title
OIDC ClientSecret logged in plaintext via Debug log statement - ([File: core/sessions/oidcauth/oidc.go])

### Summary
When constructing the OIDC authenticator for the Chainlink node's web server, the full OIDC configuration—including the client secret used to authenticate with the identity provider—is passed directly to a debug log statement using the `%#v` (Go-syntax) verb, which prints all field values of the underlying struct without any redaction.

### Finding Description
`NewOIDCAuthenticator` logs the entire `oidcCfg` config object at debug level before validating or using it: [1](#0-0) 

This mirrors the underlying zot bug class: an OIDC/OAuth `clientSecret` value that should only exist in a TOML secrets file or Kubernetes secret ends up being written verbatim into node logs (stdout or log files) when `Log.Level = 'debug'` is configured, exactly the scenario described in the analog report (Keycloak client secret printed to container logs at startup).

The `oidcCfg` argument implements the `config.OIDC` interface and is backed internally by `oidcConfig{c toml.WebServerOIDC, s toml.WebServerOIDCSecrets}`, where `WebServerOIDCSecrets.ClientSecret` is a `*commonconfig.SecretString`: [2](#0-1) [3](#0-2) 

Elsewhere in the codebase, the project is careful to redact secrets when logging configuration — e.g. `Secrets.TOMLString()` and `generalConfig.LogConfiguration` rely on `commonconfig.SecretString`'s custom marshalling to print `'xxxxx'` instead of the real value when the *Secrets* struct itself is marshaled to TOML: [4](#0-3) [5](#0-4) 

However, the `%#v` verb used in `oidc.go` does not go through TOML marshalling — it uses Go's `fmt` reflection-based formatting of the struct's fields directly. Unless `SecretString` implements a `GoString() string` method (which I could not confirm exists in this repo, since `SecretString` is defined in the external `chainlink-common` dependency and its source is not indexed here), `%#v` will print the raw underlying string value of the secret rather than the redacted form used by TOML encoding. The `blacklist`/redaction logic that exists elsewhere in the codebase for HTTP request bodies only covers `password`-like JSON/form fields and is not applied to this log statement at all: [6](#0-5) 

### Impact Explanation
If `Log.Level` is set to `debug` (a supported, non-privileged configuration option, and one explicitly documented/tested for CLI validate output), the raw OIDC `ClientSecret` used to authenticate the Chainlink node against its identity provider (e.g., Keycloak, Okta) would be written into the node's log output. Logs are frequently shipped to centralized logging systems, container stdout capture, or included in support bundles, all of which have broader read access than the node's secrets.toml file. Disclosure of this secret would allow an attacker to impersonate the node as an OAuth/OIDC client toward the identity provider, potentially enabling authentication bypass against the node's own web UI/API RBAC roles (Admin/Edit/Run/ReadOnly), which are all derived from the OIDC id-token claims validated via this same client configuration.

### Likelihood Explanation
Exploitability requires the operator to run the node with `Log.Level = 'debug'` while OIDC authentication is enabled — a legitimate, documented configuration combination, not a misconfiguration outside the product's supported feature set. No malicious peer, network attacker, or privileged account is required; the exposure happens automatically at node startup whenever the OIDC authenticator is constructed. This is a strong analog to the original zot finding (secret printed at container startup with an OIDC provider configured).

### Recommendation
Remove or redact the raw config from the debug log line in `core/sessions/oidcauth/oidc.go`. Either log only non-sensitive fields explicitly (`ClientID`, `ProviderURL`, `RedirectURL`, claim names) instead of `%#v` of the whole struct, or ensure the logged value only exposes fields that are guaranteed to implement redacting `String()`/`GoString()` methods (e.g., by logging `oidcCfg.ClientSecret()` through a wrapper `SecretString` type rather than the interface directly). Add a regression test similar to `Test_generalConfig_LogConfiguration` that asserts the emitted log output does not contain the configured client secret value when constructing the OIDC authenticator.

### Proof of Concept
1. Configure the node with `Log.Level = 'debug'` and a `[WebServer.OIDC]` block with `AuthenticationMethod = 'oidc'`.
2. Configure `[WebServer.OIDC] ClientSecret = 'super-secret-value'` in secrets.toml (per `docs/SECRETS.md`'s `WebServer.OIDC.clientSecret` field).
3. Start the node; `NewOIDCAuthenticator` executes `lggr.Debugf("OIDC CFG:\n %#v\n", oidcCfg)` at `core/sessions/oidcauth/oidc.go:76` before performing validation of required fields, causing the client secret's underlying value to be rendered into the debug log stream.
4. Inspect node logs / stdout: the OIDC client secret appears in plaintext (unless the external `SecretString.GoString()` implementation is confirmed to redact `%#v` output — this could not be verified from the indexed code and should be checked directly against the `chainlink-common` dependency version in use).

### Citations

**File:** core/sessions/oidcauth/oidc.go (L75-76)
```go
	// Ensure all RBAC role mappings to OIDC Id claims are defined, and required fields populated, or error on startup
	lggr.Debugf("OIDC CFG:\n %#v\n", oidcCfg)
```

**File:** core/config/toml/types.go (L1429-1437)
```go
type WebServerOIDCSecrets struct {
	ClientSecret *commonconfig.SecretString
}

func (w *WebServerOIDCSecrets) setFrom(f *WebServerOIDCSecrets) {
	if v := f.ClientSecret; v != nil {
		w.ClientSecret = v
	}
}
```

**File:** core/services/chainlink/config_web_server.go (L321-338)
```go
type oidcConfig struct {
	c toml.WebServerOIDC
	s toml.WebServerOIDCSecrets
}

func (l *oidcConfig) ClientID() string {
	if l.c.ClientID == nil {
		return ""
	}
	return *l.c.ClientID
}

func (l *oidcConfig) ClientSecret() string {
	if l.s.ClientSecret == nil {
		return ""
	}
	return string(*l.s.ClientSecret)
}
```

**File:** core/services/chainlink/config_general.go (L278-285)
```go
func (g *generalConfig) LogConfiguration(log, warn coreconfig.LogfFn) {
	log("# Secrets:\n%s\n", g.secretsTOML)
	log("# Input Configuration:\n%s\n", g.inputTOML)
	log("# Effective Configuration, with defaults applied:\n%s\n", g.effectiveTOML)
	if g.warning != nil {
		warn("# Configuration warning:\n%s\n", g.warning)
	}
}
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

**File:** core/web/router.go (L643-658)
```go
// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```
