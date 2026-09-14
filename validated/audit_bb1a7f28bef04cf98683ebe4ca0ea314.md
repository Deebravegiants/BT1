Based on my investigation, there is a plausible analog to CVE-2021-21270's bug class (secrets exposed via plaintext logging) reachable from an unprivileged client request in the Gin web server's debug request logger.

### Title
Incomplete Secret Redaction Blacklist Allows Plaintext Logging of Non-Password Secrets in Request Bodies - (File: core/web/router.go)

### Summary
The Chainlink node's Gin HTTP middleware `loggerFunc` logs every incoming request body at Debug level after passing it through a sanitizer, `readSanitizedJSON`/`redact`, that only redacts fields matching a hardcoded `password`-related blacklist. Any JSON body field whose name is a secret-like term other than "password" (e.g., `secret`, `apiKey`, `accessKey`, `token`) is logged unredacted whenever an authenticated (or in some misconfigured cases unauthenticated) client sends a request containing such a field.

### Finding Description
`loggerFunc` reads and logs the full request body for every request handled by the router: [1](#0-0) 

The body is sanitized via `readSanitizedJSON`, which redacts a key only if `isBlacklisted` returns true: [2](#0-1) 

`isBlacklisted` only matches keys containing the substring `"password"` or belonging to a small hardcoded map (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`): [3](#0-2) 

This mirrors the root cause of CVE-2021-21270 (OctopusDSC): a logging/debug path captures request payloads containing authentication secrets, and the redaction logic is incomplete, so secret material other than the explicitly-listed "password" fields is written to logs in plaintext. In this codebase, secret-carrying identifiers such as `Secret`, `AccessKey`, `OutgoingSecret`, `OutgoingToken`, `APIKey` (used throughout `core/auth/auth.go`, `core/bridges/external_initiator.go`, and `core/web/presenters/external_initiators.go`) are not covered by the blacklist: [4](#0-3) [5](#0-4) 

If any endpoint accepts these fields as part of the *request* body (rather than only returning them in the response), they would be logged verbatim at Debug level. I was not able to fully confirm within the available index whether any currently-defined request struct (as opposed to response/presenter structs) actually accepts a `secret`/`accessKey`/`apiKey`-named field in an incoming JSON body — the external initiator creation endpoint's request struct (`ExternalInitiatorRequest`) only contains `Name`/`URL`, and the token creation endpoint's request only contains `password` (already blacklisted). This is a limitation of what I could verify via static search; a full audit of all `ShouldBindJSON` target structs across `core/web/*_controller.go` would be needed to confirm a concrete field name that both (a) carries secret material and (b) is accepted as inbound request JSON, to conclusively demonstrate leakage.

### Impact Explanation
If a concrete inbound field exists that isn't caught by the blacklist, its value (e.g., an external initiator secret, an OIDC client secret via a future admin endpoint, or a webhook signing secret) would be persisted to the node's log files in plaintext at Debug level, readable by anyone with log access — an unprivileged-actor-adjacent disclosure vector once logs are exfiltrated or shipped to less-trusted log aggregation. This matches the CVE-2021-21270 class: secret disclosure via logs due to insufficient redaction.

### Likelihood Explanation
Likelihood is speculative without confirming a concrete non-password secret field accepted in a request body today. The blacklist mechanism itself is demonstrably narrow (substring match on "password" only) and is a maintenance hazard: any future or already-existing endpoint that accepts a secret-bearing field under a name other than "password" would silently leak it. This is more of a defense-in-depth gap than a confirmed working exploit against a known current endpoint.

### Recommendation
Broaden `isBlacklisted` in `core/web/router.go` to also match common secret-related substrings (`secret`, `token`, `apikey`, `accesskey`, `clientsecret`, `authtoken`), or switch to an allowlist model where only explicitly known-safe fields are logged. Additionally, disable or gate body/query logging behind a config flag for production builds, consistent with how `core/services/chainlink/testdata/secrets-full-redacted.toml` and `core/config/toml/types.go` already redact secrets elsewhere (`*****`/`xxxxx` patterns) via `config.SecretString`.

### Proof of Concept
Not concretely reproducible from the index alone — no currently indexed request struct exposes a non-"password" secret field for inbound binding, so no working PoC request/response pair could be confirmed. This finding should be treated as an incomplete-redaction hardening gap rather than a proven, currently-exploitable disclosure.

### Citations

**File:** core/web/router.go (L556-567)
```go
		lggr.Debugw(fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path),
			"method", c.Request.Method,
			"status", c.Writer.Status(),
			"path", c.Request.URL.Path,
			"ginPath", c.FullPath(),
			"query", redact(c.Request.URL.Query()),
			"body", readBody(rdr, lggr),
			"clientIP", c.ClientIP(),
			"errors", c.Errors.String(),
			"servedAt", end.Format("2006-01-02 15:04:05"),
			"latency", fmt.Sprintf("%v", end.Sub(start)),
		)
```

**File:** core/web/router.go (L608-629)
```go
func readSanitizedJSON(buf *bytes.Buffer) (string, error) {
	var dst map[string]any
	err := json.Unmarshal(buf.Bytes(), &dst)
	if err != nil {
		return "", err
	}

	cleaned := map[string]any{}
	for k, v := range dst {
		if isBlacklisted(k) {
			cleaned[k] = "*REDACTED*"
			continue
		}
		cleaned[k] = v
	}

	b, err := json.Marshal(cleaned)
	if err != nil {
		return "", err
	}
	return string(b), err
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

**File:** core/auth/auth.go (L21-25)
```go
// Token is used for API authentication.
type Token struct {
	AccessKey string `json:"accessKey"`
	Secret    string `json:"secret"`
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
