Based on the investigation, I found a concrete analog in the LDAP authentication provider's stale-role caching design.

### Title
Stale cached role in `ldap_sessions`/`ldap_user_api_tokens` allows revoked LDAP users to retain elevated privileges - (File: `core/sessions/ldapauth/sync.go`, `core/sessions/ldapauth/ldap.go`)

### Summary
`ERC20ConvictionScore` cached a per-user `isGovernance` flag that only got refreshed lazily, so a threshold change didn't immediately propagate to already-cached user state, creating an inconsistent authorization window. The chainlink LDAP authenticator has the same structural flaw: a user's `role` is cached in the `ldap_sessions` / `ldap_user_api_tokens` tables at authentication time and is only refreshed by the periodic `LDAPServerStateSyncer.Work` job, not on every request.

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession` and `FindUserByAPIToken` read the cached `user_role` directly from the local `ldap_sessions`/`ldap_user_api_tokens` tables and never re-query the upstream LDAP server: [1](#0-0) [2](#0-1) 

The only mechanism that refreshes these roles from upstream group membership is `LDAPServerStateSyncer.Work`, gated by `UpstreamSyncInterval`/`UpstreamSyncRateLimit`: [3](#0-2) 

If `UpstreamSyncInterval` is left at its documented default of `'0s'`, `IsInstant()` is true and the periodic goroutine (`l.run()`) is never started at all — `Work` is invoked exactly once, at node startup: [4](#0-3) 

The package-level doc comment claims "this sync happens for every auth endpoint hit," but the actual per-request auth paths (`AuthorizedUserWithSession`, `FindUserByAPIToken`) only read cached local state and never trigger a resync: [5](#0-4) [6](#0-5) 

So if an admin is demoted or removed from `AdminUserGroupCN` upstream (the LDAP analog of updating `governanceThreshold`), the already-issued session cookie/API token in `ldap_sessions`/`ldap_user_api_tokens` continues to carry the old, higher-privileged `UserRole` until the next scheduled `Work()` execution — which, with the default config, never runs again after startup.

### Impact Explanation
A demoted/revoked LDAP user retains their previously cached elevated role (e.g. `UserRoleAdmin`) for the full remaining lifetime of their session (`SessionTimeout`) or API token (`UserAPITokenDuration`, default `240h`), since expiry is purely time-based and unrelated to the role-sync logic: [7](#0-6) 
This is a genuine authorization-state inconsistency analogous to the reported bug class: a privilege-affecting config/group change does not propagate to already-materialized credential state, and — with default config — never will without an operator restart, letting an already-authenticated but now-unauthorized user continue to exercise admin-level API endpoints (job/spec management, key management, etc.).

### Likelihood Explanation
Requires only a normal administrative action (removing/demoting a user from an LDAP group) combined with the affected user's existing valid session/API token, both of which are expected operational events, not an attacker-controlled trigger. Likelihood of the stale-state window occurring is high whenever `UpstreamSyncInterval` is left at its default value, since no periodic resync ever happens after node start.

### Recommendation
Re-validate the user's role against the upstream `upstreamUserStateMap` (or a short-TTL cache) on every `AuthorizedUserWithSession`/`FindUserByAPIToken` call rather than only via the optional periodic `Work()` job; alternatively, force `UpstreamSyncInterval` to a mandatory non-zero value at LDAP config validation time in `NewLDAPAuthenticator` so revocations are always eventually reflected, and document/emit a warning when the interval is `0s`.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with default `UpstreamSyncInterval = '0s'`.
2. User `alice` is a member of `AdminUserGroupCN`; she logs in, obtaining a session cached in `ldap_sessions` with `user_role = 'admin'`.
3. Operator removes `alice` from the admin LDAP group (revokes access) — no node restart occurs, so `LDAPServerStateSyncer.run()` was never started (`UpstreamSyncInterval` is `0s`).
4. `alice`'s existing session cookie continues to pass `AuthenticateBySession` → `AuthorizedUserWithSession`, which returns the stale cached `admin` role read straight from `ldap_sessions`, for up to `SessionTimeout`/session renewal, or up to `UserAPITokenDuration` (240h) if she holds an API token — despite no longer being an admin upstream.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L10-18)
```go
Note: user can have only one API token at a time, and token expiration is enforced

User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function

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

**File:** core/sessions/ldapauth/sync.go (L93-104)
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
```

**File:** docs/CONFIG.md (L679-682)
```markdown
UserApiTokenEnabled = false # Default
UserAPITokenDuration = '240h0m0s' # Default
UpstreamSyncInterval = '0s' # Default
UpstreamSyncRateLimit = '2m0s' # Default
```
