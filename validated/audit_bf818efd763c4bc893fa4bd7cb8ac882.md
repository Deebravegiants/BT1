## Analysis

The Mattermost CVE-2023-2788 bug class — a deactivated privileged user retaining access because active-session/token validity is checked only against local/cached state rather than revalidated against the identity provider — has a direct analog in this codebase's OIDC authentication provider.

### Title
Deactivated OIDC user retains persistent access via cached session and API token, with no upstream revocation check - ([File: core/sessions/oidcauth/oidc.go])

### Summary
The OIDC `AuthenticationProvider` implementation caches a user's email and role locally in the `oidc_sessions` and `oidc_user_api_tokens` tables at login/token-creation time and never revalidates that state against the upstream identity provider on subsequent requests. Unlike the LDAP provider, which explicitly re-polls the upstream server on an interval to detect deactivated accounts and purge their access [1](#0-0) , the OIDC session reaper only purges sessions based on time-based expiration, never on upstream account status [2](#0-1) .

### Finding Description
`oidcAuthenticator.AuthorizedUserWithSession` validates a session purely by looking up the cached `oidc_sessions` row and checking a time-based `created_at + SessionTimeout >= now()` predicate — it never re-checks the upstream OIDC provider or the user's active status: [3](#0-2) 

Similarly, `FindUserByAPIToken` validates API tokens purely against the cached `oidc_user_api_tokens` table with a time-based expiry check, again with no upstream revalidation: [4](#0-3) 

The only background process touching these tables is the OIDC `sessionReaper`, which exclusively deletes sessions whose `created_at` predates a stale threshold derived from `SessionReaperExpiration`/`SessionTimeout` — it contains no logic to query the identity provider and detect/deactivate revoked users: [5](#0-4) 

Contrast this with the LDAP provider's `LDAPServerStateSyncer.Work`, which explicitly re-queries the upstream directory for each cached user's active-attribute and removes deactivated users from the source-of-truth map used to sync local sessions/roles: [6](#0-5)  This upstream revalidation capability exists in the LDAP path but has no equivalent implementation for OIDC.

`oidcAuthenticator.DeleteUser` is explicitly a no-op (`ErrNotSupported`), meaning there is no operator-initiated action inside the node itself to immediately revoke a compromised/deactivated OIDC user's active session or API token — the only local action is `DeleteUserSession`/`DeleteUserSession` for a specific known session ID: [7](#0-6) 

### Impact Explanation
If an admin/edit-role user is deactivated or has their access revoked at the upstream OIDC identity provider (e.g., IdP-side deprovisioning, group removal, account suspension) after they have already obtained a valid `oidc_sessions` cookie or `oidc_user_api_tokens` API token, that session/token remains fully authorized to call all node API endpoints gated by `AuthenticateBySession`/`AuthenticateByToken` for the full configured `SessionTimeout`/`UserAPITokenDuration` window [8](#0-7) . Depending on the user's cached role, this can allow continued administrative actions (job management, bridge/key management, fund-moving operations) despite the account no longer being authorized at the source of truth.

### Likelihood Explanation
This requires no special network position or malicious peer — it is purely a gap in the OIDC authentication provider's own revalidation logic, reachable by any previously-authenticated OIDC user whose upstream account is later deactivated. The bug is deterministic: as long as the session/token has not hit its local expiry, access persists regardless of upstream state.

### Recommendation
Implement an upstream revalidation mechanism for the OIDC provider analogous to `LDAPServerStateSyncer.Work`/`validateUsersActive` — periodically (or on each request, if feasible) reverify the cached OIDC session's/token's user against the upstream provider (introspection endpoint, userinfo endpoint, or claims re-verification) and purge `oidc_sessions`/`oidc_user_api_tokens` rows for users no longer active/authorized, mirroring the pattern already implemented for LDAP in `core/sessions/ldapauth/sync.go`.

### Proof of Concept
1. Configure the node with `AuthenticationMethod = "oidc"`.
2. An admin-role user completes the OIDC login flow via `handleTokenExchange`, receiving a session cookie backed by an `oidc_sessions` row, or provisions an API token via `SetAuthToken` backed by `oidc_user_api_tokens`.
3. The upstream identity provider deactivates/removes the user from the admin group.
4. Using the still-valid session cookie or API token, the attacker calls any authenticated node API endpoint before `SessionTimeout`/`UserAPITokenDuration` elapses — `AuthorizedUserWithSession`/`FindUserByAPIToken` return the cached (stale) role successfully because no upstream check occurs, granting continued authorized access.

### Citations

**File:** core/sessions/ldapauth/sync.go (L93-185)
```go
func (l *LDAPServerStateSyncer) Work(ctx context.Context) {
	// Purge expired ldap_sessions and ldap_user_api_tokens
	recordCreationStaleThreshold := l.config.SessionTimeout().Before(time.Now())
	err := l.deleteStaleSessions(ctx, recordCreationStaleThreshold)
	if err != nil {
		l.lggr.Error("unable to expire local LDAP sessions: ", err)
	}
	recordCreationStaleThreshold = l.config.UserAPITokenDuration().Before(time.Now())
	err = l.deleteStaleAPITokens(ctx, recordCreationStaleThreshold)
	if err != nil {
		l.lggr.Error("unable to expire user API tokens: ", err)
	}

	// Optional rate limiting check to limit the amount of upstream LDAP server queries performed
	if !l.config.UpstreamSyncRateLimit().IsInstant() {
		if !time.Now().After(l.nextSyncTime) {
			return
		}

		// Enough time has elapsed to sync again, store the time for when next sync is allowed and begin sync
		l.nextSyncTime = time.Now().Add(l.config.UpstreamSyncRateLimit().Duration())
	}

	l.lggr.Info("Begin Upstream LDAP provider state sync after checking time against config UpstreamSyncInterval and UpstreamSyncRateLimit")

	// For each defined role/group, query for the list of group members to gather the full list of possible users
	users := []sessions.User{}

	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		l.lggr.Error("Failed to Dial LDAP Server: ", err)
		return
	}
	// Root level root user auth with credentials provided from config
	bindStr := l.config.BaseUserAttr() + "=" + l.config.ReadOnlyUserLogin() + "," + l.config.BaseDN()
	if err = conn.Bind(bindStr, l.config.ReadOnlyUserPass()); err != nil {
		l.lggr.Error("Unable to login as initial root LDAP user: ", err)
	}
	defer conn.Close()

	// Query for list of uniqueMember IDs present in Admin group
	adminUsers, err := l.ldapGroupMembersListToUser(conn, l.config.AdminUserGroupCN(), sessions.UserRoleAdmin)
	if err != nil {
		l.lggr.Error("Error in ldapGroupMembersListToUser: ", err)
		return
	}
	// Query for list of uniqueMember IDs present in Edit group
	editUsers, err := l.ldapGroupMembersListToUser(conn, l.config.EditUserGroupCN(), sessions.UserRoleEdit)
	if err != nil {
		l.lggr.Error("Error in ldapGroupMembersListToUser: ", err)
		return
	}
	// Query for list of uniqueMember IDs present in Edit group
	runUsers, err := l.ldapGroupMembersListToUser(conn, l.config.RunUserGroupCN(), sessions.UserRoleRun)
	if err != nil {
		l.lggr.Error("Error in ldapGroupMembersListToUser: ", err)
		return
	}
	// Query for list of uniqueMember IDs present in Edit group
	readUsers, err := l.ldapGroupMembersListToUser(conn, l.config.ReadUserGroupCN(), sessions.UserRoleView)
	if err != nil {
		l.lggr.Error("Error in ldapGroupMembersListToUser: ", err)
		return
	}

	users = append(users, adminUsers...)
	users = append(users, editUsers...)
	users = append(users, runUsers...)
	users = append(users, readUsers...)

	// Dedupe preserving order of highest role (sorted)
	// Preserve members as a map for future lookup
	upstreamUserStateMap := make(map[string]sessions.User)
	dedupedEmails := []string{}
	for _, user := range users {
		if _, ok := upstreamUserStateMap[user.Email]; !ok {
			upstreamUserStateMap[user.Email] = user
			dedupedEmails = append(dedupedEmails, user.Email)
		}
	}

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
```

**File:** core/sessions/oidcauth/reaper.go (L37-50)
```go
func (sr *sessionReaper) Work(ctx context.Context) {
	recordCreationStaleThreshold := sr.config.SessionReaperExpiration().Before(
		sr.config.SessionTimeout().Before(time.Now()))
	err := sr.deleteStaleSessions(ctx, recordCreationStaleThreshold)
	if err != nil {
		sr.lggr.Error("unable to reap stale sessions: ", err)
	}
}

// DeleteStaleSessions deletes all sessions before the passed time.
func (sr *sessionReaper) deleteStaleSessions(ctx context.Context, before time.Time) error {
	_, err := sr.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE created_at < $1", before)
	return err
}
```

**File:** core/sessions/oidcauth/oidc.go (L297-338)
```go
// FindUserByAPIToken retrieves a possible stored user and role from the oidc_user_api_tokens table store
func (oi *oidcAuthenticator) FindUserByAPIToken(ctx context.Context, apiToken string) (clsessions.User, error) {
	if !oi.config.UserAPITokenEnabled() {
		return clsessions.User{}, errors.New("API token is not enabled")
	}

	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc user API token table for given token, user role and email are cached so
		// no further upstream OIDC query is performed, sessions and tokens are synced against the upstream server
		// via the UpstreamSyncInterval config and reaper.go sync implementation
		var foundUserToken struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundUserToken,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_user_api_tokens WHERE token_key = $1",
			apiToken, oi.config.UserAPITokenDuration().Duration(),
		); err != nil {
			return err
		}
		if !foundUserToken.Valid {
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundUserToken.UserEmail,
			Role:  foundUserToken.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			// API Token expired, purge
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_user_api_tokens WHERE token_key = $1", apiToken); execErr != nil {
				oi.lggr.Errorf("error purging stale oidc API token session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L349-391)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired
func (oi *oidcAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (clsessions.User, error) {
	if len(sessionID) == 0 {
		return clsessions.User{}, errors.New("session ID cannot be empty")
	}
	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc_sessions table for given session ID, user role and email are saved after the id claims is provided and validated
		var foundSession struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundSession,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_sessions WHERE id = $1",
			sessionID, oi.config.SessionTimeout().Duration(),
		); err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				return clsessions.ErrUserSessionExpired
			}
			return err
		}
		if !foundSession.Valid {
			// Sessions expired, purge
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundSession.UserEmail,
			Role:  foundSession.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE id = $1", sessionID); execErr != nil {
				oi.lggr.Errorf("error purging stale OIDC session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L393-402)
```go
// DeleteUser is not supported for read only OIDC
func (oi *oidcAuthenticator) DeleteUser(ctx context.Context, email string) error {
	return clsessions.ErrNotSupported
}

// DeleteUserSession removes an oidcSession table entry by ID
func (oi *oidcAuthenticator) DeleteUserSession(ctx context.Context, sessionID string) error {
	_, err := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE id = $1", sessionID)
	return err
}
```

**File:** core/web/auth/auth.go (L52-112)
```go
// AuthenticateBySession authenticates the request by the session cookie.
//
// Implements authMethod
func AuthenticateBySession(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	session := sessions.Default(c)
	sessionID, ok := session.Get(SessionIDKey).(string)
	if !ok {
		return auth.ErrorAuthFailed
	}

	user, err := authr.AuthorizedUserWithSession(ctx, sessionID)
	if err != nil {
		return err
	}

	c.Set(SessionUserKey, &user)

	return nil
}

var _ authMethod = AuthenticateBySession

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
