### Title
Disabled/deactivated LDAP users retain valid sessions and API tokens until natural expiry — ([File: core/sessions/ldapauth/ldap.go])

### Summary
Chainlink's LDAP authentication provider caches session and API-token state locally and only re-validates a user's "active" status against the upstream LDAP directory at login time or via a background sync job. The request-time authentication paths (`AuthorizedUserWithSession` and `FindUserByAPIToken`) never re-check the upstream active/deactivated attribute — they only check local expiry. Combined with the default configuration (`UpstreamSyncInterval = '0s'`, which disables the periodic background sync entirely), a user who is disabled/deactivated/removed from the LDAP directory after establishing a session or API token can continue to authenticate and act on the node for the full remaining lifetime of that cached credential — up to the `SessionTimeout` (default 15m) for sessions, or `UserAPITokenDuration` (default 240h / 10 days) for API tokens.

### Finding Description
The package-level doc comment for `ldapauth` claims:
> "User session and roles are cached and revalidated with the upstream service at the interval defined in the local LDAP config... This sync happens for every auth endpoint hit, and via the defined sync interval." [1](#0-0) 

In practice, this is not true for the two functions that are actually invoked on every authenticated HTTP request:

- `AuthorizedUserWithSession` (called on every session-cookie-authenticated request) only queries the local `ldap_sessions` cache table for expiry — it performs no upstream/active check: [2](#0-1) 

- `FindUserByAPIToken` (called on every API-token-authenticated request) similarly only checks local `ldap_user_api_tokens` for expiry: [3](#0-2) 

Both are wired directly into the request-handling authentication middleware: [4](#0-3) 

The only place `validateUsersActive` (the upstream "active" check) is invoked is in `FindUser` (used at login time via `CreateSession`) and in the background `LDAPServerStateSyncer.Work` job: [5](#0-4) [6](#0-5) 

Critically, the background sync is gated by `UpstreamSyncInterval`, which defaults to `'0s'` — explicitly documented as disabling the interval-based sync (it only runs once at `Start()`): [7](#0-6) [8](#0-7) 

So with default configuration, after the one-time sync at node startup, there is no mechanism that re-validates a live session or API token against the upstream directory's active/disabled state until that session/token naturally expires (15m / 10 days respectively) or the LDAP admin manually restarts the node. A newly-disabled user's *existing* session cookie or API token remains fully valid and usable for the entire remaining TTL.

### Impact Explanation
This matches the CVE-2023-31211 bug class: an authentication flow that fails to promptly enforce a "disabled/locked" account state, allowing a supposedly deactivated identity to continue authenticating and performing privileged actions on the node (job creation, config changes, key management, fund-moving bridge/job operations depending on the role cached in the session, e.g. `UserRoleAdmin`/`UserRoleEdit`). Given `UserAPITokenDuration` defaults to 10 days, a disabled admin's API token could be usable by an attacker (or by the disabled/terminated employee) for up to 10 days after the operator believes access was revoked.

### Likelihood Explanation
This requires no special network position — it is a normal, unprivileged-but-previously-authenticated actor retaining access using credentials/session/token they already legitimately obtained before being disabled. It is triggered simply by using the default `UpstreamSyncInterval = '0s'` configuration (the documented default), which is the out-of-box behavior; no misconfiguration beyond defaults is needed.

### Recommendation
Perform (or at minimum offer an option to perform) an upstream active-status check inside `AuthorizedUserWithSession` and `FindUserByAPIToken`, or reduce reliance on a disabled-by-default background sync. At minimum, update documentation to accurately reflect that active-status is not rechecked per-request, and make `UpstreamSyncInterval` a mandatory positive value (or default to a short interval) so that revocation propagates promptly rather than only at process restart.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `WebServer.LDAP.ActiveAttribute` set (e.g., `organizationalStatus`) and leave `UpstreamSyncInterval` at its default `'0s'`.
2. As a normal LDAP user, log in via `POST /sessions` to obtain a session cookie, or call `NewAPIToken` to obtain an API token while account is active.
3. Have the LDAP administrator mark the account inactive/disabled/locked in the upstream directory (no chainlink-side action taken).
4. Continue making authenticated requests using the previously obtained session cookie or API key/secret; observe `AuthorizedUserWithSession`/`FindUserByAPIToken` succeed because they only check local expiry (`created_at + duration >= now()`), not upstream active state, until the node is restarted or the credential naturally expires.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
```

**File:** core/sessions/ldapauth/ldap.go (L114-142)
```go
// FindUser will attempt to return an LDAP user with mapped role by email.
func (l *ldapAuthenticator) FindUser(ctx context.Context, email string) (sessions.User, error) {
	email = strings.ToLower(email)

	// First check for the supported local admin users table
	var foundLocalAdminUser sessions.User
	checkErr := l.ds.GetContext(ctx, &foundLocalAdminUser, "SELECT * FROM users WHERE lower(email) = lower($1)", email)
	if checkErr == nil {
		return foundLocalAdminUser, nil
	}
	// If error is not nil, there was either an issue or no local users found
	if !errors.Is(checkErr, sql.ErrNoRows) {
		// If the error is not that no local user was found, log and exit
		l.lggr.Errorf("error searching users table: %v", checkErr)
		return sessions.User{}, errors.New("error Finding user")
	}

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

**File:** core/web/auth/auth.go (L55-112)
```go
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

**File:** core/config/docs/core.toml (L267-269)
```text
UserAPITokenDuration = '240h0m0s' # Default
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
```
