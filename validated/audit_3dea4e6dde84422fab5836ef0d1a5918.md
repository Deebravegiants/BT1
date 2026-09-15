Audit Report

## Title
Stale LDAP-cached session role bypasses upstream revocation due to purely cache-based per-request authorization check - (File: core/sessions/ldapauth/ldap.go)

## Summary
`ldapAuthenticator.AuthorizedUserWithSession`, the per-request authorization function used by `AuthenticateBySession` for every gin request, only reads the locally cached `user_email`/`user_role` from the `ldap_sessions` table and checks a time-based expiry — it never re-queries the LDAP directory or triggers the revocation-sync logic (`LDAPServerStateSyncer.Work`). Combined with the documented default `UpstreamSyncInterval = '0s'` (which disables the periodic background sync and only runs `Work` at node startup), a user whose LDAP group membership/role is revoked upstream keeps their previously cached, potentially privileged role for the lifetime of their existing session/API token.

## Finding Description
`AuthorizedUserWithSession` at core/sessions/ldapauth/ldap.go:345-373 executes:
```go
if err := l.ds.GetContext(ctx, &foundSession,
    "SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_sessions WHERE id = $1",
    sessionID, l.config.SessionTimeout().Duration(),
); ...
``` [1](#0-0) 

This function is the sole authorization check called on every authenticated request via `AuthenticateBySession`: [2](#0-1) 

It contains no call to `LDAPServerStateSyncer.Work`, no LDAP directory query, and no cross-check against current upstream group membership — it purely validates that the cached row hasn't exceeded `SessionTimeout`. The only code path that reconciles cached roles/sessions against the upstream LDAP source of truth (purging removed users, updating roles for changed users) is `LDAPServerStateSyncer.Work`, which runs on node startup, on a configured timer (only if `UpstreamSyncInterval` is non-zero), or during explicit login/logout: [3](#0-2) [4](#0-3) 

The documented default leaves `UpstreamSyncInterval` at `'0s'`, which explicitly disables the timer-based sync and defers all revocation enforcement to login/logout/startup events: [5](#0-4) 

This is a genuine gap between the package's own doc comment claiming sync happens "for every auth endpoint hit" and the actual implementation of `AuthorizedUserWithSession`, which contains no such trigger. The security assumption broken is that a session's cached role reflects current upstream authorization state; instead it reflects a snapshot from the last sync event, which — under the default configuration — may be arbitrarily stale relative to any single already-authenticated user's continued API access.

## Impact Explanation
A user who was legitimately authenticated (e.g., granted Admin role via LDAP group membership) and subsequently demoted or removed from that group upstream retains their previously cached elevated role for all subsequent requests using their existing session cookie or API token, until an unrelated sync event occurs. This is a concrete node API role/authorization bypass: a de-privileged actor can continue to exercise Admin-level operations (job management, key access, node configuration) using a session that should have been revoked. This maps to the in-scope "node API authentication or role bypass" impact category.

## Likelihood Explanation
Exploitation requires the deployment to use `WebServer.AuthenticationMethod = 'ldap'` and does not require any special privilege from the exploiting party beyond continued possession of a session/API token that was validly issued prior to their demotion — this is not privileged/host/db access, and the "attacker" here is simply the now-de-privileged holder of previously valid credentials reusing them normally through the standard API. With the documented default `UpstreamSyncInterval = '0s'`, the exposure window is bounded only by `SessionTimeout`/`UserAPITokenDuration` and by whether some other login/logout event happens to trigger `Work` in the interim, making this readily reproducible in a default-configured LDAP deployment.

## Recommendation
- Re-validate session role against a recent/authoritative sync state (or the LDAP server directly) within `AuthorizedUserWithSession`, or enforce a mandatory maximum cache lifetime independent of `UpstreamSyncInterval`.
- Do not allow `UpstreamSyncInterval = '0s'` to fully disable periodic reconciliation; require a bounded default interval.
- Tighten `SessionTimeout`/`UserAPITokenDuration` relative to the sync interval so stale privileged roles cannot persist indefinitely.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with default `UpstreamSyncInterval = '0s'` and a long `SessionTimeout`.
2. User A authenticates while a member of the LDAP Admin group; `CreateSession` inserts `ldap_sessions` row with `user_role = 'admin'` (core/sessions/ldapauth/ldap.go:440-452).
3. Admin removes User A from the Admin group upstream.
4. With no other login/logout triggering `Work`, User A continues issuing authenticated requests using their existing session cookie; `AuthenticateBySession` → `AuthorizedUserWithSession` (core/sessions/ldapauth/ldap.go:345-373) returns the stale cached `user_role = 'admin'`, granting continued Admin API access.
5. Verify via integration test: seed `ldap_sessions` with a role, simulate upstream group removal (mock LDAP client returning updated membership without User A), call `AuthorizedUserWithSession` without invoking `Work`, and assert it still returns the stale privileged role.

### Citations

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

**File:** core/web/auth/auth.go (L52-71)
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

**File:** core/sessions/ldapauth/sync.go (L214-243)
```go
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

**File:** core/config/docs/core.toml (L268-270)
```text
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
# UpstreamSyncRateLimit defines a duration to limit the number of query/API calls to the upstream LDAP provider. It prevents the sync functionality from being called multiple times within the defined duration
```
