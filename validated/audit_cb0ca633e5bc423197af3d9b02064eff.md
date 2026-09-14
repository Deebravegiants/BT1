### Title
LDAP role/session cache can remain stale after upstream privilege downgrade, granting continued elevated access - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The LDAP authenticator caches a user's role in `ldap_sessions` / `ldap_user_api_tokens` at login/token-creation time and reuses that cached role for every subsequent authorization decision, only refreshing it when `LDAPServerStateSyncer.Work` runs. This mirrors the reported bug class: an authorization decision (role/threshold) is computed from a stale "snapshot" while the actual privilege state (LDAP group membership) has already changed, creating a window where a downgraded/removed user still exercises the old, higher privilege.

### Finding Description
`AuthorizedUserWithSession` and `FindUserByAPIToken` read the user's role straight out of the `ldap_sessions`/`ldap_user_api_tokens` tables without re-querying LDAP; the comment explicitly says "user role and email are cached so no further upstream LDAP query is performed." [1](#0-0) [2](#0-1) 

The only mechanism that refreshes this cached role to match the current upstream LDAP group membership is `LDAPServerStateSyncer.Work`, which re-derives `upstreamUserStateMap` from the LDAP groups and does a bulk `UPDATE ... SET user_role = CASE WHEN ...` over existing sessions/tokens. [3](#0-2) 

This `Work` function is invoked either on a background timer if `UpstreamSyncInterval` is configured non-zero, or — if that interval is left at its default of `0s` — only once at node startup (`Start` calls `l.Work(ctx)` a single time and never again on an interval). [4](#0-3) [5](#0-4) 

Given the default config (`UpstreamSyncInterval = '0s'`), there is no periodic re-sync at all after boot: a user's cached role in `ldap_sessions` is set once at `CreateSession` time from a `FindUser` LDAP lookup at login, and is never re-validated for the lifetime of that session/token unless an operator explicitly configures a non-zero `UpstreamSyncInterval` or the user logs out and back in. [6](#0-5) 

This is directly analogous to the reported class of bug: one piece of authorization state (session role, analogous to "who can vote"/membership) is fixed at a point in time (snapshot at login), while the *actual* current privilege state (LDAP group membership, analogous to "minApproval"/threshold config) can change independently and immediately on the LDAP server — but the node's authorization decisions keep using the stale value. The two systems (LDAP group membership vs. locally cached role used for `RequiresAdminRole`/`RequiresEditRole` gating) desync, exactly as `minApprovals` and `snapshotBlock` desync in the original report.

### Impact Explanation
If an administrator revokes or downgrades a compromised or offboarded user's LDAP group membership (e.g., removes them from the Admin group after detecting key/credential leakage — the same threat model used in the original report), that user's already-established Chainlink node session or API token continues to authenticate with the old (higher) role via `AuthorizedUserWithSession`/`FindUserByAPIToken`, since no re-sync occurs by default. This allows the demoted/compromised principal to continue performing privileged node operations (`RequiresAdminRole`-gated endpoints) using the stale cached role. [7](#0-6) 

### Likelihood Explanation
This requires the operator to be running the LDAP authenticator (`ldapauth`) and to have left `UpstreamSyncInterval` at its documented default of `'0s'`, which is the default and thus a common/likely deployment configuration. It further requires an admin to revoke a user's LDAP role expecting immediate effect (a very natural remediation action, e.g., in exactly the credential-leak scenario described in the source report) without also forcing session logout — which is plausible since the tool provides no explicit warning that revocation isn't immediate without a configured sync interval or manual logout.

### Recommendation
Re-validate the cached LDAP role against the upstream directory (or force session/token invalidation) at the moment a role change is detected, rather than relying solely on a best-effort periodic timer that defaults to disabled. At minimum, document prominently that `UpstreamSyncInterval = '0s'` means revoked privileges do not propagate until the next node restart or explicit re-login, and consider defaulting to a non-zero interval, or performing a live upstream check on privileged (`RequiresAdminRole`) actions instead of trusting the cached `user_role` column.

### Proof of Concept
1. Deploy a Chainlink node with `Auth.Type = 'ldap'` and leave `LDAP.UpstreamSyncInterval` at its default (`'0s'`). [5](#0-4) 
2. User `alice` is a member of the LDAP Admin group; she logs in, and `CreateSession` inserts `ldap_sessions` with `user_role='admin'` derived from `FindUser`. [6](#0-5) 
3. Operator detects Alice's credentials/private keys are compromised and removes her from the LDAP Admin group on the LDAP server, expecting immediate loss of admin access.
4. Because `UpstreamSyncInterval` is `'0s'`, `LDAPServerStateSyncer.Work` only ran once at startup and is never re-triggered on a timer. [4](#0-3) 
5. Alice's existing session cookie continues to resolve via `AuthorizedUserWithSession`, which reads `user_role='admin'` straight from `ldap_sessions` without contacting LDAP again, so `RequiresAdminRole`-protected endpoints continue to authorize her. [8](#0-7) [7](#0-6) 

Note: I was unable to fully verify whether any other code path (e.g., a per-request LDAP re-check or a forced-logout-on-role-change mechanism) exists elsewhere in the codebase that might mitigate this beyond what `sync.go`/`ldap.go` show; the index may not include every file, and a full Devin session with complete repository access would be needed to rule out an additional invalidation hook I did not locate.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L204-224)
```go
// FindUserByAPIToken retrieves a possible stored user and role from the ldap_user_api_tokens table store
func (l *ldapAuthenticator) FindUserByAPIToken(ctx context.Context, apiToken string) (sessions.User, error) {
	if !l.config.UserApiTokenEnabled() {
		return sessions.User{}, errors.New("API token is not enabled ")
	}

	// Query the ldap user API token table for given token, user role and email are cached so
	// no further upstream LDAP query is performed, sessions and tokens are synced against the upstream server
	// via the UpstreamSyncInterval config and reaper.go sync implementation
	var foundUserToken struct {
		UserEmail string
		UserRole  sessions.UserRole
		Valid     bool
	}
	err := l.ds.GetContext(ctx, &foundUserToken,
		"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_user_api_tokens WHERE token_key = $1",
		apiToken, l.config.UserAPITokenDuration().Duration(),
	)
	if err != nil {
		return sessions.User{}, err
	}
```

**File:** core/sessions/ldapauth/ldap.go (L342-373)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired, and update session's LastUsed field. The state of the upstream LDAP server
// is polled and synced at the defined interval via a SleeperTask
func (l *ldapAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (sessions.User, error) {
	if len(sessionID) == 0 {
		return sessions.User{}, errors.New("session ID cannot be empty")
	}
	// Query the ldap_sessions table for given session ID, user role and email are cached so
	// no further upstream LDAP query is performed
	var foundSession struct {
		UserEmail string
		UserRole  sessions.UserRole
		Valid     bool
	}
	if err := l.ds.GetContext(ctx, &foundSession,
		"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_sessions WHERE id = $1",
		sessionID, l.config.SessionTimeout().Duration(),
	); err != nil {
		return sessions.User{}, sessions.ErrUserSessionExpired
	}
	if !foundSession.Valid {
		// Sessions expired, purge
		if _, execErr := l.ds.ExecContext(ctx, "DELETE FROM ldap_sessions WHERE id = $1", sessionID); execErr != nil {
			l.lggr.Errorf("error purging stale ldap session: %v", execErr)
		}
		return sessions.User{}, sessions.ErrUserSessionExpired
	}
	return sessions.User{
		Email: foundSession.UserEmail,
		Role:  foundSession.UserRole,
	}, nil
}
```

**File:** core/sessions/ldapauth/ldap.go (L392-457)
```go
// CreateSession will forward the session request credentials to the
// LDAP server, querying for a user + role response if username and
// password match. The API call is blocking with timeout, so a sufficient timeout
// should allow the user to respond to potential MFA push notifications
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
}
```

**File:** core/sessions/ldapauth/sync.go (L56-68)
```go
func (l *LDAPServerStateSyncer) Start(ctx context.Context) error {
	// If enabled, start a background task that calls the Sync/Work function on an
	// interval without needing an auth event to trigger it
	// Use IsInstant to check 0 value to omit functionality.
	if !l.config.UpstreamSyncInterval().IsInstant() {
		l.lggr.Info("LDAP Config UpstreamSyncInterval is non-zero, sync functionality will be called on a timer, respecting the UpstreamSyncRateLimit value")
		go l.run()
	} else {
		// Ensure upstream server state is synced on startup manually if interval check not set
		l.Work(ctx)
	}
	return nil
}
```

**File:** core/sessions/ldapauth/sync.go (L245-275)
```go
		// For each user session row, update role to match state of user map from upstream source
		var queryWhenClause strings.Builder
		emailValues := []any{}
		// Prepare CASE WHEN query statement with parameterized argument $n placeholders and matching role based on index
		for email, user := range upstreamUserStateMap {
			// Only build on SET CASE statement per local session and API token role, not for each upstream user value
			_, sessionOk := existingSessionsMap[email]
			_, tokenOk := existingAPITokensMap[email]
			if !sessionOk && !tokenOk {
				continue
			}
			emailValues = append(emailValues, email)
			fmt.Fprintf(&queryWhenClause, "WHEN user_email = $%d THEN '%s' ", len(emailValues), user.Role)
		}

		// If there are remaining user entries to update
		if len(emailValues) != 0 {
			// Set new role state for all rows in single Exec
			query := fmt.Sprintf("UPDATE ldap_sessions SET user_role = CASE %s ELSE user_role END", &queryWhenClause)
			_, err = tx.ExecContext(ctx, query, emailValues...)
			if err != nil {
				return err
			}

			// Update role of API tokens as well
			query = fmt.Sprintf("UPDATE ldap_user_api_tokens SET user_role = CASE %s ELSE user_role END", &queryWhenClause)
			_, err = tx.ExecContext(ctx, query, emailValues...)
			if err != nil {
				return err
			}
		}
```

**File:** core/config/docs/core.toml (L777-781)
```text
# **ADVANCED**
# DevWebServer skips secure configuration for webserver AllowedHosts, SSL, etc.
DevWebServer = false # Default
# OCRDevelopmentMode run OCR in development mode.
OCRDevelopmentMode = false # Default
```

**File:** core/web/auth/auth.go (L236-253)
```go
// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```
