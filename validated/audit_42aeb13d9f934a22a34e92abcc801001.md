Audit Report

## Title
Deactivated OIDC user retains persistent node access via cached session/API token with no upstream revocation check - ([File: core/sessions/oidcauth/oidc.go])

## Summary
The OIDC `oidcAuthenticator` caches a user's email and role in the `oidc_sessions` and `oidc_user_api_tokens` tables at login/token-issuance time and validates subsequent requests purely against this local cache with a time-based expiry check, never re-querying the upstream identity provider. This means a user deactivated or deprovisioned at the IdP after authenticating retains full API access for the remainder of the configured `SessionTimeout`/`UserAPITokenDuration` window, unlike the LDAP provider which implements an explicit upstream re-validation sync.

## Finding Description
`AuthorizedUserWithSession` [1](#0-0)  and `FindUserByAPIToken` [2](#0-1)  both validate solely via `created_at + duration >= now()` predicates against locally cached rows, with no call back to the OIDC provider's introspection/userinfo endpoint. These are the functions invoked by `AuthenticateBySession`/`AuthenticateByToken` on every authenticated API request [3](#0-2) .

Notably, the inline comment in `FindUserByAPIToken` claims "sessions and tokens are synced against the upstream server via the UpstreamSyncInterval config and reaper.go sync implementation" [4](#0-3) , but this claim is false for the OIDC path — `UpstreamSyncInterval` is an LDAP-only config option, and the OIDC `sessionReaper.Work` only performs a time-based `DELETE FROM oidc_sessions WHERE created_at < $1`, with no upstream query at all [5](#0-4) . This is confirmed by `grep` showing `UpstreamSyncInterval` only referenced in LDAP config/sync code, and appearing in `oidc.go` solely as this stale/incorrect comment.

By contrast, `LDAPServerStateSyncer.Work` explicitly re-queries the upstream directory, checks each user's active-attribute, and purges sessions/tokens for users no longer present or active upstream [6](#0-5) . No equivalent mechanism exists for OIDC, and `oidcAuthenticator.DeleteUser` is a hard no-op (`ErrNotSupported`) [7](#0-6) , meaning there is no automated or admin-triggerable path within the node itself to force revocation of a deactivated OIDC user's live session/token.

## Impact Explanation
Any OIDC-authenticated user (including admin/edit-role) who is deactivated, removed from group claims, or deprovisioned at the upstream identity provider after obtaining a session cookie or API token continues to be treated as fully authorized by the node for the entire `SessionTimeout` or `UserAPITokenDuration` window, since role/email are cached and never revalidated. This maps to the node API authentication/role-bypass impact category, as it allows continued privileged actions (job management, bridge/key management, potentially fund-moving operations) by an account whose authorization has been revoked at the source of truth.

## Likelihood Explanation
Exploitation requires only that a previously-authenticated OIDC user's session or API token is still within its local validity window when their account is deactivated upstream — a scenario every OIDC-authenticated deployment must handle, and one explicitly solved for the LDAP provider in this same codebase. The behavior is deterministic and repeatable: as long as the row hasn't hit the local timeout, `AuthorizedUserWithSession`/`FindUserByAPIToken` will succeed regardless of upstream state.

## Recommendation
Implement an upstream revalidation mechanism for OIDC analogous to `LDAPServerStateSyncer.Work`, e.g., periodically call the provider's token introspection or userinfo endpoint (or re-verify group claims) for cached `oidc_sessions`/`oidc_user_api_tokens` entries and purge/downgrade rows for users no longer active/authorized upstream. At minimum, correct the misleading comment in `FindUserByAPIToken` and implement the sync functionality it currently claims exists.

## Proof of Concept
1. Configure the node with `AuthenticationMethod = "oidc"` and a working IdP.
2. An admin-role user completes login via `handleTokenExchange`, obtaining a session cookie backed by `oidc_sessions`, or provisions an API token via `SetAuthToken` backed by `oidc_user_api_tokens`.
3. The IdP administrator deactivates the user or removes them from the admin group.
4. Before `SessionTimeout`/`UserAPITokenDuration` elapses, the (now-revoked) session cookie or API token is used against any authenticated node endpoint — `AuthorizedUserWithSession`/`FindUserByAPIToken` return the stale cached admin role, and the request succeeds, confirmed by tracing the SQL predicates in `core/sessions/oidcauth/oidc.go` lines 363-366 and 313-316, which contain no upstream check.

### Citations

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

**File:** core/sessions/oidcauth/oidc.go (L393-396)
```go
// DeleteUser is not supported for read only OIDC
func (oi *oidcAuthenticator) DeleteUser(ctx context.Context, email string) error {
	return clsessions.ErrNotSupported
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
