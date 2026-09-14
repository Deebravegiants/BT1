### Title
LDAP-authenticated API token access does not re-validate upstream account status, allowing deactivated/removed users to retain API access - ([File: core/sessions/ldapauth/ldap.go](core/sessions/ldapauth/ldap.go))

### Summary
This mirrors the Keystone bug class (CVE-2013-0282): a secondary/alternate authentication path (EC2-style credentials in Keystone; API-token auth here) skips the "is this identity still enabled/active" check that the primary authentication path enforces.

### Finding Description
In the LDAP authentication provider, the primary login path (`FindUser`) explicitly re-validates the user's active status against the upstream LDAP directory before returning a valid identity: [1](#0-0) 

However, the API-token authentication path, `FindUserByAPIToken`, only checks the locally-cached `ldap_user_api_tokens` table for token validity/expiration — it never re-queries or re-checks whether the associated user is still active/enabled upstream: [2](#0-1) 

This locally-cached role/email data is only refreshed by a periodic background sync (`LDAPServerStateSyncer.Work`), which purges tokens for users no longer present in upstream groups or found to be inactive via `validateUsersActive`: [3](#0-2) 

Between sync intervals (governed by `UpstreamSyncInterval`/`UpstreamSyncRateLimit`, which can be configured with long periods or, per code comments, are otherwise triggered only "on the sync interval" and at startup), a user whose upstream account is deactivated, removed from all role groups, or fails the `ActiveAttribute` check will continue to authenticate successfully via `AuthenticateByToken`, which calls `FindUserByAPIToken` directly with no active-status check: [4](#0-3) 

This is structurally identical to the Keystone flaw: one authentication mechanism (session/password login) enforces the enabled/active check, while another supported mechanism (token-based) does not, allowing a caller whose access should have been revoked to bypass the restriction.

### Impact Explanation
An API token issued to a user is honored for its full validity window (`UserAPITokenDuration`) even after that user is deactivated or removed from LDAP entirely, until the next background sync purges the token row. During that window the disabled user retains full API access at whatever role they last held (including admin), enabling unauthorized job runs, configuration changes, or secret/key management actions depending on role — a concrete access-restriction bypass tied to identity state that should have blocked them.

### Likelihood Explanation
This requires only normal, unprivileged conditions: a previously legitimate user already possesses a valid API token (or generates one before being deactivated), and an administrator disables/removes them upstream expecting immediate effect. No attacker sophistication or race condition timing is required beyond the (potentially large, operator-configured) sync interval — the vulnerable window is present in every deployment using LDAP token auth unless `UpstreamSyncInterval`/`UpstreamSyncRateLimit` happen to be configured very aggressively.

### Recommendation
Have `FindUserByAPIToken` in `core/sessions/ldapauth/ldap.go` perform (or trigger) the same `validateUsersActive` check used by `FindUser` before returning a user, or reduce trust in the cached table by forcing a synchronous re-check against the upstream directory on token use, at least at some bounded rate independent of the configured sync interval.

### Proof of Concept
1. Configure LDAP authentication with `UpstreamSyncInterval` set to a non-trivial value (e.g., hours).
2. As user `alice` (edit/admin role), log in and call the token-creation endpoint to obtain an API key via `SetAuthToken`/`CreateAndSetAuthToken`.
3. An administrator deactivates `alice` in the upstream LDAP server (sets `ActiveAttribute` to a disallowed value, or removes her from all role groups).
4. Before the next sync cycle runs, `alice` continues to call the Chainlink API using her API key/secret headers; `AuthenticateByToken` → `FindUserByAPIToken` returns a valid, still-privileged user object with no active-status re-check, and the request succeeds as if she were still an authorized user.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L131-142)
```go
	// First query for user "is active" property if defined
	usersActive, err := l.validateUsersActive([]string{email})
	if err != nil {
		if errors.Is(err, ErrUserNotInUpstream) {
			return sessions.User{}, ErrUserNotInUpstream
		}
		l.lggr.Errorf("error in validateUsers call: %v", err)
		return sessions.User{}, errors.New("error running query to validate user active")
	}
	if !usersActive[0] {
		return sessions.User{}, errors.New("user not active")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L204-236)
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
	if !foundUserToken.Valid { // API Token expired, purge
		if _, execErr := l.ds.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE token_key = $1", apiToken); execErr != nil {
			l.lggr.Errorf("error purging stale ldap API token session: %v", execErr)
		}
		return sessions.User{}, sessions.ErrUserSessionExpired
	}

	return sessions.User{
		Email: foundUserToken.UserEmail,
		Role:  foundUserToken.UserRole,
	}, nil
}
```

**File:** core/sessions/ldapauth/sync.go (L174-243)
```go
	// For each unique user in list of active sessions, check for 'Is Active' property if defined in the config. Some LDAP providers
	// list group members that are no longer marked as active
	usersActiveFlags, err := l.validateUsersActive(dedupedEmails, conn)
	if err != nil {
		l.lggr.Error("Error validating supplied user list: ", err)
	}
	// Remove users in the upstreamUserStateMap source of truth who are part of groups but marked as deactivated/no-active
	for i, active := range usersActiveFlags {
		if !active {
			delete(upstreamUserStateMap, dedupedEmails[i])
		}
	}

	// upstreamUserStateMap is now the most up to date source of truth
	// Now sync database sessions and roles with new data
	err = sqlutil.TransactDataSource(ctx, l.ds, nil, func(tx sqlutil.DataSource) error {
		// First, purge users present in the local ldap_sessions table but not in the upstream server
		type LDAPSession struct {
			UserEmail string
			UserRole  sessions.UserRole
		}
		var existingSessions []LDAPSession
		if err = tx.SelectContext(ctx, &existingSessions, "SELECT user_email, user_role FROM ldap_sessions WHERE localauth_user = false"); err != nil {
			return fmt.Errorf("unable to query ldap_sessions table: %w", err)
		}
		var existingAPITokens []LDAPSession
		if err = tx.SelectContext(ctx, &existingAPITokens, "SELECT user_email, user_role FROM ldap_user_api_tokens WHERE localauth_user = false"); err != nil {
			return fmt.Errorf("unable to query ldap_user_api_tokens table: %w", err)
		}

		// Create existing sessions and API tokens lookup map for later
		existingSessionsMap := make(map[string]LDAPSession)
		for _, sess := range existingSessions {
			existingSessionsMap[sess.UserEmail] = sess
		}
		existingAPITokensMap := make(map[string]LDAPSession)
		for _, sess := range existingAPITokens {
			existingAPITokensMap[sess.UserEmail] = sess
		}

		// Populate list of session emails present in the local session table but not in the upstream state
		emailsToPurge := []any{}
		for _, ldapSession := range existingSessions {
			if _, ok := upstreamUserStateMap[ldapSession.UserEmail]; !ok {
				emailsToPurge = append(emailsToPurge, ldapSession.UserEmail)
			}
		}
		// Likewise for API Tokens table
		apiTokenEmailsToPurge := []any{}
		for _, ldapSession := range existingAPITokens {
			if _, ok := upstreamUserStateMap[ldapSession.UserEmail]; !ok {
				apiTokenEmailsToPurge = append(apiTokenEmailsToPurge, ldapSession.UserEmail)
			}
		}

		// Remove any active sessions this user may have
		if len(emailsToPurge) > 0 {
			_, err = tx.ExecContext(ctx, "DELETE FROM ldap_sessions WHERE user_email = ANY($1)", pq.Array(emailsToPurge))
			if err != nil {
				return err
			}
		}

		// Remove any active API tokens this user may have
		if len(apiTokenEmailsToPurge) > 0 {
			_, err = tx.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE user_email = ANY($1)", pq.Array(apiTokenEmailsToPurge))
			if err != nil {
				return err
			}
		}
```

**File:** core/web/auth/auth.go (L78-112)
```go
func AuthenticateByToken(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	token := &auth.Token{
		AccessKey: c.GetHeader(APIKey),
		Secret:    c.GetHeader(APISecret),
	}
	if token.AccessKey == "" {
		return auth.ErrorAuthFailed
	}

	if token.Secret == "" {
		return auth.ErrorAuthFailed
	}

	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || errors.Is(err, clsessions.ErrUserSessionExpired) {
			return auth.ErrorAuthFailed
		}
		return err
	}

	ok, err := clsessions.AuthenticateUserByToken(token, &user)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```
