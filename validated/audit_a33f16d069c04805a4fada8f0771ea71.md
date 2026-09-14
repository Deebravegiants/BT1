### Title
Empty-password LDAP bind allows authentication bypass via unauthenticated bind - (File: core/sessions/ldapauth/ldap.go)

### Summary
`ldapAuthenticator.CreateSession` forwards the user-supplied password from the `/sessions` login request directly into an LDAP `Bind()` call with no check for an empty password, matching the CVE-2020-2300 bug class (Jenkins AD plugin failing to reject empty-password ADSI binds).

### Finding Description
`SessionRequest.Password` is a plain string with no non-empty validation [1](#0-0) . The web login endpoint binds JSON directly into this struct and passes it straight to the authentication provider without checking for an empty password [2](#0-1) .

In the LDAP authentication provider, `CreateSession` takes `sr.Password` and calls `conn.Bind(searchBaseDN, sr.Password)` with no check that `sr.Password` is non-empty before doing so: [3](#0-2) 

Per LDAP semantics (RFC 4513 §5.1.2), a bind request that supplies a non-empty DN together with a zero-length password is defined as an "unauthenticated bind," which many LDAP/AD servers will report as successful without actually validating any credential — this is exactly the mechanism underlying CVE-2020-2300, where Jenkins' AD plugin forwarded an empty password to ADSI/LDAP and the directory happily returned "authenticated." If `conn.Bind` here returns no error for an empty password (which is the standard behavior of many LDAP servers, and is only preventable by explicit client-side rejection), the code proceeds to treat the login as valid: it looks up the user's real role via `FindUser` and creates a full authenticated session for that user's real email/role [4](#0-3)  — i.e. anyone who knows/guesses a valid user email can obtain a session for that user without ever supplying a correct password. No other layer of the codebase (`web/sessions_controller.go`, `session.go`) performs an empty-password rejection to compensate.

Contrast this with the local/OIDC "fallback" authenticator paths, which use `utils.CheckPasswordHash` against a bcrypt hash — bcrypt will reject an empty password against any properly-hashed value, so those paths are not vulnerable to this same class [5](#0-4) . The LDAP path is unique in delegating to a live network bind operation whose "success" semantics for empty passwords are entirely server-dependent, and the code does nothing to normalize/reject that case.

### Impact Explanation
If the target LDAP/AD server allows unauthenticated binds (a common default/legacy configuration, and precisely the scenario in the original CVE), an unprivileged remote attacker with no valid credentials can create a full authenticated Chainlink node web session as any known user (including admins), by POSTing `{"email":"<victim>","password":""}` to `/sessions`. This is a complete authentication bypass allowing privilege escalation to Admin, exposing job/fund-movement-capable functionality.

### Likelihood Explanation
Likelihood depends on the external LDAP/AD server's configuration (whether it permits unauthenticated binds for the searched DN) — this is a real-world common misconfiguration, which is the entire reason CVE-2020-2300 was rated Critical (9.8) despite similarly depending on server-side behavior. The chainlink code path performs zero client-side mitigation, so the exposure is present in this repo whenever LDAP auth is enabled and the connected directory has unauthenticated binds allowed (default in many OpenLDAP/AD setups unless explicitly disabled).

### Recommendation
In `ldapAuthenticator.CreateSession` (and `TestPassword`), explicitly reject empty passwords before calling `conn.Bind`, e.g.:
```go
if sr.Password == "" {
    return "", errors.New("password must not be empty")
}
```
This should be added both in `core/sessions/ldapauth/ldap.go` `CreateSession` [6](#0-5)  and `TestPassword` [7](#0-6) , mirroring the fix applied by Jenkins for CVE-2020-2300 (explicitly disallowing empty passwords regardless of what the upstream directory would otherwise return).

### Proof of Concept
1. Configure the node with LDAP authentication (`ldapAuth`) pointed at a directory server that permits unauthenticated binds (or one where the bind DN pattern resolves and the server ignores/accepts empty password per RFC 4513 unauthenticated-bind semantics).
2. Send:
```
POST /sessions
Content-Type: application/json

{"email":"admin@example.com","password":""}
```
3. `ldapAuthenticator.CreateSession` calls `conn.Bind(searchBaseDN, "")`, which the server treats as an unauthenticated bind and returns success; `FindUser` then resolves the real admin role and a valid session cookie is issued for the admin account without any correct credential ever being supplied [8](#0-7) .

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L396-440)
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
```

**File:** core/sessions/ldapauth/ldap.go (L504-514)
```go
func (l *ldapAuthenticator) TestPassword(ctx context.Context, email string, password string) error {
	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		return errors.New("unable to establish connection to LDAP server with provided URL and credentials")
	}
	defer conn.Close()

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
```

**File:** core/sessions/localauth/orm.go (L159-162)
```go
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```
