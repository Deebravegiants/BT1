Confirmed: `unauth.POST("/sessions", sc.Create)` in [1](#0-0)  is a fully unauthenticated endpoint, invoking `AuthenticationProvider().CreateSession`, which for LDAP-configured nodes routes user-supplied credentials directly into `ldapAuthenticator.CreateSession`.

### Title
Log Injection via Unsanitized Login Email in LDAP Authenticator - (File: core/sessions/ldapauth/ldap.go)

### Summary
The unauthenticated `POST /sessions` login endpoint accepts an email/password pair and, for LDAP-backed nodes, passes the raw client-supplied email into a `%s`-formatted log line without sanitizing control characters, allowing an unprivileged remote client to inject forged log entries — the same bug class as CVE-2015-3200 (lighttpd `mod_auth` log injection via unescaped Basic-Auth credentials containing `\n`/NUL).

### Finding Description
The session-creation route is registered without any authentication middleware: [2](#0-1) . It forwards the request body (`sr.Email`, `sr.Password`) to the configured `AuthenticationProvider`, which for LDAP mode is `ldapAuthenticator.CreateSession` in [3](#0-2) .

On a successful bind, the authenticator logs the raw, attacker-controlled `sr.Email` directly via `%s` substitution into a free-text log message: [4](#0-3) 

Unlike `escapedEmail` (which only passes through `ldap.EscapeFilter`, an LDAP-filter escaper — not a log-safe escaper) used at lines 406–418, `sr.Email` here is fully unmodified user input. If it contains newline (`\n`), carriage return (`\r`), or other control/format characters, those characters are written verbatim into the application's structured log output at line 435, exactly analogous to how CVE-2015-3200 allowed injecting fake HTTP access-log lines by omitting the required colon and including `\n`/NUL in a Basic-Auth string. A similar unsanitized-input-into-log pattern also appears in `localLoginFallback` calls and the `oidcauth` equivalent, but the LDAP success path is the clearest instance of a free-text (non-structured-field) `%s` format injection point reachable pre-authentication.

Notably, the codebase already has an established mitigation for this exact bug class — `remote.SanitizeLogString`, used across the P2P/capabilities remote packages — [5](#0-4) , confirming maintainers recognize control-character log injection as a real risk, but this protection was not applied to the web-facing LDAP login path.

### Impact Explanation
An unauthenticated attacker can inject arbitrary newline-delimited fake entries into the node's authentication logs (e.g., fabricating a bogus "Successful LDAP login request for user admin@example.com - Admin" line), which can be used to frame other users, obscure genuine attack traces, or corrupt log-based alerting/SIEM parsing that relies on line-based delimiting. This does not itself grant account takeover or fund movement, so impact is limited to log integrity/log-forging (matching CVE-2015-3200's own Confidentiality:None/Integrity:High profile).

### Likelihood Explanation
High likelihood of triggerability: the `/sessions` endpoint is intentionally unauthenticated (needed for login) and rate-limited only by the generic unauthenticated rate limiter, not access-controlled otherwise, per [2](#0-1) . Any client can submit an email field containing `\n` in a JSON body; JSON strings can encode literal newlines as `\n` escapes that get decoded to raw newline bytes before being logged, so no special bypass is required. The condition only requires the node to be configured with `WebServer.AuthenticationMethod = 'ldap'` and a reachable LDAP directory that accepts (or errors gracefully on) the bind attempt — reachability is otherwise the same as the general login path.

### Recommendation
Sanitize or reject control/format characters (`\n`, `\r`, NUL, other non-printable bytes) from `sr.Email` before it is interpolated into any log message, or switch to passing it exclusively as a structured logging field (e.g., `lggr.Infow("Successful LDAP login", "user", sr.Email, "role", foundUser.Role)`) combined with a logger/encoder that escapes control characters in field values (most structured JSON loggers already do this safely, unlike `%s`-formatted free text). Reuse the existing `remote.SanitizeLogString` helper (or equivalent) at all points where user-supplied session/login fields are written into free-text log messages, including `core/sessions/oidcauth/oidc.go` and `core/sessions/localauth/orm.go`.

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'`.
2. Send an unauthenticated request: `POST /sessions` with body `{"email": "attacker@example.com\nINFO Successful LDAP login request for user admin@example.com - Admin", "password": "<valid-or-arbitrary>"}`.
3. If the LDAP bind succeeds (or via the `localLoginFallback` path for a matching local user), the injected string is written verbatim through `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` at [4](#0-3) , producing two log lines in the output where the operator expected one, the second falsely appearing to be a legitimate "admin" login record.

### Citations

**File:** core/web/router.go (L207-217)
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
```

**File:** core/sessions/ldapauth/ldap.go (L396-411)
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
