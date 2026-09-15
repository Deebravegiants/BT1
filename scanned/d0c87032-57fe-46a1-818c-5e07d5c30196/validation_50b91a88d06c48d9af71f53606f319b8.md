### Title
LDAP CreateSession Authentication Bypass via Empty Password (Unauthenticated Bind) - (File: `core/sessions/ldapauth/ldap.go`)

### Summary
The `ldapAuthenticator.CreateSession` function forwards user-supplied credentials directly to the configured upstream LDAP server via `conn.Bind(searchBaseDN, sr.Password)` without ever validating that `sr.Password` is non-empty. [1](#0-0) 

### Finding Description
`SessionsController.Create` binds the raw, unvalidated JSON request body into a `sessions.SessionRequest{Email, Password}` and passes it straight to `AuthenticationProvider().CreateSession(ctx, sr)` with no server-side check that the password field is non-empty. [2](#0-1) 

When the configured `AuthenticationMethod` is `ldap`, this request reaches `ldapAuthenticator.CreateSession`, which constructs the user's bind DN from the attacker-controlled `email` field and calls `conn.Bind(searchBaseDN, sr.Password)` with the attacker-controlled password, with no guard for an empty password value. [3](#0-2) 

This mirrors the root cause of CVE-2022-37397 (unauthenticated/anonymous LDAP bind bypass): per RFC 4513 §5.1.2, an LDAP `Bind` request with a non-empty DN but a zero-length password is defined as an "unauthenticated bind," which many LDAP servers — including Microsoft Active Directory when anonymous/unauthenticated binding is enabled — will report as a *successful* bind rather than an authentication failure, even though no real credential check occurred. Because the chainlink code does not special-case or reject an empty `sr.Password` before calling `Bind`, an attacker who supplies any valid/enumerable email with an empty password field can obtain a successful bind result and proceed straight into `FindUser`, which then issues a real, DB-persisted `ldap_sessions` row and a valid session ID. [4](#0-3) 

The same unguarded pattern exists in `TestPassword`, used by the `NewAPIToken` and GraphQL `CreateAPIToken` flows to re-verify a logged-in user's password before minting a new long-lived API token — it also calls `conn.Bind(searchBaseDN, password)` without checking for an empty password before falling back to local-password verification. [5](#0-4) 

### Impact Explanation
If the operator's Active Directory/LDAP server has anonymous or unauthenticated bind enabled (a common AD default/misconfiguration explicitly called out in the referenced CVE), an unprivileged remote client can authenticate as any known/enumerable LDAP-mapped user (including Admin-group members) by submitting that user's email with an empty password to `POST /sessions`. This is a full authentication bypass leading to session creation with the target user's actual role (Admin/Edit/Run/View), enabling unauthorized job runs, config changes, or fund-moving actions depending on the impersonated user's role.

### Likelihood Explanation
Exploitability depends entirely on the upstream AD/LDAP server's bind policy (whether unauthenticated binds are permitted), which is exactly the precondition described in CVE-2022-37397. Chainlink's LDAP module performs zero application-level mitigation against this well-known LDAP behavior, so any node operator using `AuthenticationMethod = 'ldap'` against a permissively configured AD server is immediately exposed to unauthenticated login as any valid directory user.

### Recommendation
Reject any `SessionRequest`/`TestPassword` call where the password is empty before ever calling `conn.Bind`, e.g. add an explicit `if sr.Password == "" { return "", errors.New(...) }` check at the top of `CreateSession` and `TestPassword` in `core/sessions/ldapauth/ldap.go`, consistent with RFC 4513's guidance to disable unauthenticated bind mechanisms at the application layer.

### Proof of Concept
1. Configure a chainlink node with `WebServer.AuthenticationMethod = 'ldap'` pointed at an Active Directory server that allows unauthenticated binds (default in many AD deployments unless explicitly hardened).
2. As an unprivileged remote client, send:
```
POST /sessions
Content-Type: application/json

{"email":"known-admin@example.com","password":""}
```
3. `SessionsController.Create` forwards this to `ldapAuthenticator.CreateSession`, which calls `conn.Bind("uid=known-admin@example.com,ou=users,dc=...", "")`. [1](#0-0) 
4. Against a vulnerable AD server, `Bind` returns no error (unauthenticated bind succeeds), `FindUser` resolves the real role, and a valid `ldap_sessions` row/cookie is issued for `known-admin@example.com` — full authentication bypass without knowing the real password.

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
