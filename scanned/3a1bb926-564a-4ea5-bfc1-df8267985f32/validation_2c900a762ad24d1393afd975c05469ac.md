## #Vulnerability found for this question.

### Title
Log injection via unsanitized user email in LDAP login logging - (File: core/sessions/ldapauth/ldap.go)

### Summary
The LDAP authentication provider's `CreateSession` function logs the raw, attacker-controlled `sr.Email` value directly into a formatted log message using `Infof`, without stripping CR/LF characters. This lets any unauthenticated caller of the `/sessions` login endpoint inject forged log lines into the Chainlink node's log output, mirroring the exact bug class described in CVE-2025-59476 (Jenkins log message injection via unsanitized user-controlled content).

### Finding Description
`SessionsController.Create` in [1](#0-0)  is an unauthenticated endpoint (`POST /sessions`) that binds the client-supplied JSON body directly into a `clsessions.SessionRequest` and passes it to `sc.App.AuthenticationProvider().CreateSession(ctx, sr)`.

When the configured authentication provider is LDAP, this flows into `ldapAuthenticator.CreateSession`: [2](#0-1) 
```go
l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)
```
`sr.Email` is the raw, unauthenticated, unsanitized request field — it is never validated for control characters before being interpolated into the log message string via `Infof` (a printf-style, non-structured log call). An attacker can submit an email value containing `\n`/`\r` characters followed by forged log content (e.g., fake "Successful LDAP login" lines for a different user, or fake error/audit-looking text) and have those characters written verbatim into the node's log stream, exactly matching the Jenkins log-message-injection bug class (CWE-117/CWE-74): unrestricted line-break characters from user-specified content inserted into log output.

Notably, the sibling OIDC implementation was specifically patched to avoid this: [3](#0-2) 
```go
sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)
```
This confirms the project is aware of, and mitigates, this exact injection vector elsewhere — but the LDAP path at line 435 (and the earlier `escapedEmail`-based log at line 418, which is only LDAP-filter-escaped, not newline-stripped) was missed. The `localauth` ORM path ( [4](#0-3) , `lggr.Debugw("Found user")` with `"user", user.Email`) additionally logs the email as a structured field which is less exploitable, but the LDAP `Infof` call is a plain formatted string written straight to the log sink/console encoder, which does not escape embedded line breaks.

### Impact Explanation
An unauthenticated attacker can inject arbitrary forged lines into the node's log output by supplying a crafted `email` value with embedded newlines in a login request. This can be used to:
- Fabricate fake "successful login" entries for arbitrary usernames, misleading administrators or automated log-based alerting/SIEM systems.
- Obscure or confuse real audit trail entries around authentication events.
- Potentially forge fake ERROR/WARN-looking lines to mislead operators investigating incidents (log forgery / log spoofing), consistent with the CVSS impact of CVE-2025-59476 (Confidentiality: None, Integrity: Low).

This does not directly grant privilege escalation or secret disclosure, matching the "Medium" severity classification of the original advisory.

### Likelihood Explanation
High likelihood of triggering: the `/sessions` endpoint is unauthenticated by design (it's the login endpoint), reachable by any network client, and the `email` field is fully attacker-controlled JSON input with no server-side validation rejecting control characters before being placed into the `Infof` log call.

### Recommendation
Sanitize `sr.Email` (strip or encode `\r`/`\n` and other non-printable characters) before using it in any log message in `core/sessions/ldapauth/ldap.go`, consistent with the pattern already applied in `core/sessions/oidcauth/oidc.go`. Prefer structured logging fields (e.g., `l.lggr.Infow("Successful LDAP login request", "user", sr.Email, "role", foundUser.Role)`) with a log encoder/formatter that escapes control characters, rather than interpolating raw user input into printf-style log strings.

### Proof of Concept
1. Configure the Chainlink node with LDAP authentication enabled.
2. Send `POST /sessions` with body:
```json
{
  "email": "attacker@example.com\nINFO Successful LDAP login request for user admin@example.com - admin",
  "password": "irrelevant"
}
```
3. Observe the node's log output contains a forged extra log line falsely indicating a successful admin login, injected via the crafted `email` field, even though the actual login attempt may fail or belong to `attacker@example.com`.

### Citations

**File:** core/web/sessions_controller.go (L29-60)
```go
func (sc *SessionsController) Create(c *gin.Context) {
	defer sc.App.WakeSessionReaper()
	ctx := c.Request.Context()
	sc.App.GetLogger().Debugf("TRACE: Starting Session Creation")

	session := sessions.Default(c)
	var sr clsessions.SessionRequest
	if err := c.ShouldBindJSON(&sr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("error binding json %w", err))
		return
	}

	// Does this user have 2FA enabled?
	userWebAuthnTokens, err := sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)
	if err != nil {
		sc.App.GetLogger().Errorf("Error loading user WebAuthn data: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}

	// If the user has registered MFA tokens, then populate our session store and context
	// required for successful WebAuthn authentication
	if len(userWebAuthnTokens) > 0 {
		sr.SessionStore = sc.sessions
		sr.WebAuthnConfig = sc.App.GetWebAuthnConfiguration()
	}

	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/sessions/ldapauth/ldap.go (L435-435)
```go
	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)
```

**File:** core/sessions/oidcauth/oidc.go (L418-420)
```go
	sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
	sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
	oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)
```

**File:** core/sessions/localauth/orm.go (L149-150)
```go
	lggr := o.lggr.With("user", user.Email)
	lggr.Debugw("Found user")
```
