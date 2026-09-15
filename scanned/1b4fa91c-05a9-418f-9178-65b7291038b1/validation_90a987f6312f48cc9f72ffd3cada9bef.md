### Title
Disabled LDAP users retain full API access via previously issued API tokens - (File: `core/sessions/ldapauth/ldap.go`)

### Summary
Chainlink's LDAP authentication provider enforces the upstream "is active" check when a user authenticates via login (`FindUser`), but the equivalent check is missing from the API-token authentication path (`FindUserByAPIToken`). A user deactivated on the upstream LDAP server (or removed from all authorized groups) can continue to use an already-issued API token to make authenticated requests, exactly mirroring the reported nginx-ui pattern of "disable user" controls not being enforced for bearer/token-based auth.

### Finding Description
`FindUser`, used during interactive session login, explicitly calls `validateUsersActive` and rejects the request with `"user not active"` if the upstream LDAP `ActiveAttribute` indicates the account is deactivated: [1](#0-0) 

In contrast, `FindUserByAPIToken`, used by the HTTP API token middleware, only checks token existence and expiry against the local `ldap_user_api_tokens` cache table — it never re-validates the user's active status against LDAP or any cached active flag: [2](#0-1) 

This function is invoked directly from the web request auth middleware `AuthenticateByToken`, which loads the user purely from `FindUserByAPIToken` and, if a valid (unexpired) token row is found, sets the authenticated session user without any additional active/enabled check: [3](#0-2) 

The only mechanism that can revoke access for a deactivated user is the periodic `LDAPServerStateSyncer.Work` reaper, which re-queries LDAP group membership/active status and purges stale `ldap_user_api_tokens` rows for users no longer present in `upstreamUserStateMap`: [4](#0-3) 

However this reaper only runs on a timer if `UpstreamSyncInterval` is configured to a non-zero value; if it is left at its instant/zero default, `Work` is invoked exactly once at node startup and never again: [5](#0-4) 

So depending on configuration, a deactivated user's API token can remain valid indefinitely (or until the configured `UserAPITokenDuration` expiry) with no re-check of active status — the same class of bug as the nginx-ui advisory: the "disable" control is enforced at login but not for already-issued tokens.

### Impact Explanation
An LDAP-backed Chainlink node administrator who disables/deactivates a user account (e.g. because credentials were compromised, or the employee left) has no guarantee that this actually revokes that user's access. If the user had previously created an API token, it continues to authenticate as that user's role (Admin/Edit/Run/View) via `FindUserByAPIToken`, allowing continued authenticated access to node management APIs — including sensitive operations gated by role (job/bridge management, key management endpoints, etc., depending on role) — until the reaper cycle (if configured) purges it or the token expires.

### Likelihood Explanation
This only affects deployments using the LDAP authentication provider (`LDAPAuth`) with `UserApiTokenEnabled` and an already-issued API token for the now-deactivated user. It requires no special network position — it's a straightforward unprivileged-actor bug: possession of a previously valid, unexpired token is sufficient. Likelihood of exploitation is directly tied to operational reliance on "disable user" for access revocation, which is the exact scenario described in the source advisory.

### Recommendation
Add an active-status check to `FindUserByAPIToken` in `core/sessions/ldapauth/ldap.go`, mirroring the check already performed in `FindUser` (via `validateUsersActive`), so that token-based authentication is rejected for deactivated/removed upstream users, not just session-based login. Additionally, consider running the `LDAPServerStateSyncer.Work` reaper on a mandatory minimum interval (rather than allowing it to run only once at startup when `UpstreamSyncInterval` is unset), so token purge/re-validation happens reliably.

### Proof of Concept
1. Configure Chainlink with `LDAPAuth` and `UserApiTokenEnabled = true`, and leave `UpstreamSyncInterval` at its default/instant value (or wait between reaper runs if configured with a long interval).
2. As a normal LDAP user with a valid role, create an API token via the standard flow (`CreateAndSetAuthToken`), storing an entry in `ldap_user_api_tokens`.
3. Have an administrator deactivate that user upstream in LDAP (unset the configured `ActiveAttribute`) or remove them from all role groups.
4. Continue issuing authenticated API requests with the previously obtained `APIKey`/`APISecret` headers against endpoints protected by `webauth.AuthenticateByToken`.
5. Observe requests continue to succeed with the user's previously assigned role until the token's `UserAPITokenDuration` expires or an upstream sync reaper cycle purges the row — demonstrating the disabled account retains full API access.

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

**File:** core/web/auth/auth.go (L75-112)
```go
// AuthenticateByToken authenticates a User by their API token.
//
// Implements authMethod
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

**File:** core/sessions/ldapauth/sync.go (L56-67)
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
