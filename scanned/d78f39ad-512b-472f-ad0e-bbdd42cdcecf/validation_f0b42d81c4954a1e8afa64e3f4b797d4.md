### Title
Incomplete log-redaction blacklist leaks credentials/secrets submitted in request bodies - ([File: core/web/router.go])

### Summary
The in3-server report flagged that private keys and credentials must never leak into debug output, local logs, or external log aggregators. Chainlink's HTTP web-server has an analogous, narrower redaction mechanism for its request/response logging middleware, and that mechanism has a gap: it only redacts fields whose name contains the substring `"password"`, not other common credential/secret field names (`secret`, `token`, `apiKey`, `accessKey`, etc.) that are used throughout the same API surface.

### Finding Description
`core/web/router.go` defines `readBody`/`redact` helpers used by the request logging middleware (`loggerFunc`) to sanitize request bodies/query values before writing them to logs: [1](#0-0) 

The blacklist that drives `isBlacklisted` only matches keys containing `"password"`: [1](#0-0) 

However, several genuine API JSON payloads in the same web server use exactly the kind of secret/token field names that this filter does not catch, e.g. the External Initiator authentication resource which carries `Secret`, `OutgoingToken`, and `OutgoingSecret`: [2](#0-1) 
and the `auth.Token` structure used for API/external-initiator authentication which contains `AccessKey`/`Secret`: [3](#0-2) 

Because the blacklist is a hardcoded substring match on `"password"` only (`core/web/router.go:652-658`), any JSON field named `secret`, `token`, `accessKey`, `apiKey`, `apiSecret`, `outgoingSecret`, etc., sent in a request body to any router-logged endpoint is written verbatim into node logs (and downstream into any log aggregator the operator has configured), directly recreating the credential-leakage class from the report's "Do not leak credentials and key material in debug-mode, to local log-output or external log aggregators" recommendation.

### Impact Explanation
If request/response body logging is enabled (commonly for debugging), any external-initiator secret, access key/secret pair, or other non-"password"-named credential submitted to the API is persisted in plaintext in node logs. Because external initiator credentials are the mechanism by which a component authenticates to trigger job runs (`AuthenticateExternalInitiator` in `core/web/auth/auth.go:119-149`, `core/bridges/external_initiator.go`), leakage of these secrets from logs would let an attacker who can read the logs (log aggregator compromise, log-shipping misconfiguration, etc.) impersonate the external initiator and trigger job runs, matching the report's core concern (impersonation/leak of key material via logs) even though the underlying secret is an application secret rather than a blockchain private key.

### Likelihood Explanation
Exploitation does not require any special privilege on the node process itself: any client capable of submitting an HTTP request containing one of these field names (e.g. hitting the external-initiator or bridge creation endpoints, which in some deployments are reachable pre-authentication depending on middleware ordering) can cause a security-sensitive value to be captured by request logging as soon as Debug-level HTTP logging is enabled — a common operational configuration. This is a straightforward, high-likelihood misconfiguration/gap rather than a hypothetical scenario, since the redaction blacklist is trivially incomplete by design (`strings.Contains(lk, "password")` only).

### Recommendation
- Expand `blacklist` in `core/web/router.go` to include all credential/secret-bearing field name substrings used across the API (`secret`, `token`, `apikey`, `accesskey`, `clientsecret`, etc.), matching the same rigor already applied to `Secret` typed values elsewhere in the codebase (e.g. `config.SecretString` in `core/store/models/secrets.go`).
- Prefer redaction driven by Go struct tags/types (reusing the existing `SecretString`/`SecretURL` redaction pattern) instead of an ad hoc substring blacklist, so that any field marked as a secret is automatically excluded from logs regardless of naming.
- Audit all JSON-serializable request/response types on the web router for secret-bearing fields and ensure they use a redacting type.

### Proof of Concept
1. Enable HTTP request/response debug logging on a Chainlink node (`Log.Level = debug` with the web router logger active).
2. Submit a request to an endpoint whose payload/response includes a field named `secret`, `outgoingSecret`, or `accessKey` (e.g. `POST /v2/external_initiators` which returns `{"secret": ..., "outgoingToken": ..., "outgoingSecret": ...}` per `core/web/presenters/external_initiators.go:13-20`).
3. Inspect node logs / any external log aggregator receiving these logs: the `secret`/`outgoingSecret`/`outgoingToken` values appear in plaintext because `isBlacklisted` (`core/web/router.go:652-658`) only redacts keys containing `"password"`.

### Citations

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

**File:** core/web/presenters/external_initiators.go (L13-20)
```go
type ExternalInitiatorAuthentication struct {
	Name           string        `json:"name,omitempty"`
	URL            models.WebURL `json:"url"`
	AccessKey      string        `json:"incomingAccessKey,omitempty"`
	Secret         string        `json:"incomingSecret,omitempty"`
	OutgoingToken  string        `json:"outgoingToken,omitempty"`
	OutgoingSecret string        `json:"outgoingSecret,omitempty"`
}
```

**File:** core/auth/auth.go (L21-25)
```go
// Token is used for API authentication.
type Token struct {
	AccessKey string `json:"accessKey"`
	Secret    string `json:"secret"`
}
```
