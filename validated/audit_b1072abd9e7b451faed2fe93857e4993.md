### Title
Log Forging via Unsanitized Email in LDAP Authentication Login Flow - (File: core/sessions/ldapauth/ldap.go)

### Summary
The public, unauthenticated `POST /sessions` login endpoint accepts a user-supplied `email` field and forwards it unmodified into several `logger` calls in the LDAP authentication provider. Unlike the sibling OIDC provider, which explicitly strips `\n`/`\r` from the email before logging, the LDAP provider logs the raw, attacker-controlled string, allowing an unauthenticated caller to inject newlines/control characters into the node's log stream (CWE-117 Log Injection / Log Forging), directly analogous to the reported `generator-jhipster-kotlin` advisory.

### Finding Description
The session-creation route is registered without authentication: [1](#0-0) 

`SessionsController.Create` binds the JSON body straight into `clsessions.SessionRequest` and passes `sr.Email` unmodified to the authentication provider: [2](#0-1) 

When LDAP authentication is configured, `ldapAuthenticator.CreateSession` logs the raw `sr.Email` on a successful login without any sanitization: [3](#0-2) 

On failed/edge paths, `FindUser` (invoked internally from `CreateSession`) also logs the caller-supplied `email` value directly into `Warnf`/`Errorf` format strings: [4](#0-3) 

Only LDAP-metacharacter escaping is applied via `ldap.EscapeFilter` for use in the LDAP search filter — this does not strip newline (`\n`) or carriage-return (`\r`) characters, so the value logged still carries any injected control characters: [5](#0-4) 

By contrast, the OIDC authentication provider's equivalent `CreateSession` function explicitly sanitizes the email before logging it, proving the codebase is aware of this class of bug and mitigates it in one path but not the other: [6](#0-5) 

The local-auth `orm.CreateSession` implementation similarly logs `sr.Email` without CRLF sanitization, though via a structured field (`o.lggr.With("user", user.Email)`/`map[string]any` audit calls) rather than raw string interpolation into free text: [7](#0-6) 

### Impact Explanation
An unauthenticated attacker can submit crafted `email` values (e.g., containing `\n` or `\r`) to `POST /sessions`. When the node is configured with LDAP auth, these values are written verbatim into the application's log output via `Infof`/`Warnf`/`Errorf` calls, letting an attacker forge fake log lines, spoof other log entries, or corrupt log parsing/SIEM pipelines. This matches CWE-117 and the CVSS vector of the referenced advisory (network-reachable, no privileges or user interaction required, integrity impact limited to log data, no confidentiality/availability impact).

### Likelihood Explanation
High likelihood of reachability: the `/sessions` endpoint is intentionally public (rate-limited but unauthenticated) since it is the login endpoint itself, and LDAP is a supported, documented authentication mode. Any deployment using LDAP auth (`config.LDAP`) is exposed by simply submitting a login request with a crafted email — no valid credentials or account are required to trigger the vulnerable log statements in `FindUser`/`CreateSession`.

### Recommendation
Sanitize (strip `\n`/`\r`, and/or restrict to printable/escaped characters) any user-supplied `email` value before interpolating it into log messages in `core/sessions/ldapauth/ldap.go` (`CreateSession`, `FindUser`, and related methods), mirroring the sanitization already implemented in `core/sessions/oidcauth/oidc.go`. Consider applying the same to `core/sessions/localauth/orm.go` for defense in depth, and prefer structured logging fields over string-formatted interpolation for user-controlled values throughout.

### Proof of Concept
1. Configure a Chainlink node with LDAP authentication enabled.
2. Send an unauthenticated request:
```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"attacker@evil.com\n2026-09-13T00:00:00Z level=info msg=\"Successful LDAP login request for user admin@internal.com - admin\"","password":"anything"}
```
3. Observe that the injected newline and forged fake "successful admin login" line appears verbatim in the node's log output (via `l.lggr.Infof`/`Warnf` in `ldap.go`), forging a log entry that did not actually occur.

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

**File:** core/sessions/ldapauth/ldap.go (L173-194)
```go
	if len(result.Entries) == 0 {
		// Provided email is not present in upstream LDAP server, local admin CLI auth is supported
		// So query and check the users table as well before failing
		var localUserRole sessions.UserRole
		if err = l.ds.GetContext(ctx, &localUserRole, "SELECT role FROM users WHERE email = $1", email); err != nil {
			// Above query for local user unsuccessful, return error
			l.lggr.Warnf("No local users table user found with email %s", email)
			return sessions.User{}, errors.New("no users found with provided email")
		}

		// If the above query to the local users table was successful, return that local user's role
		return sessions.User{
			Email: email,
			Role:  localUserRole,
		}, nil
	}

	// Populate found user by email and role based on matched group names
	userRole, err := l.groupSearchResultsToUserRole(result.Entries)
	if err != nil {
		l.lggr.Warnf("User '%s' found but no matching assigned groups in LDAP to assume role", email)
		return sessions.User{}, err
```

**File:** core/sessions/ldapauth/ldap.go (L404-436)
```go

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

**File:** core/sessions/localauth/orm.go (L144-162)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	lggr := o.lggr.With("user", user.Email)
	lggr.Debugw("Found user")

	// Do email and password check first to prevent extra database look up
	// for MFA tokens leaking if an account has MFA tokens or not.
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		o.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```
