### Title
LDAP-backed users retain cached role/session permissions after upstream disable or role revocation until an optional resync occurs - (File: core/sessions/ldapauth/sync.go)

### Summary
The `LDAPServerStateSyncer` is the only mechanism that revalidates a logged-in LDAP user's active status and role against the upstream directory. When `WebServer.LDAP.UpstreamSyncInterval` is left at its documented default of `'0s'`, the periodic resync loop never runs after node startup, so a user disabled or demoted upstream keeps full access under their originally cached role for the life of their existing session/API token.

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession` never re-checks the upstream LDAP server on a per-request basis. It only looks at the locally cached `ldap_sessions` row (keyed by session ID) and checks whether the row has expired relative to `SessionTimeout`: [1](#0-0) 

The only code path that re-validates a user's `active` attribute or role membership against the upstream LDAP server is `LDAPServerStateSyncer.Work`, which purges/updates `ldap_sessions` and `ldap_user_api_tokens` rows for users no longer present or active upstream: [2](#0-1) 

Crucially, `Start` only schedules this resync on a recurring basis if `UpstreamSyncInterval` is non-zero; if it is zero (`IsInstant()` true, which is the documented default), `Work` is called exactly once, at node startup, and never again: [3](#0-2) [4](#0-3) 

The package-level doc comment for `ldapauth` claims "This sync happens for every auth endpoint hit, and via the defined sync interval," but this is not reflected in `AuthorizedUserWithSession`'s actual implementation, which performs no upstream check: [5](#0-4) 

As a direct consequence: an admin disabling a user's `ActiveAttribute` upstream, removing them from a role group, or demoting their role does not immediately revoke that user's already-issued web session or long-lived API token (`ldap_user_api_tokens`, default duration `240h`) — this is the same bug class as CVE-2020-13230 (Cacti: disabling a user account does not immediately invalidate granted permissions).

### Impact Explanation
A disabled/demoted LDAP-authenticated Chainlink node user retains their previously granted role (e.g., Admin) and continues to be authorized for privileged node API operations (job management, key/bridge access, log viewing, etc.) for up to the full `SessionTimeout` (web session, default `15m`) or, more severely, up to `UserAPITokenDuration` (API token, default `240h`/10 days) after being disabled upstream — with default config where `UpstreamSyncInterval` is `0s`, this persists indefinitely until the node is restarted, since no periodic revalidation occurs at all after boot.

### Likelihood Explanation
This requires no attacker action beyond already having had legitimate LDAP-based access prior to being disabled/demoted — a realistic, unprivileged-actor-relevant scenario (a departing or compromised account that admins believe they have revoked). It is triggered purely by the default configuration behavior (`UpstreamSyncInterval = '0s'`), not by a bug in an external/mocked/network-layer component.

### Recommendation
- Change the default/documented behavior so that `UpstreamSyncInterval` defaults to a non-zero recurring value, or explicitly perform an upstream active/role check inside `AuthorizedUserWithSession` (with reasonable caching) rather than relying solely on a possibly-disabled background sync.
- Ensure `ldap_user_api_tokens` are also subject to the same immediate-revocation checks, since their default duration (`240h`) makes stale privilege retention especially severe.
- Update the misleading doc comment in `core/sessions/ldapauth/ldap.go` claiming sync happens "for every auth endpoint hit."

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'` and leave `WebServer.LDAP.UpstreamSyncInterval` at its default (`'0s'`).
2. A user in the `AdminUserGroupCN` group logs in, creating a row in `ldap_sessions` with `user_role = 'admin'` (`CreateSession`, `core/sessions/ldapauth/ldap.go:396-457`).
3. An LDAP administrator disables the user's account (sets the `ActiveAttribute` to inactive) or removes them from the admin group upstream.
4. Because `Start` only runs `Work` once at startup (`core/sessions/ldapauth/sync.go:56-68`), the local `ldap_sessions` row is never purged/updated.
5. The disabled user continues making authenticated requests using the existing session cookie; `AuthorizedUserWithSession` (`core/sessions/ldapauth/ldap.go:345-373`) returns the stale cached `admin` role without any upstream check, granting continued admin-level API access until the session naturally expires at `SessionTimeout`.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L1-23)
```go
/*
The LDAP authentication package forwards the credentials in the user session request
for authentication with a configured upstream LDAP server

This package relies on the two following local database tables:

	ldap_sessions: 	Upon successful LDAP response, creates a keyed local copy of the user email
	ldap_user_api_tokens: User created API tokens, tied to the node, storing user email.

Note: user can have only one API token at a time, and token expiration is enforced

User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function

This implementation is read only; user mutation actions such as Delete are not supported.

MFA is supported via the remote LDAP server implementation. Sufficient request time out should accommodate
for a blocking auth call while the user responds to a potential push notification callback.
*/
```

**File:** core/sessions/ldapauth/ldap.go (L345-373)
```go
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

**File:** docs/CONFIG.md (L663-683)
```markdown
## WebServer.LDAP
```toml
[WebServer.LDAP]
ServerTLS = true # Default
SessionTimeout = '15m0s' # Default
QueryTimeout = '2m0s' # Default
BaseUserAttr = 'uid' # Default
BaseDN = 'dc=custom,dc=example,dc=com' # Example
UsersDN = 'ou=users' # Default
GroupsDN = 'ou=groups' # Default
ActiveAttribute = '' # Default
ActiveAttributeAllowedValue = '' # Default
AdminUserGroupCN = 'NodeAdmins' # Default
EditUserGroupCN = 'NodeEditors' # Default
RunUserGroupCN = 'NodeRunners' # Default
ReadUserGroupCN = 'NodeReadOnly' # Default
UserApiTokenEnabled = false # Default
UserAPITokenDuration = '240h0m0s' # Default
UpstreamSyncInterval = '0s' # Default
UpstreamSyncRateLimit = '2m0s' # Default
```
```
