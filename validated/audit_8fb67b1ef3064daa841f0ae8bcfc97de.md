Audit Report

## Title
LDAP authentication bypass via zero-length (unauthenticated) Bind - (File: core/sessions/ldapauth/ldap.go)

## Summary
`ldapAuthenticator.CreateSession` and `ldapAuthenticator.TestPassword` in `core/sessions/ldapauth/ldap.go` pass the client-supplied password directly into `conn.Bind(searchBaseDN, password)` without first rejecting an empty password. Per RFC 4513 §5.1.2, an LDAP Bind with a non-empty DN and a zero-length password is treated by most LDAP/AD servers as an "unauthenticated bind," which returns success without validating any credential, allowing an attacker to authenticate as any known, real directory user without their password.

## Finding Description
`SessionRequest` has no validation/required tags on `Password`, so `POST /sessions` accepts an empty string. [1](#0-0) 
`SessionsController.Create` binds the raw JSON directly into `sr` and forwards it unmodified to `AuthenticationProvider().CreateSession`. [2](#0-1) 

In `CreateSession`, the code binds with `sr.Password` with zero validation that it is non-empty before calling `conn.Bind`: [3](#0-2) 
If the bind returns `nil` error (as happens with an unauthenticated bind against a server that permits it, a common default absent explicit hardening), execution proceeds to resolve the real user's role via `FindUser`, and if that email belongs to a legitimate, group-assigned user, a fully authenticated session is created and audit-logged as a successful login: [4](#0-3) [5](#0-4) 

The identical unguarded pattern exists in `TestPassword`: [6](#0-5) 

No code path in this file, in `LDAPConn`/`ldapClient.CreateEphemeralConnection` (`core/sessions/ldapauth/client.go`), or in `sessions.SessionRequest` rejects an empty password before it reaches `Bind`. The only bind performed with fixed credentials is the initial service-account bind in `CreateEphemeralConnection`; the user-supplied bind is completely unguarded. [7](#0-6) 

## Impact Explanation
This is a full authentication/role bypass (CWE-287/288): an unauthenticated remote attacker who knows or guesses a valid directory user's email can obtain a fully authenticated Chainlink node session with that user's real role (up to Admin) by submitting an empty-string password, without knowing the actual credential. This maps directly to the in-scope "node API authentication or role bypass" impact category, since it grants full API/session access as another user via the unauthenticated `POST /sessions` endpoint.

## Likelihood Explanation
Requires `WebServer.AuthenticationMethod = 'ldap'` and an upstream LDAP/AD server that has not explicitly disabled unauthenticated binds — a widely documented and common default per RFC 4513, not a Chainlink node misconfiguration. No credentials, network position, or prior access are needed beyond a single unauthenticated HTTP POST containing a guessable/known email, making this realistically and repeatably exploitable wherever LDAP auth is enabled.

## Recommendation
In both `CreateSession` and `TestPassword` in `core/sessions/ldapauth/ldap.go`, reject requests where `password` (or `sr.Password`) is empty before calling `conn.Bind`, returning the same generic "invalid credentials"/"unable to log in" error used for genuine bind failures to avoid a behavioral side-channel. Consider also validating the connection actually authenticated as the intended DN (not anonymous) if the LDAP library exposes that information.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` against an LDAP server that permits unauthenticated binds (default unless explicitly disabled).
2. Identify a real directory user's email who belongs to a configured RBAC group (e.g., `AdminUserGroupCN`).
3. Send `POST /sessions` with body `{"email":"victim@example.com","password":""}`.
4. `conn.Bind(dn, "")` at `core/sessions/ldapauth/ldap.go` line 408 succeeds (unauthenticated bind, `err == nil`); `FindUser` resolves the victim's role; a valid session is created and returned for the victim's account/role without knowing their password. A Go unit test can mock `LDAPConn.Bind` to return `nil` for an empty password (simulating unauthenticated-bind server behavior) and assert `CreateSession` incorrectly returns a valid session ID.

### Citations

**File:** core/sessions/session.go (L14-22)
```go
// SessionRequest encapsulates the fields needed to generate a new SessionID,
// including the hashed password.
type SessionRequest struct {
	Email          string `json:"email"`
	Password       string `json:"password"`
	WebAuthnData   string `json:"webauthndata"`
	WebAuthnConfig WebAuthnConfiguration
	SessionStore   *WebAuthnSessionStore
}
```

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

**File:** core/sessions/ldapauth/ldap.go (L413-420)
```go
	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L440-456)
```go
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
```

**File:** core/sessions/ldapauth/ldap.go (L503-518)
```go
// TestPassword tests if an LDAP login bind can be performed with provided credentials, returns nil if success
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
	l.lggr.Infof("Error binding user authentication request in TestPassword call LDAP Bind: %v", err)
```

**File:** core/sessions/ldapauth/client.go (L31-42)
```go
// CreateEphemeralConnection returns a valid, active LDAP connection for upstream Search and Bind queries
func (l *ldapClient) CreateEphemeralConnection() (LDAPConn, error) {
	conn, err := ldap.DialURL(l.config.ServerAddress())
	if err != nil {
		return nil, fmt.Errorf("failed to Dial LDAP Server: %w", err)
	}
	// Root level root user auth with credentials provided from config
	bindStr := l.config.BaseUserAttr() + "=" + l.config.ReadOnlyUserLogin() + "," + l.config.BaseDN()
	if err := conn.Bind(bindStr, l.config.ReadOnlyUserPass()); err != nil {
		return nil, fmt.Errorf("unable to login as initial root LDAP user: %w", err)
	}
	return conn, nil
```
