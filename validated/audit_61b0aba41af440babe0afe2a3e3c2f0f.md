### Title
LDAP session authentication does not reject empty passwords, permitting RFC 4513 "unauthenticated bind" login bypass - (File: core/sessions/ldapauth/ldap.go)

### Summary
`ldapAuthenticator.CreateSession` and `ldapAuthenticator.TestPassword` forward the client-supplied `sr.Password` directly into `conn.Bind(searchBaseDN, sr.Password)` with no check that the password is non-empty [1](#0-0) . This is the same bug class as the reported Vault Terraform Provider issue: failing to explicitly deny "null"/unauthenticated binds by default, instead relying on whatever the underlying directory server's default behavior is.

### Finding Description
`SessionRequest.Password` is bound straight from the unauthenticated `/sessions` HTTP POST body with no validation [2](#0-1) [3](#0-2) . `SessionsController.Create` passes this straight to `AuthenticationProvider().CreateSession` [4](#0-3) .

In `CreateSession`, the code does:
```go
searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
``` [1](#0-0) 

Per RFC 4513 §5.1.2, an LDAP `Bind` request with a non-empty DN and an empty password is defined as an "unauthenticated bind," and many LDAP server implementations (unless explicitly hardened, analogous to `deny_null_bind` in the reported Vault advisory) will return success for this bind without validating any credential. If the target directory allows this default behavior, submitting an empty `"password": ""` for any known/guessable `email` will cause `conn.Bind` to return `nil` error, bypassing the intended credential check entirely. Execution then proceeds to `FindUser`, which — if the user exists and is a member of a role group (or falls back to the local admin `users` table) — returns a valid `sessions.User` and role, and the code creates a live server-trusted session (`ldap_sessions` row) for that identity with no password verification actually having occurred [5](#0-4) .

The same missing check exists in `TestPassword`, used to validate credentials for e.g. changing local passwords [6](#0-5) .

Nowhere in `NewLDAPAuthenticator`'s startup validation, nor in `WebServer.ValidateConfig`, is there any config knob or enforced default equivalent to `deny_null_bind` that would reject this class of bind, and no length/emptiness check exists before calling `Bind` [7](#0-6) [8](#0-7) .

### Impact Explanation
If the configured upstream LDAP/AD server permits unauthenticated binds (a common default for many LDAP servers, and exactly the behavior the referenced CVE-2025-13357 advisory warns must be explicitly denied), an unauthenticated attacker who knows or guesses a valid user email can log in as that user without any password, obtaining a full session cookie and the user's assigned RBAC role (Admin/Edit/Run/Read). This is a full authentication bypass reachable from an unprivileged HTTP client via the public `/sessions` endpoint.

### Likelihood Explanation
Likelihood depends entirely on the operator's upstream LDAP server configuration (whether it permits unauthenticated binds), which chainlink does not control or defend against, and TLS/production mode is still separately enforced [9](#0-8) . There is no compensating check in the chainlink code path itself, so any deployment against a permissive directory is exploitable trivially and repeatedly by any network client that can reach `/sessions` with a known email.

### Recommendation
Explicitly reject empty (or whitespace-only) passwords in `CreateSession` and `TestPassword` before calling `conn.Bind`, e.g. return an error if `sr.Password == ""` / `password == ""`, so the node itself enforces "deny null bind" behavior regardless of the upstream LDAP server's own defaults.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` against an LDAP server that permits unauthenticated binds (default behavior for many servers unless hardened).
2. `POST /sessions` with body `{"email": "<known-user>@example.com", "password": ""}`.
3. `conn.Bind(searchBaseDN, "")` succeeds as an RFC 4513 unauthenticated bind, `FindUser` resolves the user's role, and a valid session cookie is issued — without the attacker ever knowing the real password.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L67-112)
```go
func NewLDAPAuthenticator(
	ds sqlutil.DataSource,
	ldapCfg config.LDAP,
	dev bool,
	lggr logger.Logger,
	auditLogger audit.AuditLogger,
) (*ldapAuthenticator, error) {
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

	ldapAuth := ldapAuthenticator{
		ds:          ds,
		ldapClient:  newLDAPClient(ldapCfg),
		config:      ldapCfg,
		lggr:        lggr.Named("LDAPAuthenticationProvider"),
		auditLogger: auditLogger,
	}

	// Single override of library defined global
	ldap.DefaultTimeout = ldapCfg.QueryTimeout()

	// Test initial connection and credentials
	lggr.Infof("Attempting initial connection to configured LDAP server with bind as API user")
	conn, err := ldapAuth.ldapClient.CreateEphemeralConnection()
	if err != nil {
		return nil, fmt.Errorf("unable to establish connection to LDAP server with provided URL and credentials: %w", err)
	}
	conn.Close()

	// Store LDAP connection config for auth/new connection per request instead of persisted connection with reconnect
	return &ldapAuth, nil
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

**File:** core/sessions/ldapauth/ldap.go (L504-518)
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
	l.lggr.Infof("Error binding user authentication request in TestPassword call LDAP Bind: %v", err)
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

**File:** core/web/sessions_controller.go (L34-39)
```go
	session := sessions.Default(c)
	var sr clsessions.SessionRequest
	if err := c.ShouldBindJSON(&sr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("error binding json %w", err))
		return
	}
```

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/config/toml/types.go (L1149-1177)
```go
func (w *WebServer) ValidateConfig() (err error) {
	switch *w.AuthenticationMethod {
	case string(sessions.LDAPAuth):
		// Assert LDAP fields when AuthMethod set to LDAP
		if *w.LDAP.BaseDN == "" {
			err = errors.Join(err, configutils.ErrInvalid{Name: "LDAP.BaseDN", Msg: "LDAP BaseDN can not be empty"})
		}
		if *w.LDAP.BaseUserAttr == "" {
			err = errors.Join(err, configutils.ErrInvalid{Name: "LDAP.BaseUserAttr", Msg: "LDAP BaseUserAttr can not be empty"})
		}
		if *w.LDAP.UsersDN == "" {
			err = errors.Join(err, configutils.ErrInvalid{Name: "LDAP.UsersDN", Msg: "LDAP UsersDN can not be empty"})
		}
		if *w.LDAP.GroupsDN == "" {
			err = errors.Join(err, configutils.ErrInvalid{Name: "LDAP.GroupsDN", Msg: "LDAP GroupsDN can not be empty"})
		}
		if *w.LDAP.AdminUserGroupCN == "" {
			err = errors.Join(err, configutils.ErrInvalid{Name: "LDAP.AdminUserGroupCN", Msg: "LDAP AdminUserGroupCN can not be empty"})
		}
		if *w.LDAP.EditUserGroupCN == "" {
			err = errors.Join(err, configutils.ErrInvalid{Name: "LDAP.RunUserGroupCN", Msg: "LDAP ReadUserGroupCN can not be empty"})
		}
		if *w.LDAP.RunUserGroupCN == "" {
			err = errors.Join(err, configutils.ErrInvalid{Name: "LDAP.RunUserGroupCN", Msg: "LDAP RunUserGroupCN can not be empty"})
		}
		if *w.LDAP.ReadUserGroupCN == "" {
			err = errors.Join(err, configutils.ErrInvalid{Name: "LDAP.ReadUserGroupCN", Msg: "LDAP ReadUserGroupCN can not be empty"})
		}
		return err
```
