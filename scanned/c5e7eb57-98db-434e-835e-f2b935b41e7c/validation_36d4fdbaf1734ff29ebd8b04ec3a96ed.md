### Title
Incomplete secret redaction in HTTP request logging exposes API keys/tokens in plaintext node logs - (File: `core/web/router.go`)

### Summary
Chainlink's HTTP logging middleware sanitizes request bodies and query parameters before writing them to node logs, but the redaction filter only matches field names containing the substring `"password"`. Any other secret-bearing field name (API keys, tokens, client secrets, etc.) submitted to the web API is logged verbatim, storing it unencrypted in the node's log files — the same root-cause class (CWE-312, clear-text storage of sensitive information) as the Jenkins Kryptowire plugin advisory, just manifested through the logging/audit path instead of a config XML file.

### Finding Description
The Gin logging middleware captures the request body and query string for every API call and calls `readBody`/`redact` to scrub sensitive fields before logging at debug level: [1](#0-0) 

Both sanitizers rely on a single `isBlacklisted` check: [2](#0-1) 

The blacklist map only contains password-related keys (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`) and a substring check for `"password"`. Field names such as `apiKey`, `apiSecret`, `clientSecret`, `incomingToken`, `outgoingToken`, `authToken`, or `secret` are **not** covered, so any JSON body or query parameter using those field names is written to the node's logs unredacted. This directly parallels the config layer, which does implement proper secret redaction for TOML-based secrets via the `SecretString`/`SecretURL` types (seen redacting to `'xxxxx'` in `core/services/chainlink/testdata/secrets-full-redacted.toml`) and the `docs/SECRETS.md` documentation of `CRE.Streams.APIKey`/`APISecret`, `Pyroscope.AuthToken`, `Prometheus.AuthToken`, and `WebServer.OIDC.ClientSecret` — none of these secret field names would be caught by the HTTP-logging blacklist if ever submitted through an API endpoint (e.g., bridge/External-Initiator token creation, which uses `incomingToken`/`outgoingToken` fields rather than `password`).

### Impact Explanation
Node operators enable debug logging (a supported, documented configuration), and any secret-bearing field not literally named with "password" (API keys, EI tokens, OIDC/OAuth client secrets) ends up persisted in plaintext log files on the controller/host filesystem. Anyone with read access to logs (log aggregation systems, shared hosts, support tickets containing logs) can recover these credentials, enabling authentication bypass or impersonation of external initiators/integrations — matching the CVSS vector of the reference advisory (confidentiality impact via local/log file disclosure).

### Likelihood Explanation
Requires the node to be running with debug-level HTTP request logging enabled, which is a supported/documented mode, and for a caller to submit a request whose JSON body contains a secret field not named "password" (e.g., bridge `incomingToken`/`outgoingToken`). This is a passive/incidental exposure that occurs for legitimate API traffic, not an active exploit chain, so likelihood is moderate.

### Recommendation
Expand `isBlacklisted` in `core/web/router.go` to match a broader set of secret indicators (`token`, `secret`, `apikey`, `api_key`, `clientsecret`, `authtoken`, etc.) using substring matching rather than an exact/short list, and consider redacting by default any field whose value resembles a credential rather than relying solely on field-name heuristics.

### Proof of Concept
1. Enable debug-level logging on a Chainlink node (`Log.Level = 'debug'`).
2. Send an authenticated request to an endpoint that accepts an External Initiator or bridge definition containing `incomingToken`/`outgoingToken` fields (not named "password").
3. Observe the node's debug logs: the `loggingMiddleware` logs the full JSON body via `readBody`/`readSanitizedJSON`, and because `isBlacklisted` does not match `incomingToken`/`outgoingToken`, the token values appear in plaintext in the log output at [1](#0-0) .

Note: I could not fully trace whether every bridge/EI-token-creation endpoint routes through this exact middleware instance in this indexed snapshot; the middleware and blacklist logic themselves are confirmed present and narrowly scoped as described. A full endpoint-by-endpoint trace would benefit from a live Devin session with complete repository access.

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

**File:** core/web/router.go (L608-658)
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

func redact(values url.Values) string {
	cleaned := url.Values{}
	for k, v := range values {
		if isBlacklisted(k) {
			cleaned[k] = []string{"REDACTED"}
			continue
		}
		cleaned[k] = v
	}
	return cleaned.Encode()
}

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
