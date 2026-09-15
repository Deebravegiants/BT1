## Finding

### Title
LDAP Authentication Bypass via Unauthenticated Bind with Empty Password - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The LDAP authentication path in `ldapAuthenticator.CreateSession` and `ldapAuthenticator.TestPassword` forwards the client-supplied `sr.Password` directly to `conn.Bind(searchBaseDN, sr.Password)` without first checking that the password is non-empty. [1](#0-0) 

### Finding Description
Per LDAP protocol semantics (RFC 4513 §5.1.2 "Unauthenticated Bind Mechanism of Simple Bind"), a Bind request that supplies a non-empty DN but a zero-length password is defined as an *unauthenticated* bind. Many LDAP server implementations honor this and return a success response for such a request without actually validating any credential, since no password was presented to check. The `chainlink` LDAP authenticator's `CreateSession` builds `searchBaseDN` from the client-controlled email and then calls: [2](#0-1) 

There is no guard rejecting an empty `sr.Password` before the call to `conn.Bind`, so if the configured upstream LDAP server implements the RFC-4513 unauthenticated-bind fallback (a common, spec-compliant default unless explicitly disabled with a server-side policy), an attacker who submits a known user's email with an **empty** password string will receive a successful `Bind`. The code then treats this as a valid login, looks up the user's role via `FindUser`, and creates a full session in the `ldap_sessions` table with that user's role — including potentially an admin account — without ever verifying a real password. [3](#0-2) 

The same unguarded pattern exists in `TestPassword`, which is also reachable by unprivileged/authenticated non-admin users through the password-change API flow: [4](#0-3) 

This is conceptually the same root-cause bug class as CVE-2020-26168: the LDAP authentication logic does not properly and unconditionally verify that a non-empty, matching secret was supplied before treating an LDAP bind response as proof of identity.

### Impact Explanation
If exploitable against the configured LDAP directory (i.e., the directory does not explicitly disable unauthenticated binds), an unprivileged, unauthenticated remote attacker can obtain a fully valid Chainlink node web/API session for any known user email — including admin accounts — by submitting an empty password. This grants full node API access (job management, key/bridge configuration, fund-moving actions depending on role), a complete authentication bypass.

### Likelihood Explanation
Likelihood depends on the deployed LDAP server's configuration. Unauthenticated binds are the RFC-defined default behavior for simple bind requests carrying an empty password, and many directory servers (e.g. OpenLDAP) allow this unless an administrator has explicitly set `disallow bind_anon` or similar hardening. Because the Chainlink code performs no application-level check to reject empty passwords before delegating trust entirely to the LDAP server's Bind response, any deployment using a non-hardened LDAP server is exposed. The email is attacker-guessable/enumerable and is escaped/lower-cased before use, so the DN construction itself is not the bottleneck — only the password check is missing.

### Recommendation
Add an explicit application-level rejection of empty/zero-length passwords before calling `conn.Bind` in both `CreateSession` and `TestPassword` in `core/sessions/ldapauth/ldap.go`, e.g.:
```go
if sr.Password == "" {
    return "", errors.New("password cannot be empty")
}
```
This closes off reliance on the LDAP server's own anonymous/unauthenticated-bind policy and ensures the node itself never accepts an empty credential as a successful authentication, independent of upstream server configuration.

### Proof of Concept
1. Identify or guess the email of an existing LDAP-mapped user (e.g., an admin group member) on a target Chainlink node configured with LDAP auth against a server that permits unauthenticated binds (RFC 4513 default).
2. Send a login/session request (`POST` to the sessions endpoint backing `sessions.AuthenticationProvider.CreateSession`) with:
```json
{"email": "admin@example.com", "password": ""}
```
3. `ldapAuthenticator.CreateSession` calls `conn.Bind(searchBaseDN, "")`; the LDAP server treats this as an unauthenticated bind and returns success.
4. `FindUser` resolves the admin's role from group membership, and a valid `ldap_sessions` row / session cookie is issued for the admin account without ever having supplied a correct password.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L396-456)
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
