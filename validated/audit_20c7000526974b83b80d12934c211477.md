### Title
Stale cached LDAP/OIDC role in sessions and API tokens allows continued elevated access after upstream role revocation - ([File: core/sessions/ldapauth/ldap.go], [File: core/sessions/ldapauth/sync.go])

### Summary
The chainlink node's LDAP authentication provider caches a user's `role` in the local `ldap_sessions` and `ldap_user_api_tokens` tables at login/token-creation time. Every subsequent authorization decision (`AuthorizedUserWithSession`, `FindUserByAPIToken`) reads only this cached role from the local DB and never re-verifies against the upstream LDAP directory. Propagation of role changes (e.g. an admin revoking a user from the `NodeAdmins` group) is delegated entirely to a separate, independently-configured background sync job (`LDAPServerStateSyncer.Work`), analogous to how `BondingERC20TokenFactory.updateBondingCurve` updates the curve implementation but the hardcoded `getOutputPrice` function in `ContinuosBondingERC20Token` is never updated to match — one code path is "updated" while another path that performs the actual authorization decision keeps using stale state.

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession` explicitly loads the role from the cached `ldap_sessions` row and documents that "no further upstream LDAP query is performed": [1](#0-0) 

Similarly, `FindUserByAPIToken` reads the cached role from `ldap_user_api_tokens` with the same caveat that "sessions and tokens are synced against the upstream server via the UpstreamSyncInterval config": [2](#0-1) 

The only mechanism that reconciles these cached roles with the authoritative upstream LDAP group membership is `LDAPServerStateSyncer.Work`, which re-queries LDAP group members and issues a bulk `UPDATE ldap_sessions ... SET user_role = CASE ...` / `UPDATE ldap_user_api_tokens ...`: [3](#0-2) 

This sync only runs on a background timer if `UpstreamSyncInterval` is non-zero; if it is `'0s'` (the documented default), the periodic goroutine is never started — sync happens only once at node startup (`Start` calls `l.Work(ctx)` a single time and returns): [4](#0-3) 

The config default is explicit: [5](#0-4) 

Because `AuthenticateBySession`/`AuthenticateByToken` in the web auth middleware use the `Authenticator` interface directly against this cached-role lookup (with no live LDAP verification per request), a user whose access is revoked upstream (removed from `NodeAdmins`/`NodeEditors`/etc. group, or deactivated) retains their previously cached elevated role for the remaining lifetime of their existing session or API token: [6](#0-5) 

### Impact Explanation
With the documented default configuration (`UpstreamSyncInterval = '0s'`), a revoked or demoted user's existing session remains valid with the old (higher) role for up to `SessionTimeout` (default 15 minutes) for cookie sessions, and for up to `UserAPITokenDuration` (default 240h / 10 days) for API tokens, since the only reconciliation path for those long-lived tokens is the disabled background syncer. An operator revoking an admin's LDAP group membership in response to an offboarding or compromise event would reasonably expect that action to immediately deny future privileged node-API access, but the node continues to honor the stale cached role until the credential naturally expires or is manually purged.

### Likelihood Explanation
Likelihood is Medium: it requires the operator to be running with `AuthenticationMethod = 'ldap'` and to have left `UpstreamSyncInterval` at its documented default of `'0s'` (which disables periodic reconciliation), a configuration state that is explicitly the shipped default rather than an edge case. No attacker action is required beyond already holding a previously-valid session cookie or API token; the vulnerable condition is triggered purely by normal admin operations (revoking access) failing to take effect promptly.

### Recommendation
Perform role/authorization verification against the authoritative source (or at minimum enforce a mandatory bound on cache staleness) on every authenticated request rather than relying solely on a possibly-disabled background sync:
- Do not allow `UpstreamSyncInterval = '0s'` to fully disable reconciliation for the lifetime of long-duration credentials (particularly API tokens with `UserAPITokenDuration` up to 240h); either enforce a maximum staleness independent of this setting, or re-validate role membership at a bounded interval regardless of config.
- Alternatively, document and warn loudly that `UpstreamSyncInterval = '0s'` means revoked/demoted upstream users keep their last known role for up to `SessionTimeout`/`UserAPITokenDuration`, and consider making immediate re-validation the default behavior for privileged (Admin) roles.

### Proof of Concept
1. Configure the node with `AuthenticationMethod = 'ldap'` and leave `UpstreamSyncInterval = '0s'` (default).
2. User `alice@example.com` is a member of the LDAP `NodeAdmins` group; she logs in and receives a session cookie / API token, with role `Admin` cached in `ldap_sessions` / `ldap_user_api_tokens` via `CreateSession` (`core/sessions/ldapauth/ldap.go`).
3. The LDAP administrator removes `alice` from the `NodeAdmins` group upstream (e.g., due to termination).
4. Because `UpstreamSyncInterval` is `0s`, `LDAPServerStateSyncer.run()`'s background goroutine was never started (`Start` only invoked `Work` once at node boot), so no reconciliation occurs.
5. `alice`'s existing session/API token continues to pass `AuthorizedUserWithSession`/`FindUserByAPIToken`, both of which return the stale cached `Admin` role directly from the DB with no upstream check, granting her continued admin-level API access until her session/token naturally expires.

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

**File:** core/sessions/ldapauth/sync.go (L245-275)
```go
		// For each user session row, update role to match state of user map from upstream source
		var queryWhenClause strings.Builder
		emailValues := []any{}
		// Prepare CASE WHEN query statement with parameterized argument $n placeholders and matching role based on index
		for email, user := range upstreamUserStateMap {
			// Only build on SET CASE statement per local session and API token role, not for each upstream user value
			_, sessionOk := existingSessionsMap[email]
			_, tokenOk := existingAPITokensMap[email]
			if !sessionOk && !tokenOk {
				continue
			}
			emailValues = append(emailValues, email)
			fmt.Fprintf(&queryWhenClause, "WHEN user_email = $%d THEN '%s' ", len(emailValues), user.Role)
		}

		// If there are remaining user entries to update
		if len(emailValues) != 0 {
			// Set new role state for all rows in single Exec
			query := fmt.Sprintf("UPDATE ldap_sessions SET user_role = CASE %s ELSE user_role END", &queryWhenClause)
			_, err = tx.ExecContext(ctx, query, emailValues...)
			if err != nil {
				return err
			}

			// Update role of API tokens as well
			query = fmt.Sprintf("UPDATE ldap_user_api_tokens SET user_role = CASE %s ELSE user_role END", &queryWhenClause)
			_, err = tx.ExecContext(ctx, query, emailValues...)
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
