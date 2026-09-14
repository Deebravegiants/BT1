Confirmed: `SessionRequest.Password` has no `binding:"required"` tag and no non-empty validation exists anywhere in `sessions_controller.go` or `session.go` before it's passed to the LDAP `Bind` call.

### Title
LDAP Authentication Bypass via Empty-Password Unauthenticated Bind - (File: core/sessions/ldapauth/ldap.go)

### Summary
`ldapAuthenticator.CreateSession` (and `TestPassword`) forward the client-supplied `sr.Password` directly to `conn.Bind(searchBaseDN, sr.Password)` without ever checking that the password is non-empty. Per RFC 4513 §5.1.2, an LDAP simple bind with a non-empty DN and a zero-length password is defined as an "unauthenticated bind," which most LDAP servers accept as **successful** if anonymous/unauthenticated binds are permitted — regardless of the actual account password. Any unprivileged client who knows (or guesses) a valid Chainlink node user email can authenticate as that user with an empty password field.

### Finding Description
`SessionsController.Create` (`core/web/sessions_controller.go:29-68`) binds the raw JSON body into `sessions.SessionRequest` with `c.ShouldBindJSON(&sr)` and no `binding:"required"` constraint on `Password` [1](#0-0) , and `SessionRequest.Password` has no validation logic anywhere in `core/sessions/session.go` [2](#0-1) .

It is then passed straight into `ldapAuthenticator.CreateSession`: [3](#0-2) 

If `sr.Password` is `""`, `conn.Bind(searchBaseDN, "")` becomes an RFC-4513 "unauthenticated bind." Many LDAP servers (OpenLDAP, AD, etc., unless explicitly hardened) accept this as success without validating the DN's real credentials — exactly the prerequisite condition ("underlying LDAP server permits anonymous bind") called out in the reference Apache Druid advisory. Because `err` from `Bind` will be `nil`, the code proceeds to call `l.FindUser(ctx, escapedEmail)` and, on success, creates a valid `ldap_sessions` row and returns a legitimate session cookie/token for that user — no password was ever verified. `FindUser` does not re-check credentials, only group membership [4](#0-3) .

The same flaw exists in `TestPassword`, used for API-token validation flows: [5](#0-4) 

By contrast, `localauth/orm.go`'s `CreateSession` uses `utils.CheckPasswordHash` against a locally stored hash and never forwards credentials to an external bind call [6](#0-5) , so it is not affected — this is specific to the LDAP driver's reliance on the remote bind response.

### Impact Explanation
An unauthenticated remote attacker who knows any valid LDAP-managed user's email (often a corporate email address, easily guessable/enumerable) can obtain a fully authenticated Chainlink node session with that user's role (Admin/Edit/Run/View) simply by submitting an empty `password` field — completely bypassing authentication when the backing LDAP server allows unauthenticated binds (a common default/legacy configuration). This grants access to node management APIs, job specs, bridges, keys metadata, and potentially admin-level actions if the impersonated account is privileged.

### Likelihood Explanation
Exploitation requires only a POST to `/sessions` with a known email and an empty password string — no special access is needed, and the request path (`SessionsController.Create` → `AuthenticationProvider().CreateSession`) is reachable by any unprivileged network client that can reach the node's web server. The only external dependency is that the operator's LDAP server allows anonymous/unauthenticated binds, which is a common (often default) LDAP server posture, mirroring the exact prerequisite in the referenced CVE-2026-23906 advisory.

### Recommendation
Reject empty-password LDAP bind attempts before calling `conn.Bind`, e.g., in `ldapAuthenticator.CreateSession` and `TestPassword`, add an explicit check such as `if sr.Password == "" { return "", errors.New("invalid credentials") }` prior to constructing/using the bind call. Additionally, add `binding:"required"` on `SessionRequest.Password` in `core/sessions/session.go` and validate non-empty password server-side as defense in depth.

### Proof of Concept
1. Configure `[WebServer.LDAP]` with an upstream LDAP server that permits unauthenticated/anonymous binds (default OpenLDAP or many misconfigured AD deployments).
2. Identify a valid Chainlink node user email present in the LDAP directory (e.g., `victim@example.com`).
3. Send:
```
POST /sessions
Content-Type: application/json

{"email": "victim@example.com", "password": ""}
```
4. `ldapAuthenticator.CreateSession` calls `conn.Bind("uid=victim@example.com,...", "")`, which the LDAP server accepts as an unauthenticated bind (`err == nil`).
5. `FindUser` resolves the user's group/role, a new row is inserted into `ldap_sessions`, and a valid session cookie is returned — granting full access as `victim@example.com` without ever knowing their password.

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

**File:** core/sessions/ldapauth/ldap.go (L115-123)
```go
func (l *ldapAuthenticator) FindUser(ctx context.Context, email string) (sessions.User, error) {
	email = strings.ToLower(email)

	// First check for the supported local admin users table
	var foundLocalAdminUser sessions.User
	checkErr := l.ds.GetContext(ctx, &foundLocalAdminUser, "SELECT * FROM users WHERE lower(email) = lower($1)", email)
	if checkErr == nil {
		return foundLocalAdminUser, nil
	}
```

**File:** core/sessions/ldapauth/ldap.go (L405-411)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L504-517)
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
	if err == nil {
		return nil
	}
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
