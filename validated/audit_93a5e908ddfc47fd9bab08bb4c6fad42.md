Audit Report

## Title
LDAP session authentication does not reject empty passwords, permitting RFC 4513 "unauthenticated bind" login bypass - (File: core/sessions/ldapauth/ldap.go)

## Summary
`ldapAuthenticator.CreateSession` and `ldapAuthenticator.TestPassword` pass the client-supplied `sr.Password`/`password` directly into `conn.Bind(searchBaseDN, ...)` with no check that the value is non-empty. If the configured upstream LDAP/AD server allows RFC 4513 "unauthenticated binds" (non-empty DN + empty password succeeds), an unauthenticated HTTP client can log in as any known user by supplying an empty password, since chainlink itself performs no defense-in-depth check to block this well-known LDAP bind trick.

## Finding Description
The unauthenticated `POST /sessions` endpoint binds the request body directly into `SessionRequest{Email, Password}` with no validation [1](#0-0)  and `SessionsController.Create` forwards it straight to `AuthenticationProvider().CreateSession` [2](#0-1) . Inside `CreateSession`, the DN is built from the (attacker-controlled) email and bound with the raw password with no emptiness check: [3](#0-2) 
If `conn.Bind` succeeds, the code proceeds to `FindUser`, and on success creates a live, server-trusted `ldap_sessions` row for that identity and returns a valid session ID [4](#0-3) . The identical unguarded pattern exists in `TestPassword`, which is used to validate credentials for local password changes [5](#0-4) . Neither `NewLDAPAuthenticator`'s startup checks nor `WebServer.ValidateConfig` contain any config knob or enforced default (e.g., a `deny_null_bind`-style guard) that rejects this bind pattern client-side; the code relies entirely on the upstream directory server's own configuration to reject empty-password binds, which many LDAP/AD deployments do not do by default.

## Impact Explanation
If the upstream directory server permits unauthenticated binds, an unauthenticated network client who knows or guesses a valid user email can authenticate as that user with no password and obtain a full session cookie plus the user's RBAC role (Admin/Edit/Run/Read), reachable via the public `/sessions` endpoint — this maps to the in-scope "node API authentication/role bypass" impact category.

## Likelihood Explanation
The trigger path itself (an unprivileged POST with `password: ""`) requires no credentials and is fully attacker-controlled, but the actual bypass is conditional on the deployed LDAP/AD server's own bind policy, which chainlink has no visibility into or control over via any of its own config. chainlink is missing a defense-in-depth, application-side check for this well-known LDAP-specific attack class (analogous to the referenced CVE-2025-13357 in Vault's Terraform provider), and enforcing "deny null bind" locally would close the gap regardless of upstream server defaults.

## Recommendation
Explicitly reject empty/whitespace-only passwords in `CreateSession` and `TestPassword` before calling `conn.Bind` (e.g., `if sr.Password == "" { return "", errors.New("password required") }` and equivalent in `TestPassword`), so the node enforces "deny null bind" behavior independent of the upstream LDAP server's own defaults.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` against an LDAP/AD server that permits unauthenticated binds (a common default unless explicitly hardened).
2. Send `POST /sessions` with body `{"email": "<known-user>@example.com", "password": ""}`.
3. `conn.Bind(searchBaseDN, "")` in `CreateSession` (core/sessions/ldapauth/ldap.go:408) succeeds as an RFC 4513 unauthenticated bind; `FindUser` resolves the user's role, and a valid `ldap_sessions` row/session cookie is returned without the attacker ever supplying the real password. A Go unit test mocking `ldapClient.CreateEphemeralConnection` to return a fake connection whose `Bind` succeeds for empty password would confirm the code path returns a valid session ID.

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

**File:** core/web/sessions_controller.go (L56-60)
```go
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
