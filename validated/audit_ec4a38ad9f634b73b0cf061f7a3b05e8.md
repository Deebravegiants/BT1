### Title
Log injection via unescaped user-controlled email in LDAP login logging - (File: core/sessions/ldapauth/ldap.go)

### Summary
The Keycloak advisory (CVE-2023-6484) describes writing unsanitized, attacker-controlled WebAuthn error/login data into logs, enabling log injection/forging. Chainlink's `ldapAuthenticator.CreateSession` has the same bug class: the unauthenticated `/sessions` login endpoint accepts a raw `email` field and writes it directly into a formatted log message without stripping control characters such as `\r`/`\n`, unlike the equivalent OIDC code path which explicitly sanitizes the same value.

### Finding Description
The public, unauthenticated login endpoint `POST /sessions` is wired to `SessionsController.Create`, which binds the JSON body into `clsessions.SessionRequest{Email, Password, ...}` and forwards it unmodified to the configured `AuthenticationProvider().CreateSession(ctx, sr)`: [1](#0-0) [2](#0-1) 

When the LDAP authenticator is configured, `sr.Email` (fully attacker-controlled, no CRLF stripping) flows into `ldapAuthenticator.CreateSession`, where it is interpolated directly into a `%s`-formatted log message on the success path: [3](#0-2) 

and on error/lookup paths as well: [4](#0-3) 

This is the same root cause pattern as GHSA-j628-q885-8gr5: user-supplied authentication-flow string data reaches a text-formatted log sink (`Infof`) without escaping newlines/control characters, so a malicious `email` value containing `\r\n` (or ANSI escape sequences) can inject fake log lines, forge additional "log entries", or corrupt log parsing/SIEM ingestion.

Notably, the codebase demonstrates awareness of exactly this risk in the sibling OIDC authenticator, where the equivalent value is explicitly sanitized before being logged: [5](#0-4) 

but the same fix was not applied to the LDAP path (nor is `escapedEmail`—which is LDAP-filter-escaped, not log-escaped—used at line 435; the raw `sr.Email` is used there). The local (non-LDAP/OIDC) authenticator uses zap's structured `With("user", ...)`/`Debugw` field-based logging rather than string formatting for the email value, which is comparatively safer but the LDAP path bypasses this by using `Infof`/`Errorf` with `%s` directly in the message text.

### Impact Explanation
Impact is limited to log integrity/observability, matching the Medium severity and `C:N/I:L/A:N` CVSS vector of the original advisory: an unauthenticated caller can forge or corrupt Chainlink node application log entries by submitting a crafted `email` value containing newline or control characters to `/sessions`. This can be used to spoof fake "Successful LDAP login" entries, obscure malicious activity, or break downstream log parsers/alerting pipelines that key off structured multi-line entries. It does not directly disclose secrets or bypass authentication.

### Likelihood Explanation
Likelihood is high for triggering the log write (every login attempt against an LDAP-backed deployment reaches this code, `AC:L`, `PR:N`, `UI:N`), but the LDAP authenticator is an optional, operator-enabled deployment mode—the impact is only realized on installations configured to use LDAP authentication. The endpoint itself is unauthenticated and rate-limited (`rl.Unauthenticated()`), similar to the original Keycloak login form.

### Recommendation
Sanitize `sr.Email` (and any other user-supplied value written via `%s`/`Infof`/`Errorf` string interpolation in `core/sessions/ldapauth/ldap.go`) by stripping/escaping `\r`, `\n`, and other control characters before logging, mirroring the sanitization already implemented in `core/sessions/oidcauth/oidc.go` (`strings.ReplaceAll(sr.Email, "\n"/"\r", "")`). Prefer structured logging fields (e.g., `lggr.Infow("Successful LDAP login request", "user", sr.Email, "role", foundUser.Role)`) over format-string interpolation so the logging encoder is responsible for safe escaping, consistent with `core/sessions/localauth/orm.go`'s use of `o.lggr.With("user", user.Email)`.

### Proof of Concept
1. Configure a Chainlink node with LDAP authentication enabled (`[WebServer.LDAP]`).
2. Send an unauthenticated request:
```
POST /sessions
Content-Type: application/json

{"email":"attacker@example.com\n2024-01-01T00:00:00Z\tINFO\tFAKE: Successful LDAP login request for user admin@example.com - admin","password":"x"}
```
3. Observe that `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` (core/sessions/ldapauth/ldap.go:435) writes the injected newline-delimited content into the log stream verbatim, producing a forged log line that appears as a separate, legitimate-looking entry (e.g., a fake admin login), which is not stripped the way the OIDC authenticator's equivalent code path strips it.

### Citations

**File:** core/web/sessions_controller.go (L34-60)
```go
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

**File:** core/sessions/ldapauth/ldap.go (L409-419)
```go
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
```

**File:** core/sessions/ldapauth/ldap.go (L435-435)
```go
	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)
```

**File:** core/sessions/oidcauth/oidc.go (L412-420)
```go
func (oi *oidcAuthenticator) CreateSession(ctx context.Context, sr clsessions.SessionRequest) (string, error) {
	foundUser, err := oi.localLoginFallback(ctx, sr)
	if err != nil {
		return "", err
	}

	sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
	sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
	oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)
```
