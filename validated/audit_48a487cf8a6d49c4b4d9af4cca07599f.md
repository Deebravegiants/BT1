This confirms the technical claim is accurate: `AuthenticateBySession` calls `AuthorizedUserWithSession` directly per request with no per-request upstream LDAP resync, and `LDAPServerStateSyncer.Start` only runs `Work` once when `UpstreamSyncInterval` is the documented default `0s`.Audit Report

## Title
LDAP-backed users retain cached role/session permissions after upstream disable or role revocation until an optional resync occurs - (File: core/sessions/ldapauth/sync.go)

## Summary
`ldapAuthenticator.AuthorizedUserWithSession` authenticates every LDAP-backed request purely against the locally cached `ldap_sessions` row, with no per-request upstream check. The only mechanism that revalidates a user's active status/role against the upstream LDAP directory is `LDAPServerStateSyncer.Work`, and `Start` only schedules this on a recurring basis if `UpstreamSyncInterval` is non-zero; at its documented default of `'0s'`, `Work` runs exactly once at node startup and never again, so a user disabled or demoted upstream keeps full access under their originally cached role for the life of their session/API token.

## Finding Description
`AuthenticateBySession` (`core/web/auth/auth.go:55-71`) is the middleware invoked on every authenticated web request, and it calls `authr.AuthorizedUserWithSession(ctx, sessionID)` directly, with no upstream LDAP query involved. [1](#0-0) 

`ldapAuthenticator.AuthorizedUserWithSession` (`core/sessions/ldapauth/ldap.go:345-373`) only queries the local `ldap_sessions` table and checks expiry relative to `SessionTimeout`; it performs no call to the upstream LDAP server and returns the cached `user_role` as-is. [2](#0-1) 

The only code that re-validates active/role state against the upstream server is `LDAPServerStateSyncer.Work`, which purges/updates `ldap_sessions` and `ldap_user_api_tokens` for users no longer present or active upstream. [3](#0-2) 

Crucially, `Start` only schedules `Work` on a recurring timer if `UpstreamSyncInterval().IsInstant()` is false (i.e., non-zero); when the interval is the documented default `'0s'`, `Work` is invoked exactly once at startup via the `else` branch and never again. [4](#0-3) 

The package doc comment claims sync "happens for every auth endpoint hit," but this is contradicted by the actual `AuthorizedUserWithSession` implementation, which performs no upstream check whatsoever — confirming the doc comment is inaccurate and the real behavior matches the claim. [5](#0-4) 

The documented default configuration explicitly sets `UpstreamSyncInterval = '0s'`, confirming this is the out-of-the-box behavior, not a misconfiguration requiring unusual operator action. [6](#0-5) 

## Impact Explanation
A disabled/demoted LDAP-authenticated node user retains their previously cached role (e.g., Admin) and continues to be authorized for privileged node API operations for up to `SessionTimeout` (web session, default `15m`) or up to `UserAPITokenDuration` (API token, default `240h`/10 days) — and with the default `UpstreamSyncInterval = '0s'`, this persists indefinitely (no revalidation at all after boot) until the node process is restarted. This maps to an in-scope "node API authentication or role bypass" impact class: stale/unauthorized privilege retention despite upstream revocation, analogous to CVE-2020-13230.

## Likelihood Explanation
This requires no special attacker capability beyond having had legitimate prior access before being disabled/demoted upstream — a realistic scenario (departing employee, compromised account being remediated by an admin who reasonably expects the disable to take effect promptly). It is triggered purely by default configuration values and normal continued use of an already-authenticated session/token, not by any additional exploit action, host access, or social engineering. This is a genuine logic gap in the security assumption that "sync happens for every auth endpoint hit," which the code does not implement.

## Recommendation
- Perform an upstream active/role check (with reasonable caching/rate limiting) directly inside `AuthorizedUserWithSession`, rather than relying solely on the background `LDAPServerStateSyncer`.
- Change the default behavior so `UpstreamSyncInterval` is non-zero, or explicitly warn/log prominently when it is left at `'0s'` that revocation propagation is startup-only.
- Apply the same immediate revocation check to `ldap_user_api_tokens`, given their much longer default duration (`240h`).
- Correct the misleading doc comment in `core/sessions/ldapauth/ldap.go` claiming sync happens "for every auth endpoint hit."

## Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'`, leaving `WebServer.LDAP.UpstreamSyncInterval` at its default `'0s'`.
2. A user in `AdminUserGroupCN` logs in, creating an `ldap_sessions` row with `user_role = 'admin'`.
3. An LDAP administrator disables the user's account upstream (sets `ActiveAttribute` inactive) or removes them from the admin group.
4. Because `Start` (`core/sessions/ldapauth/sync.go:56-68`) only runs `Work` once at startup under the default `0s` interval, the local `ldap_sessions` row is never purged/updated.
5. The disabled user continues making authenticated requests with the existing session cookie; `AuthorizedUserWithSession` (`core/sessions/ldapauth/ldap.go:345-373`) returns the stale cached `admin` role with no upstream check, granting continued admin-level API access (e.g., calling an admin-only endpoint guarded by `RequiresAdminRole` in `core/web/auth/auth.go:237-253`) until natural session expiry at `SessionTimeout`, or up to `UserAPITokenDuration` for an API token. [7](#0-6)

### Citations

**File:** core/web/auth/auth.go (L55-71)
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
```

**File:** core/web/auth/auth.go (L237-253)
```go
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
