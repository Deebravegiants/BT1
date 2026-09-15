The claim is accurate as-verified against the code. The vulnerability is confirmed to exist exactly as described.

Audit Report

## Title
Log injection via unsanitized user email in LDAP login logging - (File: core/sessions/ldapauth/ldap.go)

## Summary
`ldapAuthenticator.CreateSession` in `core/sessions/ldapauth/ldap.go` logs the raw, attacker-controlled `sr.Email` field via `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` without stripping CR/LF characters, allowing an unauthenticated caller of the `/sessions` endpoint to inject forged log lines into the node's log stream. [1](#0-0)  This exactly mirrors the CWE-117/CWE-74 log injection bug class, and the sibling OIDC code path was specifically patched against this same issue while the LDAP path was not. [2](#0-1) 

## Finding Description
`SessionsController.Create` binds the client-supplied JSON body directly into a `clsessions.SessionRequest` and forwards it unauthenticated to `sc.App.AuthenticationProvider().CreateSession(ctx, sr)`. [3](#0-2)  When the LDAP authentication provider is configured, this reaches `ldapAuthenticator.CreateSession`, which on a successful login (either genuine LDAP bind or local fallback) logs the raw `sr.Email` via a printf-style `Infof` call: [1](#0-0) . Notably, line 406 does apply `ldap.EscapeFilter` to the email for use in the LDAP search filter, but that escaping is for LDAP filter syntax, not for newline/control characters, and the later `Infof` call at line 435 uses the *un-escaped* `sr.Email` directly. [4](#0-3)  Additionally, line 418 logs `escapedEmail` in an error path, which is also not newline-sanitized. [5](#0-4) 

In contrast, the OIDC authenticator's equivalent code strips `\n` and `\r` from the email before logging it, demonstrating the project is aware of and mitigates this exact vector elsewhere but missed the LDAP path. [2](#0-1)  No sanitization, validation, or structured-field-based logging is applied to `sr.Email` anywhere in the LDAP path before this log call, so an attacker-controlled string containing embedded CR/LF sequences is written verbatim into the node's log output.

## Impact Explanation
An unauthenticated attacker who can reach the LDAP-backed `/sessions` login endpoint can inject forged, arbitrary log lines into the node's log stream by including `\n`/`\r` and crafted text in the `email` field of the login request. This enables fabrication of fake audit/log entries (e.g., spoofed "successful login" lines for other users) or forging misleading operational log content, which can mislead administrators, SIEM/alerting pipelines, or incident responders reviewing authentication logs. This maps to a log forgery/log integrity impact, consistent with a Medium-severity classification as in the referenced CVE-2025-59476 pattern — it does not directly cause privilege escalation, secret disclosure, or fund movement, but does corrupt the integrity of node audit logs.

## Likelihood Explanation
The precondition is that the node is configured to use LDAP authentication (a supported, non-default but legitimate configuration) — no operator/admin credentials are needed by the attacker; the `/sessions` endpoint is the unauthenticated login endpoint by design. Any network client can submit a crafted `email` value in the JSON POST body with no server-side control-character validation blocking it before reaching the `Infof` call, making this readily and repeatably triggerable.

## Recommendation
Sanitize `sr.Email` (strip `\r`/`\n` and other control characters) before any use in log messages in `core/sessions/ldapauth/ldap.go`, mirroring the existing pattern in `core/sessions/oidcauth/oidc.go`. Apply this consistently to both the line 418 error-path log and the line 435 success-path log. Prefer structured logging (e.g., `Infow("Successful LDAP login request", "user", sr.Email, ...)`) paired with an encoder that escapes control characters in field values, rather than interpolating raw user input into printf-style log strings.

## Proof of Concept
1. Configure a Chainlink node with LDAP authentication enabled and a working LDAP server (or one that will fail bind, forcing the local fallback path).
2. Send `POST /sessions` with body:
```json
{
  "email": "attacker@example.com\nINFO Successful LDAP login request for user admin@example.com - admin",
  "password": "<valid local-fallback-admin password or valid LDAP credential for attacker@example.com>"
}
```
3. On successful authentication (local fallback or real LDAP bind), observe the node's log output contains the forged extra line falsely indicating a successful admin login, injected via the crafted `email` field at `core/sessions/ldapauth/ldap.go:435`.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L406-407)
```go
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
```

**File:** core/sessions/ldapauth/ldap.go (L416-419)
```go
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
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
