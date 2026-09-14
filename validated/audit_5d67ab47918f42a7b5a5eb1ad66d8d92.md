## Finding [1](#0-0) 

### Title
Delayed revocation of LDAP-authenticated sessions and API tokens — local session/role state is only revalidated against the upstream LDAP server on a background sync interval, not on each request - (File: core/sessions/ldapauth/sync.go)

### Summary
Chainlink's LDAP authentication driver caches session and API-token role state in local Postgres tables (`ldap_sessions`, `ldap_user_api_tokens`) and only reconciles that cached state against the upstream LDAP directory via a separate background sync job, `LDAPServerStateSyncer.Work`, rather than at request time.

### Finding Description
The LDAP authenticator's package doc explicitly documents this design: "User session and roles are cached and revalidated with the upstream service at the interval defined in the local LDAP config through the `Application.sessionReaper` implementation in `reaper.go`... Changes to the upstream identity server will propagate through and update local tables... via the defined sync interval." [2](#0-1) 

Request-time authorization checks — `FindUserByAPIToken` for API tokens — validate purely against the locally cached row and its TTL, with no live upstream LDAP query: `SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_user_api_tokens WHERE token_key = $1`. [3](#0-2) 

The actual removal/downgrade of a user who is deleted from an LDAP group, deactivated, or has their group membership changed only happens inside `LDAPServerStateSyncer.Work`, which builds an `upstreamUserStateMap` from a live directory query and then deletes/updates rows in `ldap_sessions` / `ldap_user_api_tokens` that no longer match upstream state. [4](#0-3) [5](#0-4) 

Critically, this reconciliation is gated by two independently configurable timers, and its cadence depends entirely on operator config:
- `UpstreamSyncInterval`: if this is `0s` (the documented default), the periodic goroutine is never started at all — `Work` is invoked exactly once at node startup and never again. [6](#0-5) 
- `UpstreamSyncRateLimit`: even when the interval-based ticker is running, `Work` additionally short-circuits (skips the upstream re-query and DB reconciliation) until `nextSyncTime` has elapsed. [7](#0-6) 

This is structurally the same bug class as CVE-2022-2447: an administrator (or here, an LDAP directory operator) revokes/downgrades a user's access upstream, but the node continues to honor the locally-cached session and API-token role for a window of time controlled by a config knob that defaults to "never resync automatically."

### Impact Explanation
A user who is removed from all LDAP role groups, deactivated via the `ActiveAttribute` check, or has their role downgraded in the upstream directory retains their prior Chainlink node role/session (Admin/Edit/Run/Read) — and thus API access — until the next successful `LDAPServerStateSyncer.Work` run. With the documented default `UpstreamSyncInterval = '0s'`, no periodic resync ever runs after node startup, so revocation effectively never propagates automatically for the life of the running node process. Depending on the assigned role, this can allow a formerly-authorized (now revoked) actor to continue creating/reading jobs, bridges, or other privileged node operations.

### Likelihood Explanation
Exploitation requires no attacker action beyond already having obtained a valid session cookie or API token prior to revocation, and simply continuing to use it — the same "no special skill required" profile as the original CVE. The condition is directly reachable whenever an operator relies on the documented default config (`UpstreamSyncInterval = '0s'`) or sets a long `UpstreamSyncRateLimit`, both of which are supported, non-error configurations.

### Recommendation
Revalidate session/API-token role against the upstream LDAP server (or at minimum enforce a bounded, mandatory maximum resync interval regardless of `UpstreamSyncInterval`/`UpstreamSyncRateLimit` configuration) rather than relying solely on the locally cached `ldap_sessions`/`ldap_user_api_tokens` rows for authorization decisions. Consider treating `UpstreamSyncInterval = 0` as "use a safe minimum interval" rather than "never resync," and document/warn operators explicitly about the access-revocation lag implied by these settings.

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'` and leave `UpstreamSyncInterval` at its default `0s`. [6](#0-5) 
2. A user in the `EditUserGroupCN` LDAP group logs in, obtaining a session (stored in `ldap_sessions`) or generates an API token (stored in `ldap_user_api_tokens`).
3. The LDAP administrator removes the user from all role groups (or deactivates them) in the upstream directory.
4. Because `Work` only ran once at node startup and the periodic ticker was never started, the user's existing session/API token continues to pass `AuthorizedUserWithSession`/`FindUserByAPIToken` checks (validated purely by local TTL, not upstream membership), granting continued Edit-level API access indefinitely. [3](#0-2)

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

**File:** core/sessions/ldapauth/ldap.go (L204-230)
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

**File:** core/sessions/ldapauth/sync.go (L187-243)
```go
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
