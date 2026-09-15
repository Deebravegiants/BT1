Based on my investigation, this codebase already implements the mitigation that the Rancher advisory recommends adding — a dedicated background reaper (`LDAPServerStateSyncer`) that periodically re-validates cached LDAP session/API-token state against the upstream directory and purges/role-updates entries for users who are no longer present or active. However, there is a concrete gap in how that mitigation is wired up that reproduces the "stale externally-revoked identity remains usable" bug class.

### Title
Long-lived LDAP API tokens and sessions remain valid after upstream user revocation when `UpstreamSyncInterval` is left at its default disabled value - (File: core/sessions/ldapauth/sync.go)

### Summary
The LDAP authentication provider caches user sessions and API tokens locally (`ldap_sessions`, `ldap_user_api_tokens`) and relies entirely on `LDAPServerStateSyncer.Work` to re-check them against the upstream LDAP server and purge/revoke access for deactivated or removed users [1](#0-0) . Whether this reconciliation runs on any recurring basis is entirely controlled by the `UpstreamSyncInterval` config value, which defaults to `'0s'` [2](#0-1) .

### Finding Description
`LDAPServerStateSyncer.Start` only schedules a recurring background sync goroutine if `UpstreamSyncInterval` is non-zero; if it is zero (the default), `Work` is invoked exactly once, at node startup, and never again automatically: [3](#0-2) .

Per-request authentication paths do not perform any live upstream check either — `AuthorizedUserWithSession` and `FindUserByAPIToken` both trust the locally cached `ldap_sessions` / `ldap_user_api_tokens` rows and only validate a time-based expiry against `created_at + SessionTimeout` / `created_at + UserAPITokenDuration`, with no upstream re-validation call: [4](#0-3) [5](#0-4) .

The package-level documentation itself claims "This sync happens for every auth endpoint hit, and via the defined sync interval" [6](#0-5) , but no code path in `ldap.go`'s `AuthorizedUserWithSession` or `FindUserByAPIToken` actually triggers `LDAPServerStateSyncer.Work` — the comment describes intended behavior that is not implemented for the per-request path. The only wiring of the syncer service is in `application.go`, i.e., a single component started once at boot: [7](#0-6) .

Combined with `UserAPITokenDuration` defaulting to `240h0m0s` (10 days) [8](#0-7) , an LDAP API token issued to a user is treated as valid by `FindUserByAPIToken` for up to 10 days purely based on local timestamp, with no automatic re-check against the upstream directory unless an operator has explicitly configured a non-zero `UpstreamSyncInterval`.

### Impact Explanation
If a user is removed from the LDAP group or marked inactive in the identity provider, but `UpstreamSyncInterval` is left at its (default) disabled value, that user's previously-issued API token continues to authenticate successfully against `FindUserByAPIToken` for up to `UserAPITokenDuration` (10 days by default) since only a local timestamp check gates validity — exactly the "Rancher does not clean up a revoked/deleted AP user" bug class from the referenced advisory. This grants continued, unauthorized API access with the user's last-synced role (potentially Admin) to a party who should have lost access at the identity-provider level.

### Likelihood Explanation
This requires no attacker sophistication beyond possessing a previously valid, un-expired LDAP API token or session — which is realistic in any operator revoking access for an employee/contractor offboarding scenario. The likelihood of exposure hinges entirely on operator configuration: the vulnerability is latent whenever `UpstreamSyncInterval` is left at its documented default (`0s`), which disables the only mechanism (besides node restart) that revalidates cached identities against the authoritative LDAP source. This is a plausible default-configuration gap rather than a forced attacker action.

### Recommendation
- Trigger `LDAPServerStateSyncer.Work` synchronously (or via the sync-rate-limited path) from `AuthorizedUserWithSession` and `FindUserByAPIToken`, not only from the timer/startup, matching the documented behavior in `ldap.go`'s package comment.
- Consider making `UpstreamSyncInterval = 0` behave as "sync on every auth check" rather than "sync once at startup only," or emit a startup warning that user revocation propagation will require node restarts if left at `0s`.
- Reduce the default `UserAPITokenDuration` and/or clearly document the operational risk of leaving `UpstreamSyncInterval` disabled in the docs/config comments.

### Proof of Concept
1. Deploy chainlink node with `WebServer.LDAP` auth enabled, `UpstreamSyncInterval = '0s'` (default), `UserApiTokenEnabled = true`, `UserAPITokenDuration = '240h0m0s'` (default).
2. User `alice` logs in via LDAP, is issued an API token, which is stored in `ldap_user_api_tokens` with `created_at = now()`.
3. Administrator removes `alice` from the relevant LDAP group (revokes access) in the upstream directory.
4. Because `UpstreamSyncInterval` is `0s`, no further `Work()` sync runs after node startup; `alice`'s locally cached token row is never purged.
5. `alice` continues to call the Chainlink API using her API token; `FindUserByAPIToken` only checks `created_at + UserAPITokenDuration >= now()` against the local `ldap_user_api_tokens` table and returns her (last known) role successfully — for up to 10 days after revocation, with no restart or manual intervention.

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

**File:** core/sessions/ldapauth/sync.go (L93-116)
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
```

**File:** core/config/docs/core.toml (L266-267)
```text
# UserAPITokenDuration is the duration of time an API token is active for before expiring
UserAPITokenDuration = '240h0m0s' # Default
```

**File:** core/config/docs/core.toml (L268-269)
```text
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
```

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
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

**File:** core/services/chainlink/application.go (L1-1)
```go
package chainlink
```
