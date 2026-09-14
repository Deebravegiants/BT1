### Title
Compromised LDAP-authenticated user retains privileged role/session until the next periodic upstream sync — ([File: core/sessions/ldapauth/sync.go])

### Summary
The reported bug describes a compromised oracle address whose report is still counted toward quorum because on-chain state used to validate reports is not immediately invalidated when the oracle's role is revoked — the removal only takes effect for future checks, leaving a window where the compromised actor is still treated as authorized. The same *stale-authorization-window* class exists in chainlink's LDAP authentication provider: once a user is removed from (or downgraded in) the upstream LDAP admin/edit/run group, the locally cached session and API token role remain valid and continue to authorize requests until the next periodic `LDAPServerStateSyncer.Work` run actually purges/updates them.

### Finding Description
`AuthorizedUserWithSession` and `FindUserByAPIToken` in `core/sessions/ldapauth/ldap.go` authorize requests purely from locally cached `ldap_sessions` / `ldap_user_api_tokens` rows, without live-checking the upstream LDAP server on every request: [1](#0-0) [2](#0-1) 

The only mechanism that reconciles these cached role/membership entries with the authoritative upstream LDAP group membership is `LDAPServerStateSyncer.Work`, which runs on a configurable `UpstreamSyncInterval` timer (and is additionally throttled by `UpstreamSyncRateLimit`): [3](#0-2) [4](#0-3) 

The actual purge/role-downgrade of `ldap_sessions` and `ldap_user_api_tokens` for users removed from upstream groups only happens inside this deferred sync transaction: [5](#0-4) 

So if an admin (or the LDAP server operator) revokes a compromised user's group membership (e.g., demotes/removes them from the Admin group after key/credential leakage), that user's existing cached `ldap_sessions` row (and API token, if `UserApiTokenEnabled`) continues to authenticate them with their old, higher-privileged role — analogous to the malicious oracle whose report is still validated because it was submitted before the on-chain quorum removal took effect — until the next `Work()` execution actually reconciles state. This window can span the full `UpstreamSyncInterval` (and `UpstreamSyncRateLimit`), during which a compromised admin session/token can still create/edit jobs, manage users, rotate keys, or move funds.

### Impact Explanation
While the removal is genuinely revoked at the LDAP source of truth, the local chainlink node continues to trust the stale cached role for the full sync interval. If that interval is not very short (or the sync is rate-limited/misconfigured), a compromised credential retains admin/edit access for an extended window after the operator believed it was revoked — a direct authorization/role-bypass impact matching the "HIGH" classification of the reported analog (its effect is easier and continued unauthorized access using a "should already be revoked" credential).

### Likelihood Explanation
This requires: (1) LDAP auth provider enabled, (2) a user account credential compromise, and (3) the operator revoking the user upstream instead of also manually purging the local session/token. This is a realistic operational sequence — the whole point of upstream revocation is to have chainlink pick it up automatically — but the design only does so periodically rather than on next-request basis, which is exactly the "stale-record still valid" pattern from the report.

### Recommendation
On every authenticated request (or at minimum for session/token validation), consider live-checking (or shortening/removing the sync-interval gap for) whether the cached role/membership is still valid, or immediately invalidate/downgrade `ldap_sessions` and `ldap_user_api_tokens` entries as soon as a revocation is detected rather than waiting for the next scheduled `Work()` tick. This mirrors the report's recommendation to zero out cached quorum/report state immediately upon role revocation rather than let it remain valid until the next reconciliation pass.

### Proof of Concept
1. Enable LDAP auth with `UpstreamSyncInterval` set to a non-trivial duration (e.g., minutes).
2. User `alice@corp` is a member of the Admin LDAP group; she logs in, creating a row in `ldap_sessions` with `user_role = 'admin'` [6](#0-5) .
3. Alice's credentials leak. The operator removes her from the upstream Admin LDAP group immediately.
4. Before the next `LDAPServerStateSyncer.Work` tick fires, the attacker uses Alice's still-valid `ldap_sessions` cookie/session ID to call `AuthorizedUserWithSession`, which only checks the local cache and returns `user_role = 'admin'` [7](#0-6) , granting continued admin-level API access despite the upstream revocation having already occurred.

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L440-452)
```go
	session := sessions.NewSession()
	_, err = l.ds.ExecContext(
		ctx,
		"INSERT INTO ldap_sessions (id, user_email, user_role, localauth_user, created_at) VALUES ($1, $2, $3, $4, now())",
		session.ID,
		strings.ToLower(sr.Email),
		foundUser.Role,
		isLocalUser,
	)
	if err != nil {
		l.lggr.Errorf("unable to create new session in ldap_sessions table %v", err)
		return "", fmt.Errorf("error creating local LDAP session: %w", err)
	}
```

**File:** core/sessions/ldapauth/sync.go (L56-66)
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
