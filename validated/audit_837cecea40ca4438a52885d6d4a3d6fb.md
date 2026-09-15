Audit Report

## Title
LDAP CreateSession Authentication Bypass via Empty Password (Unauthenticated Bind) - (File: `core/sessions/ldapauth/ldap.go`)

## Summary
`ldapAuthenticator.CreateSession` forwards the client-supplied `sr.Password` field directly to `conn.Bind(searchBaseDN, sr.Password)` without ever checking that the password is non-empty. [1](#0-0)  The same unguarded pattern exists in `TestPassword`. [2](#0-1)  This is the exact root-cause pattern behind CVE-2022-37397: per RFC 4513 §5.1.2, a non-empty DN with a zero-length password is a defined "unauthenticated bind," and many LDAP/AD servers configured (by default or misconfiguration) to allow unauthenticated binds will report success without validating any credential.

## Finding Description
`SessionsController.Create` binds the raw JSON body into `sessions.SessionRequest{Email, Password}` with no server-side check for empty password, and passes it directly to `AuthenticationProvider().CreateSession(ctx, sr)`. [3](#0-2)  When `AuthenticationMethod` is `ldap`, `ldapAuthenticator.CreateSession` builds the bind DN from the attacker-controlled email and calls `conn.Bind(searchBaseDN, sr.Password)` with no guard against `sr.Password == ""`. [1](#0-0)  If `Bind` succeeds, the code proceeds to `FindUser`, and on success inserts a real `ldap_sessions` row and returns a valid session ID. [4](#0-3)  No code path in `ldap.go` or `client.go` rejects an empty password before it reaches `conn.Bind`; `CreateEphemeralConnection` only performs the node's own service-account bind, not any validation of end-user credentials. [5](#0-4) 

## Impact Explanation
If the operator's LDAP/AD server has anonymous or unauthenticated bind enabled — a known, documented AD behavior/misconfiguration and the exact precondition of CVE-2022-37397 — an attacker who knows or can enumerate a valid LDAP-mapped email can obtain a successful bind and be issued a real session with that user's actual role (potentially Admin), fully bypassing authentication. This maps to the in-scope "node API authentication or role bypass" impact category.

## Likelihood Explanation
Exploitability requires the upstream LDAP/AD server to be configured to permit unauthenticated binds; Chainlink's code performs no application-level mitigation against this well-known LDAP behavior class, so any deployment with `AuthenticationMethod = 'ldap'` against a permissive AD server is immediately exposed. The attack is triggerable by any unprivileged remote client via a single unauthenticated `POST /sessions` request with a known/guessed email and empty password field — no credentials, host access, or operator privileges required on the attacker's side.

## Recommendation
Add an explicit `if sr.Password == "" { return "", errors.New("password required") }` guard (and equivalent for `password` in `TestPassword`) at the top of `CreateSession` and `TestPassword` in `core/sessions/ldapauth/ldap.go`, before any call to `conn.Bind`, consistent with RFC 4513's recommendation to disable unauthenticated bind handling at the application layer.

## Proof of Concept
1. Configure a chainlink node with `WebServer.AuthenticationMethod = 'ldap'` pointed at an LDAP/AD server that permits unauthenticated binds.
2. Send `POST /sessions` with body `{"email":"known-admin@example.com","password":""}`.
3. `SessionsController.Create` forwards this unmodified to `ldapAuthenticator.CreateSession`, which calls `conn.Bind("uid=known-admin@example.com,ou=users,dc=...", "")`.
4. Against the permissively configured server, `Bind` returns nil (unauthenticated bind success); `FindUser` resolves the real role and a valid `ldap_sessions` row/session cookie is issued for the impersonated user — full auth bypass without knowing the real password. A Go unit test can mock `LDAPConn.Bind` to return nil for an empty-password call to demonstrate the missing guard directly against `ldapAuthenticator.CreateSession`.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L406-411)
```go
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

**File:** core/sessions/ldapauth/ldap.go (L503-514)
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
```

**File:** core/web/sessions_controller.go (L34-56)
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
```

**File:** core/sessions/ldapauth/client.go (L31-43)
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
}
```
