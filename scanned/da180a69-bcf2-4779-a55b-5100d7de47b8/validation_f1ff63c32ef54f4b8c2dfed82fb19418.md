## Title
LDAP unauthenticated ("empty password") bind allows authentication bypass in `ldapAuthenticator.CreateSession` - (File: `core/sessions/ldapauth/ldap.go`)

### Summary
The LDAP `CreateSession` login path binds to the upstream LDAP server using the client-supplied password with no check that the password is non-empty. Per RFC 4513 §5.1.2, a simple bind with a non-empty DN and a zero-length password is defined as an *unauthenticated bind*, and many LDAP servers (including common OpenLDAP configurations) return success for this operation without validating any credential. An unprivileged network client that knows (or guesses/enumerates) any valid user email can authenticate as that user by submitting an empty `password` field to the public `/sessions` endpoint, without knowing the real password. This is the same class of issue referenced by CVE-2020-14827 (MySQL Server LDAP Auth component allowing unauthorized access via low-privilege network access).

### Finding Description
`SessionsController.Create` binds the client-supplied JSON body directly into `sessions.SessionRequest` with no validation that `Password` is non-empty: [1](#0-0) 

`sessions.SessionRequest.Password` has no length/required validation tag: [2](#0-1) 

This request flows unauthenticated through the router to `SessionsController.Create` on `POST /sessions`: [3](#0-2) 

For the LDAP authentication provider, `CreateSession` performs the bind directly with the attacker-controlled password: [4](#0-3) 

If `sr.Password` is an empty string, `conn.Bind(searchBaseDN, "")` is a valid, non-error "unauthenticated bind" per the LDAP protocol for many server configurations, so `err` is `nil` and `returnErr` stays unset — the code proceeds as if the password were verified, then looks up the user's role via `FindUser` and issues a full session with that role: [5](#0-4) 

`TestPassword` (used elsewhere for credential re-verification, e.g. changing password/API tokens) has the identical pattern: [6](#0-5) 

By contrast, the local/OIDC-local authentication path never has this issue, because it always compares against a stored bcrypt hash rather than delegating to a bind call that itself defines empty-password as a valid (but unauthenticated) success case: [7](#0-6) 

### Impact Explanation
An attacker with no prior credentials who knows any valid LDAP-mapped user's email (often predictable, e.g. corporate email format) can obtain a fully authenticated session cookie with that user's role (`admin`, `edit`, `run`, or `view`) by submitting an empty password. If the targeted email belongs to an `admin`-role LDAP group member, this is a complete authentication bypass leading to full node compromise (job creation/deletion, key export flows, fund transfer endpoints gated by `RequiresAdminRole`/`RequiresEditRole`, etc.): [8](#0-7) [9](#0-8) 

### Likelihood Explanation
Exploitability depends on whether the deployed LDAP server permits unauthenticated/anonymous binds for the configured `searchBaseDN` — this is the RFC-defined default behavior for simple binds with empty passwords unless the LDAP server administrator has explicitly disabled it. This is a well-documented, commonly overlooked LDAP misconfiguration risk, and the chainlink code applies no defensive check (e.g., rejecting empty passwords before calling `Bind`) to prevent it, unlike best practice guidance for LDAP client implementations.

### Recommendation
Reject any `SessionRequest.Password` (and in `TestPassword`) that is empty before calling `conn.Bind`, returning an authentication failure immediately. This defends against unauthenticated LDAP bind regardless of server-side configuration, consistent with LDAP client security guidance (RFC 4513 §6.3.1) to never treat a zero-length-password bind as authenticating a real user.

### Proof of Concept
1. Deploy chainlink node with LDAP auth enabled against an LDAP server that permits unauthenticated binds for the configured base DN (default behavior unless explicitly disabled).
2. As an unauthenticated attacker, send:
```
POST /sessions
Content-Type: application/json

{"email":"admin@example.com","password":""}
```
3. `ldapAuthenticator.CreateSession` calls `conn.Bind(searchBaseDN, "")`, which the LDAP server treats as a successful unauthenticated bind (`err == nil`).
4. `FindUser` resolves `admin@example.com`'s LDAP group membership/role, and a valid session cookie is issued for that identity/role without the attacker ever knowing the real password.

### Citations

**File:** core/web/sessions_controller.go (L34-39)
```go
	session := sessions.Default(c)
	var sr clsessions.SessionRequest
	if err := c.ShouldBindJSON(&sr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("error binding json %w", err))
		return
	}
```

**File:** core/sessions/session.go (L16-22)
```go
type SessionRequest struct {
	Email          string `json:"email"`
	Password       string `json:"password"`
	WebAuthnData   string `json:"webauthndata"`
	WebAuthnConfig WebAuthnConfiguration
	SessionStore   *WebAuthnSessionStore
}
```

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

**File:** core/web/router.go (L245-257)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	{
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)
```

**File:** core/sessions/ldapauth/ldap.go (L404-411)
```go

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L413-457)
```go
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

**File:** core/sessions/ldapauth/ldap.go (L511-518)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
	if err == nil {
		return nil
	}
	l.lggr.Infof("Error binding user authentication request in TestPassword call LDAP Bind: %v", err)
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

**File:** core/web/auth/auth.go (L236-253)
```go
// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```
