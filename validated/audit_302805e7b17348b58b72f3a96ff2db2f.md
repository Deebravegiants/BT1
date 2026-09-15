Audit Report

## Title
Sensitive fields inside GraphQL `variables` (e.g. passwords) are not redacted before being written to application logs at Debug level - (File: core/web/router.go)

## Summary
The HTTP request logging middleware `loggerFunc` logs sanitized request bodies at Debug level via `readSanitizedJSON`, but that function only inspects top-level JSON keys against the `blacklist`/`isBlacklisted` check. GraphQL requests to `/query` nest all mutation arguments under a `variables` object, so fields like `oldPassword`, `newPassword` (`UpdateUserPassword`) and `password` (`CreateAPIToken`) bypass redaction entirely and are written to logs in plaintext when Debug logging is enabled.

## Finding Description
`loggerFunc` reads the request body and logs it verbatim (after "sanitization") at Debug level on every request: [1](#0-0) 

`readSanitizedJSON` only redacts keys found at the top level of the parsed JSON map: [2](#0-1) 

`isBlacklisted` only performs a case-insensitive substring/exact match against a small set of literal key names (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`): [3](#0-2) 

Since the sanitizer never recurses into nested objects, a GraphQL request body of the shape `{"query": "...", "variables": {"input": {"oldPassword": "...", "newPassword": "..."}}, "operationName": "..."}` has only `query`, `variables`, and `operationName` as top-level keys — none of which match the blacklist — so the entire `variables` subtree, including any password fields, is copied through unredacted into the logged JSON. This is confirmed by the resolver code where `UpdateUserPassword` and `CreateAPIToken` accept `OldPassword`/`NewPassword`/`Password` as nested GraphQL input fields (`core/web/resolver/mutation.go`), which arrive as nested `variables.input.*` fields in the raw request body that `loggerFunc` logs.

## Impact Explanation
This results in disclosure of a user's plaintext current/new password (or other secret-bearing GraphQL mutation arguments) into the node's own log stream whenever Debug-level logging is enabled — a supported, non-default but commonly used operational configuration for troubleshooting. This maps to a secret/credential-exfiltration-via-logs impact class: an existing redaction mechanism (`isBlacklisted`/`blacklist`) exists specifically to prevent this, but is structurally incomplete because it does not walk nested JSON, so it fails for the exact GraphQL-based admin API this node exposes.

## Likelihood Explanation
Any authenticated Operator UI/admin API user invoking `UpdateUserPassword` or `CreateAPIToken` (or any other GraphQL mutation carrying secrets in `variables`) triggers this deterministically, with no privilege escalation, race condition, or unusual setup needed beyond the node being configured with Debug log level — a documented, operator-selectable logging level. The behavior is fully reproducible and not dependent on attacker-controlled bypass logic; it happens as a side effect of normal password-management usage.

## Recommendation
Modify `readSanitizedJSON` (and correspondingly `isBlacklisted`) to recursively walk nested JSON objects and arrays — in particular the GraphQL `variables` object — and redact any blacklisted key at any nesting depth, not only the top level. Additionally consider broadening the blacklist to cover other credential-bearing field names (e.g., `token`, `secret`, `clientSecret`) consistent with other secret types handled elsewhere in the codebase.

## Proof of Concept
1. Configure the node with `Log.Level = "debug"`.
2. As an authenticated user, send a GraphQL POST to `/query`:
```json
{
  "query": "mutation($input: UpdatePasswordInput!) { updatePassword(input: $input) { ... } }",
  "variables": { "input": { "oldPassword": "CurrentSecretPass1", "newPassword": "NewSecretPass2" } }
}
```
3. Inspect the node's Debug log output emitted by `loggerFunc` (`core/web/router.go` lines 556-562) — the `body` field contains the full JSON payload, including `oldPassword` and `newPassword` in plaintext, because `readSanitizedJSON` (lines 608-629) only inspects the top-level keys `query`/`variables`/`operationName`, none of which match `isBlacklisted` (lines 643-658).

A Go unit test directly calling `readSanitizedJSON` with a nested GraphQL-shaped body containing `variables.input.oldPassword` would demonstrate that the returned sanitized string still contains the plaintext password value, proving the redaction gap without requiring a running server.

### Citations

**File:** core/web/router.go (L556-562)
```go
		lggr.Debugw(fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path),
			"method", c.Request.Method,
			"status", c.Writer.Status(),
			"path", c.Request.URL.Path,
			"ginPath", c.FullPath(),
			"query", redact(c.Request.URL.Query()),
			"body", readBody(rdr, lggr),
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
