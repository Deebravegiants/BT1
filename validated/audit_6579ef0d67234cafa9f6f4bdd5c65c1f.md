Based on my review of `core/sessions/ldapauth/ldap.go` and `core/sessions/ldapauth/sync.go`, the claim's code citations and logical analysis are accurate. `AuthorizedUserWithSession` only checks the local `ldap_sessions` cache and its expiry timestamp, with no upstream LDAP re-validation. The background `Work()`/`run()` sync is only recurring when `UpstreamSyncInterval` is non-zero; with the documented default `0s`, it fires once at `Start()` and never again, confirmed at [1](#0-0) . This verifiably creates a window where a deactivated user's previously-issued session/token continues to grant access until `SessionTimeout` elapses, since per-request auth (`AuthenticateBySession`/`AuthenticateGQL`) never re-checks `active` status.

Audit Report

## Title
Deactivated LDAP User Retains Full Node Access Until Background Sync Runs (Default Disabled) - ([File: core/sessions/ldapauth/ldap.go])

## Summary
`ldapAuthenticator.AuthorizedUserWithSession`, which backs both cookie-session and GraphQL authentication, validates sessions purely against the local `ldap_sessions` cache and its expiry timestamp, without ever re-querying the upstream LDAP directory for the user's current `active` status or group membership. Revocation is delegated entirely to `LDAPServerStateSyncer.Work`, which by default (`UpstreamSyncInterval = '0s'`) runs only once at node startup and never again, meaning a session or API token issued before a user is deactivated upstream remains fully valid for its entire lifetime (`SessionTimeout`, default 15m, or up to `UserAPITokenDuration` of 240h for API tokens).

## Finding Description
`AuthorizedUserWithSession` performs a local-only check: [2](#0-1)  — it queries `SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_sessions WHERE id = $1` and returns the cached role if not expired, with no call to `validateUsersActive` or any upstream group-membership check.

The only mechanism that re-validates active/group status against the LDAP server is `LDAPServerStateSyncer.Work`, gated by `Start()`: [1](#0-0) . When `UpstreamSyncInterval.IsInstant()` (i.e., the documented default `'0s'`), the periodic `run()` goroutine is never started — `Work` executes exactly once at startup and is never triggered again by any subsequent per-request auth call, contradicting the package's own doc comment claiming sync "happens for every auth endpoint hit."

Both major auth entry points funnel through this insufficiently-checked function: `AuthenticateBySession` [3](#0-2)  and `AuthenticateGQL` [4](#0-3) , neither of which perform any additional active-status check beyond what `AuthorizedUserWithSession` provides.

## Impact Explanation
This is a broken session/credential revocation issue (CWE-613, Insufficient Session Expiration / improper invalidation) affecting LDAP-authenticated Chainlink nodes. An LDAP administrator deactivating a user (or removing their role-group membership) expects immediate loss of node API access; instead, the existing session cookie or API token continues to authorize requests at the user's previously-assigned role (Admin/Edit/Run/View) until natural session/token expiry, since the enforcement point (`AuthorizedUserWithSession`) never re-checks upstream state. This maps to the "node API authentication or role bypass" impact category, since a revoked identity retains authenticated role-based access to job management, key operations, and other admin API surfaces it should no longer have.

## Likelihood Explanation
Exploitation requires no attacker action beyond continued normal use of an already-issued, legitimately-obtained session/API token — no credential leak, host access, or additional attack technique is needed. It is triggered purely by the documented default configuration (`UpstreamSyncInterval = '0s'`) combined with the standard LDAP deactivation workflow that any LDAP-backed deployment would perform, making this readily reproducible in any default LDAP-auth node.

## Recommendation
- Re-validate the user's `active` status and/or current group membership against LDAP (or a short-TTL cache) inside `AuthorizedUserWithSession`, not only during `FindUser`/`CreateSession`/`ListUsers`.
- Do not allow `UpstreamSyncInterval = 0` to fully disable recurring revocation checks; either default to a safe non-zero interval or force a lightweight active-check on every `AuthorizedUserWithSession` call regardless of configured interval.
- Correct the `ldapauth` package doc comment, which inaccurately states sync happens "for every auth endpoint hit."

## Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'` and default `UpstreamSyncInterval = '0s'`.
2. A user logs in successfully; `CreateSession` inserts a row into `ldap_sessions` with role and `created_at` (`core/sessions/ldapauth/ldap.go` L437-452).
3. The LDAP administrator deactivates the user upstream (sets inactive attribute or removes all role-group memberships).
4. Because `UpstreamSyncInterval` is `0s`, `LDAPServerStateSyncer.run()` never fires again post-startup (`core/sessions/ldapauth/sync.go` L56-68), so `ldap_sessions` is never purged/updated for this user.
5. The deactivated user continues issuing authenticated requests; `AuthenticateBySession`/`AuthenticateGQL` call `AuthorizedUserWithSession`, which only checks local expiry and returns the still-cached role, granting continued access until `SessionTimeout` elapses (`core/sessions/ldapauth/ldap.go` L345-372).

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L345-372)
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

**File:** core/web/auth/gql.go (L25-47)
```go
func AuthenticateGQL(authenticator Authenticator, lggr logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := c.Request.Context()
		session := sessions.Default(c)
		sessionID, ok := session.Get(SessionIDKey).(string)
		if !ok {
			return
		}

		user, err := authenticator.AuthorizedUserWithSession(ctx, sessionID)
		if err != nil {
			if errors.Is(err, clsessions.ErrUserSessionExpired) {
				lggr.Warnw("Failed to authenticate session", "err", err)
			} else {
				lggr.Errorw("Failed call to AuthorizedUserWithSession, unable to get user", "err", err)
			}
			return
		}

		ctx = WithGQLAuthenticatedSession(c.Request.Context(), user, sessionID)

		c.Request = c.Request.WithContext(ctx)
	}
```
