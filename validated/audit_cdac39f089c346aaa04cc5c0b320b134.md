I've verified the code matches the claim's citations exactly.

Audit Report

## Title
Revoked/deactivated LDAP user role not re-enforced during session/API-token lifetime when `UpstreamSyncInterval` is left at its default `'0s'` — ([File: core/sessions/ldapauth/sync.go], [File: core/sessions/ldapauth/ldap.go])

## Summary
`ldapAuthenticator.AuthorizedUserWithSession` and `FindUserByAPIToken` only query the locally cached `ldap_sessions`/`ldap_user_api_tokens` tables and check time-based expiry; they never re-validate the cached role/active-status against the upstream LDAP directory on the request path. Re-validation only happens in `LDAPServerStateSyncer.Work`, which is invoked either on a recurring ticker (only started if `UpstreamSyncInterval` is non-zero) or exactly once at node startup when the interval is the documented default `'0s'`. This means a revoked/demoted LDAP user's previously issued session cookie or API token continues to grant its cached (possibly Admin) role until it naturally expires (`SessionTimeout` default 15m, `UserAPITokenDuration` default 240h), contradicting the package doc's claim that sync "happens for every auth endpoint hit."

## Finding Description [1](#0-0) [2](#0-1) 
Both authenticated-request entry points read only cached rows and check `created_at + duration >= now()`, with no LDAP callback. Live re-validation is confined to `LDAPServerStateSyncer.Work`: [3](#0-2) 
And `Start` only runs `Work` on a recurring ticker if `UpstreamSyncInterval` is non-zero; otherwise it fires `Work` exactly once at startup: [4](#0-3) 
The package doc comment inaccurately states revocation "propagate[s] through... for every auth endpoint hit": [5](#0-4) 
No code path (session/token lookup, `CreateSession`, or auth middleware) calls `Work` from the request path, so the documented default (`UpstreamSyncInterval = '0s'`) leaves revocation enforcement to the one-time startup sync only, until the node is restarted or an operator configures a non-zero interval.

## Impact Explanation
This is a legitimate logic bug in the LDAP authentication provider: an already-authenticated session/API token retains its cached role even after the underlying LDAP identity is revoked, demoted, or deactivated, for as long as the token/session validity window remains (`SessionTimeout` default 15m; `UserAPITokenDuration` default 240h/10 days). This is an authentication/role-bypass class issue in Chainlink's own code (not a dependency or misconfiguration bug), since the default shipped configuration value (`UpstreamSyncInterval = '0s'`) produces this exact behavior, and the code comments actively misrepresent the guarantee provided.

## Likelihood Explanation
This requires the node operator to opt into `WebServer.AuthenticationMethod = 'ldap'` (an enterprise-only, opt-in feature) and to not override the shipped default `UpstreamSyncInterval = '0s'`. The exploit does not require an unprivileged external attacker to trigger anything new — it requires that a previously legitimate credential (session cookie or API token) obtained by a user who is later revoked continues to work past the point of revocation. This is a genuine escalation-of-persistence bug (stale privilege retention) rather than something purely reachable by an unprivileged, uncredentialed client from scratch, but it is a real flaw in the authorization/revocation logic that Chainlink ships and documents incorrectly.

## Recommendation
- Perform a live LDAP/group-membership and active-status check (or at least trigger a cache re-validation) inside `AuthorizedUserWithSession` and `FindUserByAPIToken` on the authenticated request path, or
- Change the default value of `UpstreamSyncInterval` so background sync is active by default instead of disabled, and/or enforce a maximum staleness bound on cached roles independent of the configured interval.
- Correct the doc comment in `core/sessions/ldapauth/ldap.go` (lines 12–17) to accurately state that live revocation propagation is contingent on `UpstreamSyncInterval` being configured to a non-zero value, and that with the default `'0s'` value, sync only occurs once at node startup.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` and leave `WebServer.LDAP.UpstreamSyncInterval` unset (default `'0s'`).
2. Log in as an LDAP user in the Admin group via `CreateSession` to obtain a session cookie, or call the API-token creation endpoint to obtain a token valid up to 240h.
3. On the upstream LDAP server, remove the user from the Admin group or flip `ActiveAttribute` to inactive.
4. Continue issuing authenticated Admin-role requests using the previously obtained session/token — `AuthorizedUserWithSession`/`FindUserByAPIToken` (core/sessions/ldapauth/ldap.go, lines 204-235 and 342-372) will keep returning the stale cached Admin role until the session/token naturally expires or the node restarts, since `LDAPServerStateSyncer.Work` (core/sessions/ldapauth/sync.go, lines 56-68) only ran once at startup.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
```

**File:** core/sessions/ldapauth/ldap.go (L204-235)
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
```

**File:** core/sessions/ldapauth/ldap.go (L342-372)
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
