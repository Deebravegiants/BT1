### Title
LDAP Authentication Allows Unauthenticated Bind via Empty Password on `CreateSession` - ([File: core/sessions/ldapauth/ldap.go])

### Summary
`ldapAuthenticator.CreateSession` forwards attacker-supplied `sessions.SessionRequest.Email` and `Password` directly into an LDAP `Bind` call without validating that the password is a non-empty string, mirroring the exact root cause described in the MISP LDAP authentication bypass (CVE-2026-85216).

### Finding Description
`CreateSession` builds a bind DN from the user-supplied email and calls `conn.Bind(searchBaseDN, sr.Password)` with no prior check that `sr.Password` is non-empty: [1](#0-0) 

`sessions.SessionRequest` declares `Password string` with no length/emptiness constraint, and unlike `sessions.ValidateAndHashPassword` (used for local admin user creation) there is no equivalent validation applied to LDAP login requests before the credential is dispatched to the LDAP server: [2](#0-1) 

The same unauthenticated-bind pattern exists in `TestPassword`, which is reachable from the API-token creation flow: [3](#0-2) 

This is structurally identical to the reported MISP bug: a custom authenticator (`ldapAuthenticator`) that "replaces" normal credential validation but does not reject empty/invalid password values before calling the LDAP bind primitive. Per RFC 4513 §5.1.2, an LDAP bind with a non-empty DN and an empty password is defined as an "unauthenticated bind," and many LDAP servers (unless explicitly hardened) will return success for a valid DN with an empty password. If the configured directory permits unauthenticated binds, `conn.Bind(searchBaseDN, "")` can succeed for any email that maps to a valid DN, allowing session creation for that user without knowledge of their password.

I could not directly verify server-side behavior of the specific `go-ldap/ldap/v3` client wrapper (`LDAPClient`/`CreateEphemeralConnection`) for how it forwards an empty password to `conn.Bind`, since the underlying implementation file was not returned by search; the vulnerability's exploitability therefore depends on the target LDAP server's configuration (whether unauthenticated binds are permitted), which is consistent with how the original MISP advisory itself is conditioned on the LDAP server accepting unauthenticated binds.

### Impact Explanation
If successfully triggered, an unauthenticated remote attacker who knows or can enumerate a valid directory user's email could obtain a valid chainlink node session (`ldap_sessions` row) and impersonate that user, inheriting whatever role (`admin`, `edit`, `run`, `view`) is mapped from the LDAP group membership. An attacker impersonating an admin user could read secrets, modify node configuration, or trigger job runs — comparable in severity to the original MISP bypass.

### Likelihood Explanation
Exploitability is gated on the upstream LDAP server allowing unauthenticated binds (a non-default but not uncommon misconfiguration), so this is not universally exploitable out of the box, but the chainlink code path itself performs no defense-in-depth check to prevent it, unlike the local/OIDC password paths which always run `utils.CheckPasswordHash` against a stored bcrypt hash. The `NewLDAPAuthenticator` constructor enforces TLS in production but does not enforce or verify that unauthenticated binds are disabled server-side: [4](#0-3) 

### Recommendation
Add an explicit rejection of empty (or non-string/whitespace-only) passwords in `CreateSession` and `TestPassword` before calling `conn.Bind`, e.g. return an error immediately if `sr.Password == ""` (and similarly for `password == ""` in `TestPassword`), so the LDAP server is never given the opportunity to interpret the request as an unauthenticated bind.

### Proof of Concept
1. Identify (or guess) a valid directory user's email that maps into the configured `BaseUserAttr`/`UsersDN`/`BaseDN` search DN.
2. POST to `/sessions` with `{"email": "<valid-user-email>", "password": ""}`.
3. `CreateSession` builds `searchBaseDN` and calls `conn.Bind(searchBaseDN, "")`: [5](#0-4) 
4. If the LDAP server accepts unauthenticated binds for that DN, `conn.Bind` returns no error, `FindUser` resolves the role, and a session is created and returned to the attacker: [6](#0-5)

### Citations

**File:** core/sessions/ldapauth/ldap.go (L74-90)
```go
	// If not chainlink dev and not tls, error
	if !dev && !ldapCfg.ServerTLS() {
		return nil, errors.New("LDAP Authentication driver requires TLS when running in Production mode")
	}

	// Ensure all RBAC role mappings to LDAP Groups are defined, and required fields populated, or error on startup
	if ldapCfg.AdminUserGroupCN() == "" || ldapCfg.EditUserGroupCN() == "" ||
		ldapCfg.RunUserGroupCN() == "" || ldapCfg.ReadUserGroupCN() == "" {
		return nil, errors.New("LDAP Group mapping from server group name for all local RBAC role required. Set group names for `_UserGroupCN` fields")
	}
	if ldapCfg.ServerAddress() == "" {
		return nil, errors.New("LDAP ServerAddress config required")
	}
	if ldapCfg.ReadOnlyUserLogin() == "" {
		return nil, errors.New("LDAP ReadOnlyUserLogin config required")
	}

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

**File:** core/sessions/ldapauth/ldap.go (L413-456)
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
```

**File:** core/sessions/ldapauth/ldap.go (L503-517)
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
```

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
