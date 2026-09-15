## Title
Disabled/removed LDAP users retain valid sessions and API tokens because revocation depends on an optional, default-disabled periodic sync — ([File: core/sessions/ldapauth/ldap.go], [File: core/sessions/ldapauth/sync.go])

### Summary
When using the LDAP authentication provider, per-request session and API-token validation (`AuthorizedUserWithSession`, `FindUserByAPIToken`) only checks a local cache table (`ldap_sessions` / `ldap_user_api_tokens`) and never re-queries the upstream directory for the user's active/group-membership status. Revocation of these cached credentials only happens via a separate background sync job (`LDAPServerStateSyncer.Work`), and that job is **only scheduled on a timer if `UpstreamSyncInterval` is explicitly set to a non-zero value** — its documented default is `0s`, meaning it runs exactly once at node startup and never again. This mirrors CVE-2022-1155 in Snipe-IT: disabling/removing a user upstream does not revoke their already-issued sessions/tokens.

### Finding Description
`AuthorizedUserWithSession` for LDAP purely reads the local `ldap_sessions` cache row and checks only its stored expiry (`created_at + SessionTimeout`), performing no upstream check: [1](#0-0) 

Similarly, `FindUserByAPIToken` explicitly documents that "no further upstream LDAP query is performed" and only checks the local token's expiry against `UserAPITokenDuration` (default 240h): [2](#0-1) 

The only mechanism that removes sessions/tokens for users deactivated or removed from LDAP groups is `LDAPServerStateSyncer.Work`, which deletes `ldap_sessions`/`ldap_user_api_tokens` rows for emails no longer present in the upstream group membership state: [3](#0-2) 

But this sync is only run on an interval when `UpstreamSyncInterval` is non-zero; otherwise it runs a single time at `Start()` and is never invoked again for the life of the running node: [4](#0-3) 

The package-level doc comment for `ldapauth` claims "This sync happens for every auth endpoint hit, and via the defined sync interval," which is inaccurate for the hot auth path shown above — `AuthorizedUserWithSession` and `FindUserByAPIToken` do not trigger any upstream re-validation: [5](#0-4) 

The documented config default confirms `UpstreamSyncInterval` ships disabled: [6](#0-5) 

### Impact Explanation
An administrator disabling, deprovisioning, or removing a user's group membership in the upstream LDAP/AD directory (the standard "kill access" action) has no effect on that user's already-issued Chainlink node session cookie or API token unless the operator has separately configured a non-zero `UpstreamSyncInterval`. With the shipped default, revocation only happens on node restart. A disabled user (or an attacker holding their leaked session cookie/API token) can continue to authenticate and perform actions up to their role's privileges — up to the full `SessionTimeout`/`UserAPITokenDuration` (token default 240h) — well after the account was supposed to be cut off. This is a direct authentication/authorization control bypass (CWE-613: Insufficient Session Expiration) analogous to CVE-2022-1155.

### Likelihood Explanation
This requires no attacker sophistication beyond already possessing a valid session cookie or API token issued while the account was active (a routine occurrence: session hijack, leaked token, or a departing/terminated employee's own still-valid credentials). Because the default config leaves the sync disabled, this is the out-of-the-box behavior for any node operator who deploys LDAP auth without explicitly tuning `WebServer.LDAP.UpstreamSyncInterval`, making the likelihood of exposure high in real deployments.

### Recommendation
- Re-validate upstream active/group-membership status inline on `AuthorizedUserWithSession` and `FindUserByAPIToken` (at least at a bounded rate), not only via the optional background syncer.
- Change `UpstreamSyncInterval` to have a safe non-zero default, or make the startup-only behavior explicit and documented as insecure.
- Update the package documentation to accurately reflect that per-request upstream revalidation does not occur, avoiding operator overconfidence in the security guarantee.
- Consider actively purging cached sessions/tokens as soon as a `DELETE`d LDAP user is detected, rather than relying purely on interval-based reconciliation.

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'` and leave `UpstreamSyncInterval` at its default (`0s`).
2. A valid LDAP user logs in, creating a row in `ldap_sessions` (and/or issues an API token creating a row in `ldap_user_api_tokens`).
3. The LDAP administrator disables/removes the user from all the configured role groups upstream (equivalent to disabling the account).
4. Because `UpstreamSyncInterval` is `0s`, `LDAPServerStateSyncer.run()` never fires again (`core/sessions/ldapauth/sync.go` lines 60-67), so no purge of the stale `ldap_sessions`/`ldap_user_api_tokens` row occurs.
5. The disabled user's browser session cookie (or previously issued API token) continues to authenticate successfully via `AuthorizedUserWithSession`/`FindUserByAPIToken`, since these only check the local cached row's expiry, not upstream status — full API access continues until the cookie/token's natural expiry or node restart.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L10-17)
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

**File:** core/sessions/ldapauth/sync.go (L189-243)
```go
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

**File:** docs/CONFIG.md (L679-682)
```markdown
UserApiTokenEnabled = false # Default
UserAPITokenDuration = '240h0m0s' # Default
UpstreamSyncInterval = '0s' # Default
UpstreamSyncRateLimit = '2m0s' # Default
```
