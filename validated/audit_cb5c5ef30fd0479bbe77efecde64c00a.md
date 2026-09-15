Audit Report

## Title
LDAP Session Authentication Accepts Empty Password via Unauthenticated Bind, Allowing Login as Any Known User - (File: core/sessions/ldapauth/ldap.go)

## Summary
`ldapAuthenticator.CreateSession` passes the caller-supplied `sr.Password` directly into `conn.Bind(searchBaseDN, sr.Password)` without ever checking whether it is empty. Per RFC 4513 §5.1.2, a simple bind with a non-empty DN and a zero-length password is defined as an "unauthenticated bind," which many LDAP server configurations treat as a successful bind, allowing an attacker who only knows a valid user's email to obtain a persisted Chainlink session for that user.

## Finding Description
In `CreateSession`, the bind DN is built from the caller-controlled `sr.Email` and immediately used with the raw `sr.Password` in `conn.Bind`, with no guard against an empty password: [1](#0-0) . If the bind returns no error, the code proceeds to resolve the user's role via `FindUser` and unconditionally inserts a new row into `ldap_sessions`, returning a valid session ID to the caller: [2](#0-1) . This contrasts with the sibling `localauth` implementation, which always verifies the password against a stored hash before issuing a session: [3](#0-2) . This code path is reachable from the unauthenticated `/sessions` HTTP endpoint, which only requires a JSON body with `email`/`password`: [4](#0-3) . A search across the `ldapauth` package confirms there is no explicit empty-password check anywhere in the reachable code (`client.go`'s `CreateEphemeralConnection` only performs the operator's own read-only service-account bind, not user validation): [5](#0-4) .

The root cause and the missing defense-in-depth check are accurately described in the claim. The vulnerability's actual triggerability, however, depends entirely on the behavior of the operator's external LDAP server — specifically, whether that third-party directory service is configured to permit unauthenticated/anonymous binds for the target DN. This is standard, hardened LDAP server behavior to disable in production (most modern LDAP servers, including OpenLDAP with default ACLs and Active Directory, reject or restrict unauthenticated binds), and RFC 4513 itself explicitly recommends that clients and servers disable this behavior. The vulnerability is therefore a real code-level gap (missing defense-in-depth), but exploitability is conditioned on external server configuration rather than a guaranteed bypass purely from Chainlink code.

## Impact Explanation
If exploitable (i.e., the operator's LDAP server permits unauthenticated bind), an unprivileged network client could obtain a valid, persisted node session as any user whose email is known, including admins — a legitimate node API authentication/role bypass impact in scope for the bounty program.

## Likelihood Explanation
The attack requires no privileges beyond knowledge of a valid user email and network access to the node's `/sessions` endpoint, satisfying the "unprivileged actor" requirement. However, real-world likelihood is constrained by upstream LDAP server configuration: most production-grade directory servers reject unauthenticated binds by default or via standard hardening, so successful exploitation is not guaranteed purely by the Chainlink code but depends on this external factor. The missing explicit empty-password check in Chainlink's code is nonetheless a legitimate defense-in-depth gap, inconsistent with the stricter validation performed in the sibling `localauth` module.

## Recommendation
In `ldapAuthenticator.CreateSession`, explicitly reject session requests where `sr.Password == ""` before calling `conn.Bind`, removing reliance on upstream LDAP server configuration to prevent unauthenticated bind semantics.

## Proof of Concept
1. Deploy a Chainlink node with `AuthenticationProviderName = ldap`, pointed at an LDAP server configured (intentionally or by default) to allow unauthenticated bind for valid DNs.
2. POST to `/sessions`: `{"email": "admin@company.com", "password": ""}`.
3. `conn.Bind(searchBaseDN, "")` succeeds due to unauthenticated bind semantics on the LDAP server.
4. `FindUser` resolves the admin role, a row is inserted into `ldap_sessions`, and a valid session cookie is returned — granting session access as the admin without a correct password.

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L413-452)
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
```

**File:** core/sessions/localauth/orm.go (L159-162)
```go
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```

**File:** core/web/sessions_controller.go (L27-60)
```go
// Create creates a session ID for the given user credentials, and returns it
// in a cookie.
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
