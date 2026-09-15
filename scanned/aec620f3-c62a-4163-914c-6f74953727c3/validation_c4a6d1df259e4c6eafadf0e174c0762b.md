### Title
Flat, top-level-only key redaction in the web request logger fails to protect nested secrets (password, oldPassword, newPassword, API key/token fields) from being written to debug logs - (File: core/web/router.go)

### Summary
The Jenkins advisory describes a redaction mechanism that fails to fully protect secret values before they are written to logs (the transformed/escaped value still let an attacker reconstruct the real secret). The chainlink analog is the gin request logger's body-sanitization routine, which redacts secrets only by scanning the **top-level keys of a flat JSON map**, so any secret nested one level deeper (or sent in a shape the blacklist doesn't recognize) is written to the debug log verbatim.

### Finding Description
`loggerFunc` wraps every HTTP request/response with a debug log line that includes the raw request body, passed through `readBody` → `readSanitizedJSON`: [1](#0-0) [2](#0-1) 

`readSanitizedJSON` unmarshals the body into a single-level `map[string]any` and only replaces values whose **top-level** key matches `isBlacklisted`: [3](#0-2) 

This blacklist-and-flatten approach is structurally identical to the Jenkins flaw in kind: a redaction/escaping mechanism that is applied to the “outer” representation of a value but doesn't account for how the actual secret can still surface through the log. Here, if a client submits a JSON body where a secret is nested inside an object (e.g. `{"data":{"attributes":{"oldPassword":"...","newPassword":"..."}}}`, a shape consistent with JSON:API-style payloads used elsewhere in this API, or any client-crafted body that wraps a `password`/`oldPassword`/`newPassword` field inside an outer object), `json.Unmarshal` produces a top-level key (e.g. `"data"`) whose value is itself a `map[string]any`. `isBlacklisted("data")` returns false, so the entire nested object — including the raw secret — is copied unredacted into `cleaned` and then logged in full at Debug level via `lggr.Debugw(...)`.

Endpoints that accept password material directly in request bodies (e.g. `UserController.UpdatePassword` with `OldPassword`/`NewPassword` fields, `UserController.Create` with a `Password` field, and the various `*_keys_controller.go` handlers taking `OldPassword`/`NewPassword` for key export/import) are all routed through this shared logging middleware: [4](#0-3) [5](#0-4) 

Any unprivileged/unprivileged-adjacent client (an authenticated API user acting on their own account, e.g. via `UpdatePassword` or `NewAPIToken`) whose request body is nested (by design, by a proxy, or by a slightly different client encoding) will have their real password/secret persisted in plaintext in the operator's debug logs, defeating the purpose of the redaction. Additionally the redaction logic matches only `strings.Contains(lk, "password")`, so any secret field not literally named with "password" (e.g. `"token"`, `"apiKey"`, `"secret"`) is not redacted at all, even at the top level.

### Impact Explanation
Impact is credential/secret disclosure (CWE-522 analog): plaintext passwords or tokens intended to be hidden from logs can end up in application logs accessible to operators, log aggregation systems, or anyone with log access — mirroring the Jenkins issue's core harm (secret reconstructable from log output). This is a confidentiality issue (matches CVSS `C:L`), not an availability or integrity issue.

### Likelihood Explanation
Likelihood is moderate: it requires (a) Debug-level logging enabled for the web server (a supported, documented configuration, not a debug-only special build) and (b) a request body shape where the secret field is not at the JSON top level, or is named something other than a variant containing "password". Since the redaction blacklist is a hardcoded, narrow set of key names (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`) checked only against top-level keys, this is easy to trigger unintentionally by any client library that wraps payloads (e.g., JSON:API `data.attributes` conventions used elsewhere in this codebase) and doesn't require any privilege escalation — a normal authenticated user changing their own password can leak their own new password into the operator's logs, and any endpoint carrying a `token`/`apiKey`-like secret leaks unconditionally regardless of nesting.

### Recommendation
- Make `readSanitizedJSON` recursively walk nested objects/arrays and redact any key matching the blacklist at any depth, not just the top level.
- Expand redaction matching beyond substring `"password"` to cover other secret-bearing field names (`token`, `secret`, `apikey`, `key`, `credential`, etc.), or invert the design to an explicit allow-list of loggable fields per endpoint.
- Consider not logging raw request bodies for authentication/password/token endpoints at all, instead logging only method/path/status.

### Proof of Concept
1. Enable `Log.Level = 'debug'` on a running chainlink node.
2. As an authenticated user, send a `PATCH` to the "update password" endpoint with a nested body, e.g.:
```
PATCH /v2/user/password
Content-Type: application/json

{"data":{"oldPassword":"CurrentSecretPass123!","newPassword":"BrandNewSecretPass456!"}}
```
3. Because the endpoint uses `c.ShouldBindJSON` (which tolerates/consumes the body independent of nesting depth expected by the struct, or simply because a slightly different client wraps the payload), the raw bytes reach `loggerFunc`'s `readBody`/`readSanitizedJSON`.
4. `json.Unmarshal` produces `{"data": {"oldPassword": "...", "newPassword": "..."}}`; `isBlacklisted("data")` is `false`, so the entire nested object, including both plaintext passwords, is copied into `cleaned` unredacted.
5. The resulting debug log line contains the plaintext `oldPassword`/`newPassword` values via `"body", readBody(rdr, lggr)` in the `lggr.Debugw` call: [6](#0-5) .

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

**File:** core/web/user_controller.go (L26-31)
```go
// UpdatePasswordRequest defines the request to set a new password for the
// current session's User.
type UpdatePasswordRequest struct {
	OldPassword string `json:"oldPassword"`
	NewPassword string `json:"newPassword"`
}
```

**File:** core/web/user_controller.go (L52-64)
```go
func (u *UserController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	type newUserRequest struct {
		Email    string `json:"email"`
		Password string `json:"password"`
		Role     string `json:"role"`
	}

	var request newUserRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
```
