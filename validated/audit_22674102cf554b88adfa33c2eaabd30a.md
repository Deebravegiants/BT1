### Title
Debug-level HTTP request logging in the node API only redacts "password"-named fields, allowing other secrets (bridge `IncomingToken`/`OutgoingToken`, external-initiator secrets, API keys) to be written to node logs - (File: core/web/router.go)

### Summary
The Snowflake advisory describes a bug class where DEBUG-level logging captured credentials that a redaction formatter failed to fully mask. The Chainlink node has an analogous DEBUG-level HTTP logging middleware, `loggerFunc`, that dumps full request bodies and query strings, relying on a narrow, hard-coded redaction blacklist that only matches keys containing the substring "password".

### Finding Description
`loggerFunc` in `core/web/router.go` reads the entire request body and logs it at `Debugw` for every request that passes through the gin engine: [1](#0-0) 

The body/query redaction is delegated to `readSanitizedJSON`/`redact`, both of which only strip fields whose key matches `isBlacklisted`: [2](#0-1) [3](#0-2) 

The blacklist is a static, tiny set of password-related keys: [4](#0-3) 

Any other sensitive field name in a request body — e.g. bridge `IncomingToken`/`OutgoingToken` values used to authenticate bridge/external-initiator callbacks, or other secret-bearing fields that don't literally contain the substring "password" — is logged verbatim to the node log file whenever `Log.Level = 'debug'` is configured (a supported, documented configuration, not an edge case): [5](#0-4) 

This mirrors the CVE-2024-49750 root cause: a purpose-built secret-redaction mechanism (here, `isBlacklisted`) that is incomplete, so DEBUG logging leaks credential-bearing fields it was specifically designed to protect.

### Impact Explanation
If an authenticated node operator (or any client hitting the node's HTTP API, including bridge/external-initiator management endpoints) enables debug logging — which is a normal, supported diagnostic mode — request bodies containing bridge tokens or other non-"password"-named secrets get persisted into the node's log files unredacted. Anyone with read access to node logs (which is often a broader trust boundary than the admin API itself — e.g. log aggregation systems, support engineers, CI artifacts) could recover these secrets and use them to impersonate bridges/external initiators or replay authenticated callbacks. This is a real, unprivileged-to-log-reader confidentiality leak, consistent with CWE-532.

### Likelihood Explanation
Moderate. It requires `Log.Level = 'debug'` to be enabled, which is common during troubleshooting and is explicitly documented/supported. Once enabled, the exposure is automatic and silent for any field name not resembling "password" — no additional attacker action is needed beyond reaching the endpoint that carries the secret in its request body.

### Recommendation
Broaden the redaction blacklist in `isBlacklisted` (core/web/router.go) beyond substring matching on "password" to include known secret-bearing keys across the API surface (e.g. `IncomingToken`, `OutgoingToken`, `secret`, `token`, `apiKey`, `Authorization`), or replace the ad-hoc blacklist with an allow-list/structured redaction approach (e.g., marking sensitive struct fields the same way `config.SecretString`/`SecretURL` already do elsewhere in the codebase) so that DEBUG-level HTTP logging never emits raw secret material regardless of field naming.

### Proof of Concept
Not independently verified beyond static code reading — I could not confirm from the index whether bridge `IncomingToken`/`OutgoingToken` values are actually included in request bodies that flow through `loggerFunc` (vs. being stored server-side only), since the bridge controller/handler source wasn't fully retrieved in this session. This should be validated by tracing `core/web/bridge_types_controller.go` and the presenters in `core/web/presenters/bridges.go` to confirm whether token values appear in create/update request payloads that hit this logging middleware, and by enabling `Log.Level=debug` and issuing such a request to observe log output directly.

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

**File:** core/web/router.go (L631-658)
```go
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

**File:** docs/CONFIG.md (L412-419)
```markdown
### Level
```toml
Level = 'info' # Default
```
Level determines only what is printed on the screen/console. This configuration does not apply to the logs that are recorded in a file (see [`Log.File`](#logfile) for more details).

The available levels are:
- "debug": Useful for forensic debugging of issues.
```
