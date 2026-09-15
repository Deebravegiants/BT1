### Title
Unsanitized LDAP Login Email/Credentials Written to Logs Enables Log Injection - (File: core/sessions/ldapauth/ldap.go)

### Summary
The LDAP authenticator's `CreateSession` function logs the raw, attacker-supplied `Email` field from an unauthenticated `SessionRequest` without neutralizing control characters (CWE-117), analogous to CVE-2026-49091's Kibana log-injection bug class. This is reachable pre-authentication via the standard chainlink login flow.

### Finding Description
`sessions.SessionRequest` carries an `Email` field with no format/character validation at the struct level [1](#0-0) . In the LDAP authenticator's `CreateSession`, this attacker-controlled string is passed to `ldap.EscapeFilter` only to build the LDAP search DN — `EscapeFilter` neutralizes LDAP filter metacharacters (`\`, `*`, `(`, `)`, NUL) per RFC 4515, but it does **not** strip or encode newline/control characters [2](#0-1) .

The same raw (or LDAP-escaped-but-not-log-escaped) values are then written directly to the application log with `Infof`/`%s` formatting in multiple places within the same unauthenticated flow:
- `l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)` [3](#0-2) 
- `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` [4](#0-3) 

Neither of these paths route through any control-character sanitizer. This is notable because the codebase already has a purpose-built defense for exactly this class of bug — `remote.SanitizeLogString`, which strips unprintable characters and truncates long strings before logging peer-supplied content [5](#0-4)  — and the web request logger similarly redacts/sanitizes JSON bodies before logging (`readSanitizedJSON`, `redact`) [6](#0-5) . The LDAP login path was not brought under this same discipline, so a login `Email` value containing `\n`, `\r`, or ANSI escape sequences is written verbatim to the structured/plaintext log stream.

### Impact Explanation
An unauthenticated client submitting a login request (`SessionRequest.Email`) can inject newlines or terminal control sequences into the operator's log stream. When logs are viewed with a terminal or log viewer that interprets these sequences, an attacker can forge fake log lines (e.g., fabricate a bogus "Successful LDAP login request for user admin@example.com" entry) or obscure/tamper with the visual representation of legitimate log entries — the same log-tampering/forging impact (CAPEC-93) described in the Kibana advisory. This can mislead incident responders, hide malicious activity, or falsely implicate other users, undermining audit trail integrity for authentication events.

### Likelihood Explanation
The `CreateSession` function is invoked directly by the login/session-creation flow before any authentication succeeds, so the crafted `Email` value is attacker-controlled and requires no prior privileges — only the ability to submit a login attempt. This makes exploitation straightforward for any external, unprivileged actor with network access to the login endpoint (particularly once LDAP auth is enabled, a documented supported auth mode).

### Recommendation
Sanitize `sr.Email` (and any other request-derived values) before logging in `ldap.go`, using an existing pattern such as `remote.SanitizeLogString` or a similar control-character stripping/truncation helper, at every `Infof`/`Errorf`/`Audit` call site that includes the raw email or derived values from the LDAP bind result.

### Proof of Concept
1. Configure chainlink node with LDAP authentication enabled.
2. Submit a login request to the session endpoint with:
   ```json
   { "email": "attacker@example.com\n2026-09-13T00:00:00Z INFO Successful LDAP login request for user admin@example.com - admin", "password": "validpass" }
   ```
3. If the email/credentials pass LDAP bind (or fail with the injected content still logged in the "querying for user groups" error path at line 418), the resulting log line is written containing an embedded fake, well-formatted log entry.
4. Viewing the resulting log file in a terminal or naive log viewer displays the forged "admin" login line as if it were a genuine, separate log entry.

---
Note: I could not verify at the HTTP-handler layer (`core/web` session controller) how `SessionRequest.Email` is deserialized/forwarded to `CreateSession`, since `core/web/session_controller.go` was not found in the indexed codebase — the index may not contain this file. If you need to confirm the exact unauthenticated HTTP entry point and its request validation, a Devin session with full repo access would be able to inspect that file directly.

### Citations

**File:** core/sessions/session.go (L14-22)
```go
// SessionRequest encapsulates the fields needed to generate a new SessionID,
// including the hashed password.
type SessionRequest struct {
	Email          string `json:"email"`
	Password       string `json:"password"`
	WebAuthnData   string `json:"webauthndata"`
	WebAuthnConfig WebAuthnConfiguration
	SessionStore   *WebAuthnSessionStore
}
```

**File:** core/sessions/ldapauth/ldap.go (L406-411)
```go
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L417-419)
```go
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
```

**File:** core/sessions/ldapauth/ldap.go (L435-435)
```go
	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)
```

**File:** core/capabilities/remote/utils_test.go (L109-120)
```go
func TestSanitizeLogString(t *testing.T) {
	t.Parallel()

	require.Equal(t, "hello", remote.SanitizeLogString("hello"))
	require.Equal(t, "[UNPRINTABLE] 0a", remote.SanitizeLogString("\n"))

	var longString strings.Builder
	for range 100 {
		longString.WriteString("aa-aa-aa-")
	}
	require.Equal(t, longString.String()[:256]+" [TRUNCATED]", remote.SanitizeLogString(longString.String()))
}
```

**File:** core/web/router.go (L588-629)
```go
func readBody(reader io.Reader, lggr logger.Logger) string {
	buf := new(bytes.Buffer)
	_, err := buf.ReadFrom(reader)
	if err != nil {
		lggr.Warn("unable to read from body for sanitization: ", err)
		return "*FAILED TO READ BODY*"
	}

	if buf.Len() == 0 {
		return ""
	}

	s, err := readSanitizedJSON(buf)
	if err != nil {
		lggr.Warn("unable to sanitize json for logging: ", err)
		return "*FAILED TO READ BODY*"
	}
	return s
}

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
