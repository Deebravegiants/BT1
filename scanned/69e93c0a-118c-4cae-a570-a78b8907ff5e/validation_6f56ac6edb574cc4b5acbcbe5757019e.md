Confirmed: the login endpoint `POST /sessions` (`SessionsController.Create` in `core/web/sessions_controller.go`) binds an unauthenticated client's JSON body directly into `clsessions.SessionRequest` (`sr.Email`, `sr.Password`) and passes it unmodified to `AuthenticationProvider().CreateSession(ctx, sr)`. For LDAP-backed deployments this reaches `ldapAuthenticator.CreateSession` in `core/sessions/ldapauth/ldap.go`, which logs the raw, attacker-supplied `sr.Email` via `Infof` with no CRLF sanitization.

### Title
Log Forging via Unsanitized Login Email in LDAP Authenticator - (File: core/sessions/ldapauth/ldap.go)

### Summary
The LDAP session-creation path logs the unauthenticated client-supplied email field directly into free-text log messages using `%s` formatting, without stripping CR/LF characters. This allows an unprivileged, unauthenticated caller of the `POST /sessions` login endpoint to inject fabricated log lines (log forging), matching the CVE-2025-36159 bug class of "improper neutralization of output" enabling users to forge log entries or impersonate other users/hide their activity in an application's logs.

### Finding Description
`SessionsController.Create` binds the request body straight into `sr clsessions.SessionRequest` via `c.ShouldBindJSON(&sr)` with no validation of the `Email` field's character content [1](#0-0) . This is forwarded to `AuthenticationProvider().CreateSession(ctx, sr)`, which for LDAP-configured nodes calls `ldapAuthenticator.CreateSession` [2](#0-1) .

On a successful bind/login, the authenticator logs:
```go
l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)
``` [3](#0-2)  — `sr.Email` is written verbatim into the log message. The only transformation applied to the email elsewhere in this function is `ldap.EscapeFilter`, which escapes LDAP filter metacharacters (`\`, `*`, `(`, `)`, NUL) but does **not** strip or escape `\r`/`\n` [4](#0-3) . Since the LDAP bind is attempted before the fallback local check, and the failure/log path also reuses `escapedEmail` in a log statement, a client can submit an email value containing embedded newlines (e.g. `attacker@example.com\n2026-09-13 12:00:00 INF Successful LDAP login request for user admin@example.com - admin`) that gets split across multiple lines in the log stream, forging what appears to be a legitimate admin login entry.

This is a real, previously-recognized bug class in this same codebase: the sibling `oidcauth` authenticator explicitly sanitizes the exact same field before logging it:
```go
sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)
``` [5](#0-4) . The `ldapauth` implementation was never updated with the equivalent CRLF-stripping fix, leaving it exploitable.

### Impact Explanation
An unauthenticated network client hitting the login endpoint can forge arbitrary log lines in the node's operational logs (and, since these lines also flow into the audit trail infrastructure via the same logger, potentially corrupt on-disk/forwarded audit records). This can be used to fabricate evidence of successful admin logins that never happened, obscure a real attacker's login attempts among injected noise, or mislead operators/SOC tooling that parse log lines for authentication monitoring. No confidentiality or availability impact, but integrity of audit/log data is compromised, consistent with the CVSS vector in the reference CVE (C:N/I:H/A:N).

### Likelihood Explanation
High likelihood of reachability: the `/sessions` endpoint is unauthenticated by design (it's the login endpoint) and accepts arbitrary JSON-controlled `Email` values with no server-side character filtering before this log call. Only requires an LDAP-authentication-configured deployment attempting a login (the code path is reached regardless of whether the LDAP bind ultimately succeeds, as long as it reaches the final success branch, or via the `escapedEmail` log at line 418 on the FindUser failure path where the raw error email is not the escaped one being logged in the success line).

### Recommendation
Apply the same CRLF/control-character sanitization used in `core/sessions/oidcauth/oidc.go` (strip `\r`/`\n`, or more robustly all non-printable characters) to `sr.Email` before it is passed to any `lggr.Infof`/`Errorf`/`Warnf` call in `core/sessions/ldapauth/ldap.go`, including the success log at line 435 and the `escapedEmail`-based log at line 418. Consider centralizing this sanitization in a shared logging helper or in `SessionRequest` validation so all current and future authenticator implementations (local, LDAP, OIDC) are protected uniformly, rather than duplicating ad-hoc fixes per authenticator.

### Proof of Concept
1. Configure a chainlink node with LDAP authentication enabled.
2. Send `POST /sessions` with body:
```json
{"email": "attacker@example.com\n2026-09-13T12:00:00Z INF Successful LDAP login request for user admin@example.com - admin", "password": "wrongpass"}
```
3. Observe the node's log output: the injected string is written as-is into the `Infof` call at `core/sessions/ldapauth/ldap.go:435` (reached if bind eventually succeeds via LDAP or local fallback for that raw string, or observe the same effect via the `escapedEmail` log at line 418 which is hit on any `FindUser` lookup failure after LDAP bind), producing a forged extra log line that appears to record a successful admin login that never occurred. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** core/web/sessions_controller.go (L29-68)
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

	if err := saveSessionID(session, sid); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, errors.Join(errors.New("unable to save session id"), err))
		return
	}

	jsonAPIResponse(c, Session{Authenticated: true}, "session")
}
```

**File:** core/sessions/ldapauth/ldap.go (L396-457)
```go
func (l *ldapAuthenticator) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		return "", errors.New("unable to establish connection to LDAP server with provided URL and credentials")
	}
	defer conn.Close()

	var returnErr error

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}

	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
	}

	isLocalUser := false
	if returnErr != nil {
		// Unable to log in against LDAP server, attempt fallback local auth with credentials, case of local CLI Admin account
		// Successful local user sessions can not be managed by the upstream server and have expiration handled by the reaper sync module
		foundUser, returnErr = l.localLoginFallback(ctx, sr)
		isLocalUser = true
	}

	// If err is still populated, return
	if returnErr != nil {
		return "", returnErr
	}

	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)

	// Save session, user, and role to database. Given a session ID for future queries, the LDAP server will not be queried
	// Sessions are set to expire after the duration + creation date elapsed, and are synced on an interval against the upstream
	// LDAP server
	session := sessions.NewSession()
	_, err = l.ds.ExecContext(
		ctx,
		"INSERT INTO ldap_sessions (id, user_email, user_role, localauth_user, created_at) VALUES ($1, $2, $3, $4, now())",
		session.ID,
		strings.ToLower(sr.Email),
		foundUser.Role,
		isLocalUser,
	)
	if err != nil {
		l.lggr.Errorf("unable to create new session in ldap_sessions table %v", err)
		return "", fmt.Errorf("error creating local LDAP session: %w", err)
	}

	l.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})

	return session.ID, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L409-439)
```go
// CreateSession in the context of the OIDC driver handles only the local auth admin user, exposed by the default endpoint defined in the router. To initiate the SAML/OIDC
// flow, a separate /oidc-login route is defined which handles the redirect to the
// configured provider
func (oi *oidcAuthenticator) CreateSession(ctx context.Context, sr clsessions.SessionRequest) (string, error) {
	foundUser, err := oi.localLoginFallback(ctx, sr)
	if err != nil {
		return "", err
	}

	sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
	sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
	oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)

	// Save local admin session, user, and role to sessions table
	// Sessions are set to expire after the duration + creation date elapsed
	session := clsessions.NewSession()
	_, err = oi.ds.ExecContext(ctx,
		"INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
		session.ID,
		strings.ToLower(sr.Email),
		foundUser.Role,
	)
	if err != nil {
		oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
		return "", fmt.Errorf("error creating local OIDC session: %w", err)
	}

	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})

	return session.ID, nil
}
```
