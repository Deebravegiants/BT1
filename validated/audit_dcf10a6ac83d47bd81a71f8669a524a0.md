### Title
Unsanitized email input from unauthenticated `/sessions` endpoint is written into log lines, enabling log injection/forging - (File: core/sessions/ldapauth/ldap.go)

### Summary
Chainlink's Gin router registers `POST /sessions` in an unauthenticated route group (`unauth.POST("/sessions", sc.Create)`), which forwards the raw, attacker-controlled `email`/`password` fields to `AuthenticationProvider().CreateSession`. When the LDAP authentication driver is configured, the `sr.Email` value is interpolated directly into `Infof`-style log messages without any control-character sanitization, letting an unauthenticated client inject characters (e.g., CR/LF) into the node's log stream — the same underlying bug class as the reported Gin advisory (CWE-116/117, unsanitized input reaching the logger causing arbitrary log-line injection).

### Finding Description
The session-creation endpoint is intentionally reachable without authentication: [1](#0-0) 

`SessionsController.Create` binds the JSON body straight into `clsessions.SessionRequest` and passes it, unmodified, to the configured `AuthenticationProvider`: [2](#0-1) 

In the LDAP driver's `CreateSession`, the raw `sr.Email` (not the filter-escaped/lowercased `escapedEmail` variable used elsewhere in the same function) is formatted directly into a log message via `Infof`: [3](#0-2) 

Because Go's `%s` verb performs no escaping of control characters, any user-supplied email string containing newline (`\n`)/carriage-return (`\r`) sequences (or terminal escape sequences) is written verbatim into the log output stream by `l.lggr.Infof(...)`. This is the classic CWE-117 log forging pattern flagged by the Gin advisory: unsanitized externally-controlled input is passed straight to a logging call rather than being redacted or structured. Note that elsewhere in this codebase the project already recognizes this risk class and defends against it — e.g. the gateway/vault handler explicitly asserts that raw request params must never leak into logs, and `core/web/router.go`'s custom `loggerFunc`/`readSanitizedJSON`/`redact` helpers exist specifically to avoid putting raw, unredacted request bodies into log lines: [4](#0-3) [5](#0-4) 

The LDAP `CreateSession` path does not follow this same discipline for the success/failure log lines that embed `sr.Email` directly.

### Impact Explanation
An unauthenticated remote attacker can inject arbitrary log lines/content into the node's operator logs by submitting crafted `email` values containing newline or control characters to `POST /sessions`. This can be used to forge fake log entries (e.g., spoofing a "Successful LDAP login request for user X" audit-adjacent log line for a different, legitimate user), pollute or corrupt log-processing pipelines (SIEM/log parsers that assume one JSON/line per log entry), and potentially facilitate log-based social engineering of operators reviewing logs. This matches the CVSS vector of the underlying report: no confidentiality/availability impact, but integrity of the log stream (`I:H`) is affected, reachable pre-authentication over the network (`AV:N`, `PR:N`, `UI:N`).

### Likelihood Explanation
High likelihood of reachability: the `/sessions` endpoint is explicitly unauthenticated (only rate-limited), so any remote, unprivileged client can reach `ldapAuthenticator.CreateSession` when the node is configured to use the LDAP authentication driver. No special conditions are needed beyond LDAP auth being enabled, and the injected email need not even be a valid LDAP filter value to reach the vulnerable log line (the failure paths and the final success log both use the attacker-supplied string).

### Recommendation
Sanitize or structurally encode all user-controlled fields (especially `sr.Email`) before they are ever passed to a formatted log call. Prefer structured logging fields (`lggr.Infow("Successful LDAP login request", "email", sr.Email, "role", foundUser.Role)`) combined with a sink/encoder that escapes control characters, or explicitly strip/escape `\r`, `\n`, and other non-printable characters (mirroring the existing `remote.SanitizeLogString` helper already used elsewhere in this codebase) before formatting into any `%s`-based log message. Apply this consistently across `core/sessions/ldapauth/ldap.go` and `core/sessions/oidcauth/oidc.go`, which contain similar `Infof`/`Errorf` calls embedding user-supplied email/username strings.

### Proof of Concept
1. Configure the node with LDAP authentication enabled.
2. Send `POST /sessions` with body: `{"email":"attacker@example.com\n2026-09-14T00:00:00Z INFO Successful LDAP login request for user admin@example.com - admin","password":"anything"}`.
3. Observe the node's log output: the injected string is written verbatim into the log stream via `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` (or the earlier `Infof` bind-failure line), producing a forged log entry that appears to originate from the node itself, without requiring any authentication.

### Citations

**File:** core/web/router.go (L207-218)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
}
```

**File:** core/web/router.go (L588-606)
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

**File:** core/sessions/ldapauth/ldap.go (L406-435)
```go
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L1044-1058)
```go
	invalidParamsLogs := logs.FilterMessage("invalid params")
	entries := invalidParamsLogs.All()
	require.Len(t, entries, 1, "expected exactly one 'invalid params' log entry")
	assert.Equal(t, zapcore.ErrorLevel, entries[0].Level)
	assert.Equal(t, req.ID, entries[0].ContextMap()["requestID"])
	assert.NotContains(t, entries[0].ContextMap(), "params", "raw params must not be logged")

	for _, e := range logs.All() {
		assert.NotContains(t, e.Message, marker)
		for k, v := range e.ContextMap() {
			if s, ok := v.(string); ok {
				assert.NotContains(t, s, marker, "log field %q must not contain raw request params", k)
			}
		}
	}
```
