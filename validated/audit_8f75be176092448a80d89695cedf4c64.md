### Title
Unsanitized user-controlled email logged verbatim on login, enabling terminal escape-sequence injection into operator logs - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The `CVE-2017-10784` WEBrick advisory concerns Basic-auth usernames being written unsanitized into server logs, allowing an attacker to inject terminal escape sequences that corrupt or spoof log output for whoever views the log with a terminal emulator. The chainlink LDAP authentication driver has the same bug class: the raw, client-supplied `SessionRequest.Email` field is written directly into an `Infof` log line on every successful login, with no control-character sanitization.

### Finding Description
`SessionsController.Create` in `core/web/sessions_controller.go:29-56` binds the unauthenticated POST `/sessions` request body straight into a `clsessions.SessionRequest{Email, Password}` struct via `c.ShouldBindJSON(&sr)` and forwards it unmodified to `AuthenticationProvider().CreateSession(ctx, sr)`. This endpoint is reachable by any unauthenticated actor since it's the login endpoint itself. [1](#0-0) 

When the LDAP driver is configured, `ldapAuthenticator.CreateSession` in `core/sessions/ldapauth/ldap.go` takes this attacker-controlled `sr.Email` and, on a successful bind/local-fallback login, logs it verbatim:
```go
l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)
``` [2](#0-1) 

There is no stripping of control characters (e.g. `\x1b` ANSI escape sequences, carriage returns) before this value reaches the logger. The only escaping applied to the email anywhere in this function is `ldap.EscapeFilter`, which escapes LDAP filter metacharacters (`\`, `*`, `(`, `)`, NUL) for use in an LDAP search filter — it does not strip or encode terminal control/escape characters, so it provides no protection against this bug class. [3](#0-2) 

Notably, the sibling OIDC driver in `core/sessions/oidcauth/oidc.go` already recognizes this exact risk and partially mitigates it before its equivalent log line, stripping `\n` and `\r`:
```go
sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)
``` [4](#0-3) 

This confirms the project is aware that user-supplied email must be sanitized before logging, but the LDAP driver's identical log call was never given the same treatment. In addition, the `oidc.go` sanitization itself is incomplete — it only strips `\n`/`\r`, not other ANSI/terminal escape sequences (`\x1b[...`), so a crafted email containing raw ESC-sequence bytes would still pass through unsanitized there too. This is the same underlying flaw as `CVE-2017-10784`: user-supplied identity strings logged without stripping terminal control/escape sequences. [5](#0-4) 

### Impact Explanation
An unauthenticated client can submit an email value containing ANSI/terminal escape sequences via the public `/sessions` login endpoint. On successful login (or even on partial failure paths that also log `sr.Email`/`escapedEmail`, e.g. line 418 `"Successful user login, but error querying for user groups: user: %s..."`), that raw value is written to the node operator's logs. If those logs are viewed via a terminal emulator, the injected escape sequences can rewrite terminal titles, hide/alter previously displayed log lines, or in vulnerable terminal emulators execute more advanced escape-sequence-driven actions (clipboard injection, OSC command execution) — matching the exact impact class described in the WEBrick advisory (log-based terminal injection leading to potential command execution against whoever reviews the logs).

### Likelihood Explanation
High reachability: the `/sessions` endpoint requires no prior authentication (it *is* the login endpoint), and the vulnerable log statement fires on the normal successful-login code path in `ldapAuthenticator.CreateSession`, so any registered/valid LDAP or local-fallback user (or an attacker probing usernames) can trigger it by simply including escape bytes in the `email` JSON field submitted with valid credentials, or triggering the "querying for user groups" error branch. No special privilege or race condition is required.

### Recommendation
Sanitize `sr.Email` (and any other client-supplied identity strings such as `escapedEmail`/bind DN components) before passing them to logger calls in `core/sessions/ldapauth/ldap.go`, mirroring — and improving on — the approach already used in `core/sessions/oidcauth/oidc.go`. Rather than only stripping `\n`/`\r`, strip/escape all non-printable and ANSI escape (`\x1b`) control characters, or better, route all user-controlled values through a structured logging field (`lggr.Infow("...", "email", sr.Email)`) combined with a logger-level sanitizer, consistent with the existing `remote.SanitizeLogString` helper used elsewhere in the codebase (`core/capabilities/remote/utils_test.go` references `remote.SanitizeLogString`, which already handles unprintable-character replacement and truncation) — apply that same utility to session/login logging paths. [6](#0-5) 

### Proof of Concept
1. Configure the node with `AuthenticationProviderName = "ldap"` (or local fallback enabled).
2. Send `POST /sessions` with body:
```json
{"email": "victim\u001b]0;PWNED\u0007@example.com", "password": "<valid-password>"}
```
3. On successful authentication, `core/sessions/ldapauth/ldap.go:435` logs:
   `Successful LDAP login request for user victim<ESC>]0;PWNED<BEL>@example.com - admin`
4. When an operator tails/reviews this log in a terminal emulator that interprets OSC escape sequences, the terminal title (or other terminal state) is altered by attacker-controlled input, demonstrating the injection — the same primitive exploited in `CVE-2017-10784`.

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

**File:** core/sessions/ldapauth/ldap.go (L392-435)
```go
// CreateSession will forward the session request credentials to the
// LDAP server, querying for a user + role response if username and
// password match. The API call is blocking with timeout, so a sufficient timeout
// should allow the user to respond to potential MFA push notifications
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
```

**File:** core/sessions/oidcauth/oidc.go (L418-420)
```go
	sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
	sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
	oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)
```

**File:** core/capabilities/remote/utils_test.go (L109-119)
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
```
