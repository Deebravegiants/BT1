Confirmed: `core/sessions/ldapauth/ldap.go` never rejects an empty `sr.Password` before calling `conn.Bind(searchBaseDN, sr.Password)`. LDAP servers (per RFC 4513) that permit "unauthenticated bind" will return a successful bind result when a valid DN is supplied with a zero-length password, regardless of what the actual password is. No confirmation of an explicit unauthenticated-bind rejection exists anywhere in the reachable code paths I inspected.

### Title
LDAP Session Authentication Accepts Empty Password via Unauthenticated Bind, Allowing Login as Any Known User - (File: core/sessions/ldapauth/ldap.go)

### Summary
`ldapAuthenticator.CreateSession` performs an LDAP simple bind using the caller-supplied `sr.Password` without first validating that the password is non-empty. Per RFC 4513 §5.1.2, LDAP simple binds with a non-empty DN and a zero-length password constitute an "unauthenticated bind," which most LDAP servers (unless explicitly hardened) treat as a *successful* bind. An unprivileged client who only knows (or guesses) a valid user's email/DN can send a session-creation request with `password: ""` and have the operator's node authenticate them as that user, bypassing password verification entirely — mirroring the same "known/guessed username → account takeover, no valid credential required" root cause described in the firstuseauthenticator advisory.

### Finding Description
`CreateSession` in [1](#0-0)  builds a bind DN directly from the caller-supplied `sr.Email` and passes `sr.Password` unchecked into `conn.Bind(searchBaseDN, sr.Password)`. There is no guard rejecting an empty password before the bind call, unlike the local-auth implementation which uses `utils.CheckPasswordHash` to reject any password value against a stored hash ( [2](#0-1) ).

If the bind succeeds (`err == nil`), the code proceeds to call `l.FindUser(ctx, escapedEmail)` to fetch the role and then creates a full, persisted session in `ldap_sessions` for that user with no additional password check ( [3](#0-2) ). This is directly reachable from the unauthenticated `/sessions` HTTP endpoint ( [4](#0-3) ), which only requires a JSON body containing `email`/`password` — no prior authentication is needed to hit this code path.

This is the same bug class as CVE-2021-41194: an authentication routine that, for certain crafted/degenerate inputs (empty password / anonymous bind), grants a session for an arbitrary known user without actually validating a secret the user should possess.

### Impact Explanation
If the configured upstream LDAP server allows unauthenticated ("anonymous") binds — a common default in many LDAP deployments unless explicitly disabled — any unprivileged network client can obtain a valid, persisted Chainlink node session cookie for any user whose email is known or guessed, including admin accounts, by submitting a login request with an empty password. This grants full session-level access to the node's HTTP API (job management, keys, bridges, etc., depending on the impersonated user's role), satisfying the "concrete authentication or role bypass" acceptance criterion.

### Likelihood Explanation
Likelihood depends on the operator's upstream LDAP server configuration (whether unauthenticated binds are permitted for the searched DN). This is a realistic, commonly-encountered default in many directory server setups, and the Chainlink code itself provides no defense-in-depth check against it, unlike the sibling `localauth` and `oidcauth` implementations which always verify a password hash before issuing a session. The attack requires only knowledge of a valid email address, which is often guessable or already known (e.g., admin@company.com), making this a low-effort, low-privilege attack when LDAP is deployed permissively.

### Recommendation
In `ldapAuthenticator.CreateSession`, explicitly reject session requests where `sr.Password == ""` before calling `conn.Bind`, and/or configure the LDAP client to disable unauthenticated bind semantics (many LDAP libraries provide a "simple bind" mode that treats empty passwords as invalid rather than delegating to server behavior). This mirrors the fix pattern applied for CVE-2021-41194, which added explicit checks to prevent authentication bypass on degenerate credential input.

### Proof of Concept
1. Deploy/target a Chainlink node configured with `AuthenticationProviderName = ldap` where the upstream LDAP server permits unauthenticated bind for valid DNs (default behavior for many LDAP servers unless hardened).
2. As an unprivileged network client, POST to `/sessions`:
```
POST /sessions
Content-Type: application/json

{"email": "admin@company.com", "password": ""}
```
3. `ldapAuthenticator.CreateSession` calls `conn.Bind(searchBaseDN, "")`, which the LDAP server treats as an unauthenticated bind and returns success.
4. `FindUser` resolves the admin's role, a new row is inserted into `ldap_sessions`, and a valid session cookie is returned to the attacker — granting authenticated access as the admin user without ever supplying a correct password.

### Citations

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
