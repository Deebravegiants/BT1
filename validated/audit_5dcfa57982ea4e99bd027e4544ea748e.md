### Title
Deactivated/revoked LDAP users retain valid session and API token access until natural expiry — ([File: core/sessions/ldapauth/ldap.go])

### Summary
The LDAP authentication provider's session and API-token validation paths (`AuthorizedUserWithSession`, `FindUserByAPIToken`) only check whether a cached local record has aged past its configured timeout — they never re-check the user's "active" status against the upstream LDAP directory at request time. Deactivation propagation depends entirely on a separate background sync job (`Work()` in `core/sessions/ldapauth/sync.go`) that, by default configuration (`UpstreamSyncInterval = '0s'`), only runs once at node startup and is not re-triggered on a timer unless an operator explicitly configures a non-zero interval. This is directly analogous to the Gogs/PAM CVE-2022-0871 bug class: an account that has been expired/deactivated upstream continues to be treated as valid by the application until an unrelated, much longer expiry window elapses.

### Finding Description
`AuthorizedUserWithSession` in `core/sessions/ldapauth/ldap.go` (lines 342-373) validates a session purely via:
```
"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_sessions WHERE id = $1"
``` [1](#0-0) 
No call is made to the upstream LDAP server or to `validateUsersActive` on this path. The same pattern exists in `FindUserByAPIToken` (lines 204-236), which only checks `created_at + UserAPITokenDuration >= now()`. [2](#0-1) 

The only mechanism that removes access for a deactivated/removed upstream user is `LDAPServerStateSyncer.Work()`, which purges `ldap_sessions`/`ldap_user_api_tokens` rows for users no longer present/active upstream. [3](#0-2) 
That job is only scheduled on a recurring ticker `if !l.config.UpstreamSyncInterval().IsInstant()`; otherwise it is executed exactly once, at `Start()`. [4](#0-3) 
The default value for `UpstreamSyncInterval` is `'0s'`, and the doc comment for the config explicitly states this "disables the background sync being run on an interval," relying only on a check "performed during login/logout actions." [5](#0-4) 

Because `AuthorizedUserWithSession` and `FindUserByAPIToken` never invoke revalidation against the upstream directory, a user who is deactivated, removed from a role group, or has an expired upstream account keeps full API/GUI access for the remaining life of their existing session (`SessionTimeout`, default `15m`) or, far more significantly, for the remaining life of their API token (`UserAPITokenDuration`, default `240h0m0s` = 10 days) unless the operator has manually configured a recurring `UpstreamSyncInterval`. [6](#0-5) 

This mirrors the Gogs PAM flaw: authentication/authorization state ("is this account still valid") is cached and trusted for a duration disconnected from the actual upstream state change, so revocation at the identity provider does not translate into an immediate access revocation in Chainlink.

### Impact Explanation
An LDAP-integrated Chainlink node continues to authorize requests from a user whose access was revoked upstream (e.g., employee offboarding, compromised-account lockout, group/role demotion) for as long as 10 days by default via a still-valid API token, or up to 15 minutes via an active session — regardless of the administrator's intent to immediately cut off access. Given that `UserAPITokenEnabled` grants the same authorization as the underlying role (including up to Admin), this is a legitimate authorization-bypass/stale-credential risk with real operational impact for node operators relying on LDAP for centralized identity control.

### Likelihood Explanation
Any deployment using the default `UpstreamSyncInterval = '0s'` (the documented default) is affected without any special configuration mistake — this is the out-of-box behavior. The only way to close the window is for operators to explicitly configure a recurring sync interval, which is not enforced or warned about at startup.

### Recommendation
Re-validate (or at minimum periodically force-validate) upstream active status inside `AuthorizedUserWithSession` and `FindUserByAPIToken` rather than relying solely on local record age, or enforce a mandatory maximum `UpstreamSyncInterval` default that is short enough to bound the exposure window; additionally, surface a startup warning when `UpstreamSyncInterval` is `0s` and `ActiveAttribute` is configured, since that combination effectively disables continuous revocation enforcement.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `ActiveAttribute` set, and leave `UpstreamSyncInterval` at its default `'0s'`.
2. User logs in and/or creates a long-lived API token (`UserAPITokenDuration` default 240h).
3. Administrator deactivates the user's account / removes group membership upstream in LDAP.
4. Because no recurring sync runs, `ldap_sessions`/`ldap_user_api_tokens` rows are never purged.
5. The user continues to successfully call authenticated endpoints via `AuthorizeUserWithSession`/`FindUserByAPIToken`, which only checks local row age, not upstream active state, until the token/session naturally expires.

### Citations

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

**File:** core/config/docs/core.toml (L199-233)
```text
# SessionTimeout determines the amount of idle time to elapse before session cookies expire. This signs out GUI users from their sessions.
SessionTimeout = '15m' # Default
# SessionReaperExpiration represents how long an API session lasts before expiring and requiring a new login.
SessionReaperExpiration = '240h' # Default
# HTTPMaxSize defines the maximum size for HTTP requests and responses made by the node server.
HTTPMaxSize = '32768b' # Default
# StartTimeout defines the maximum amount of time the node will wait for a server to start.
StartTimeout = '15s' # Default
# ListenIP specifies the IP to bind the HTTP server to
ListenIP = '0.0.0.0' # Default

# Optional OIDC config if WebServer.AuthenticationMethod is set to 'oidc'
[WebServer.OIDC]
# ClientID is the ID of the OIDC application registered with the identity provider
ClientID = 'abcd1234' # Example
# ProviderURL is the base URL for your OIDC Identity provider.
ProviderURL = 'https://id[.]example[.]com/oauth2/default' # Example
# RedirectURL will always be <NODE_BASE_URL>/signin. This needs to match the configuration on the provider side.
RedirectURL = 'http://localhost:8080/signin' # Example
# ClaimName is the name of the field in the id_token where to find the user's ID claims.
ClaimName = 'groups' # Default
# AdminClaim is string label of the id claim that maps the core node's 'Admin' role
AdminClaim = 'NodeAdmins' # Default
# EditClaim is string label of the id claim that maps the core node's 'Edit' role
EditClaim = 'NodeEditors' # Default
# RunClaim is string label of the id claim that maps the core node's 'Run' role
RunClaim = 'NodeRunners' # Default
# ReadClaim is string label of the id claim that maps the core node's 'Read' role
ReadClaim = 'NodeReadOnly' # Default
# SessionTimeout determines the amount of idle time to elapse before session cookies expire. This signs out GUI users from their sessions.
SessionTimeout = '15m0s' # Default
# UserAPITokenEnabled enables the users to issue API tokens with the same access of their role
UserAPITokenEnabled = false # Default
# UserAPITokenDuration is the duration of time an API token is active for before expiring
UserAPITokenDuration = '240h0m0s' # Default
```

**File:** core/config/docs/core.toml (L268-269)
```text
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
```
