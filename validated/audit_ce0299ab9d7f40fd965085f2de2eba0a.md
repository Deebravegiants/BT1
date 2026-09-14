### Title
Stale cached role/session persists for revoked or downgraded LDAP/OIDC users until next background sync - ([File: core/sessions/ldapauth/sync.go])

### Summary
The SKALE report describes a validator that is administratively disabled but whose already-granted delegations remain valid and exploitable until they naturally expire (up to 12 months), because disabling only flips a `trustedValidators` flag without revoking the outstanding privileged state. The analogous pattern in this codebase is in the LDAP/OIDC authentication providers: when an upstream identity server revokes a user or downgrades their role/group membership, the locally cached `ldap_sessions` / `ldap_user_api_tokens` (and OIDC equivalents) rows keep granting the user their old, possibly higher, role until the next `UpstreamSyncInterval` tick fires and the reconciliation logic in `LDAPServerStateSyncer.Work` runs.

### Finding Description
LDAP-authenticated sessions and API tokens are validated purely against local cache tables, not against the upstream directory on every request: [1](#0-0) 
The comment on the package explicitly documents that role revalidation against the upstream server is deferred to a periodic reconciliation job: [2](#0-1) 

That reconciliation only executes on a timer (`UpstreamSyncInterval`) or once at startup — it is not triggered per-request: [3](#0-2) 

Crucially, the default value of `UpstreamSyncInterval` is `'0s'`, which the config docs describe as disabling the periodic background sync entirely: [4](#0-3) 

When the interval is `0s` ("IsInstant"), `Start` only calls `Work` once at node startup and never again on a recurring schedule: [5](#0-4) 

The actual role/session purge and role downgrade logic that removes revoked users and updates roles for existing sessions/tokens lives inside `Work`'s transaction: [6](#0-5) 

Until that job runs, an already-issued session cookie or API token for a user whose upstream LDAP group membership has been revoked (removed from `AdminUserGroupCN`, marked inactive, etc.) continues to authenticate successfully with the stale cached role, because `AuthorizedUserWithSession`/`FindUserByAPIToken` only check local table freshness (`created_at`/expiry), not upstream validity: [7](#0-6) [8](#0-7) 

The OIDC driver has the identical architecture and identical default-disabled interval mechanism.

### Impact Explanation
If an operator relies on the default configuration (`UpstreamSyncInterval = '0s'`, i.e., disabled recurring sync) or sets a long interval, a user whose access is revoked upstream (e.g., removed from the `NodeAdmins` LDAP/OIDC group, terminated employee, compromised account disabled by IT) retains their previously cached Admin/Edit/Run role for the full remaining lifetime of their session cookie (`SessionTimeout`, default 15m — bounded) or, more critically, their API token (`UserAPITokenDuration`, default 240h = 10 days) after revocation. This is a "disabled principal still has active privileges" class of bug directly analogous to the SKALE finding, and can lead to unauthorized administrative actions (job creation/deletion, key management, fund transfer endpoints) by an actor who should have already lost access.

### Likelihood Explanation
This requires the LDAP/OIDC authentication method to be enabled (not the default `local` auth) and an admin to have not configured a short `UpstreamSyncInterval`. Given the documented default of `0s` (sync disabled unless explicitly configured), this is a plausible real-world misconfiguration rather than a contrived edge case, and the risk window (up to 10 days for API tokens) is significant.

### Recommendation
- Revalidate the user's role/active status against the upstream LDAP/OIDC source (or at least re-check the local `ldap_sessions`/`ldap_user_api_tokens` freshness against a mandatory minimum sync cadence) on every authenticated request, not only via the optional periodic job.
- Consider disallowing `UpstreamSyncInterval = 0` from fully disabling revalidation, or cap the maximum token/session lifetime tightly when sync is disabled.
- Shorten default `UserAPITokenDuration` for LDAP/OIDC-backed tokens, or force re-validation on token use similar to session `last_used` tracking in `localauth`.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `UpstreamSyncInterval = '0s'` (default).
2. User `alice@corp.com` is a member of the `NodeAdmins` LDAP group; she logs in and receives a session, and creates a long-lived API token (`UserAPITokenEnabled = true`, default duration 240h).
3. Administrator removes `alice` from the `NodeAdmins` group upstream (revoking access) because she left the company or was compromised.
4. Because `UpstreamSyncInterval` is `0s`, `LDAPServerStateSyncer.run()` never fires again (see `Start`), so `ldap_user_api_tokens` is never re-synced.
5. `alice`'s existing API token continues to authenticate with the `admin` role via `FindUserByAPIToken`/`AuthorizedUserWithSession`, which only check local table freshness — not upstream membership — for up to 10 more days.

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

**File:** core/sessions/ldapauth/ldap.go (L592-620)
```go
}

// DeleteAuthToken clears and disables the users Authentication Token.
func (l *ldapAuthenticator) DeleteAuthToken(ctx context.Context, user *sessions.User) error {
	_, err := l.ds.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE user_email = $1", user.Email)
	return err
}

// SaveWebAuthn is not supported for read only LDAP
func (l *ldapAuthenticator) SaveWebAuthn(ctx context.Context, token *sessions.WebAuthn) error {
	return sessions.ErrNotSupported
}

// Sessions returns all sessions limited by the parameters.
func (l *ldapAuthenticator) Sessions(ctx context.Context, offset, limit int) ([]sessions.Session, error) {
	var sessions []sessions.Session
	sql := `SELECT * FROM ldap_sessions ORDER BY created_at, id LIMIT $1 OFFSET $2;`
	if err := l.ds.SelectContext(ctx, &sessions, sql, limit, offset); err != nil {
		return sessions, nil
	}
	return sessions, nil
}

// FindExternalInitiator supports the 'Run' role external initiator header auth functionality
func (l *ldapAuthenticator) FindExternalInitiator(ctx context.Context, eia *auth.Token) (*bridges.ExternalInitiator, error) {
	exi := &bridges.ExternalInitiator{}
	err := l.ds.GetContext(ctx, exi, `SELECT * FROM external_initiators WHERE access_key = $1`, eia.AccessKey)
	return exi, err
}
```

**File:** core/sessions/ldapauth/sync.go (L56-91)
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

func (l *LDAPServerStateSyncer) Close() error {
	close(l.stopCh)
	<-l.done
	return nil
}

func (l *LDAPServerStateSyncer) run() {
	defer close(l.done)
	ctx, cancel := l.stopCh.NewCtx()
	defer cancel()
	ticker := time.NewTicker(l.config.UpstreamSyncInterval().Duration())
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			l.Work(ctx)
		}
	}
}
```

**File:** core/sessions/ldapauth/sync.go (L214-275)
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

**File:** core/config/docs/core.toml (L264-271)
```text
# UserApiTokenEnabled enables the users to issue API tokens with the same access of their role
UserApiTokenEnabled = false # Default
# UserAPITokenDuration is the duration of time an API token is active for before expiring
UserAPITokenDuration = '240h0m0s' # Default
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
# UpstreamSyncRateLimit defines a duration to limit the number of query/API calls to the upstream LDAP provider. It prevents the sync functionality from being called multiple times within the defined duration
UpstreamSyncRateLimit = '2m0s' # Default
```

**File:** core/sessions/oidcauth/oidc.go (L297-337)
```go
// FindUserByAPIToken retrieves a possible stored user and role from the oidc_user_api_tokens table store
func (oi *oidcAuthenticator) FindUserByAPIToken(ctx context.Context, apiToken string) (clsessions.User, error) {
	if !oi.config.UserAPITokenEnabled() {
		return clsessions.User{}, errors.New("API token is not enabled")
	}

	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc user API token table for given token, user role and email are cached so
		// no further upstream OIDC query is performed, sessions and tokens are synced against the upstream server
		// via the UpstreamSyncInterval config and reaper.go sync implementation
		var foundUserToken struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundUserToken,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_user_api_tokens WHERE token_key = $1",
			apiToken, oi.config.UserAPITokenDuration().Duration(),
		); err != nil {
			return err
		}
		if !foundUserToken.Valid {
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundUserToken.UserEmail,
			Role:  foundUserToken.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			// API Token expired, purge
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_user_api_tokens WHERE token_key = $1", apiToken); execErr != nil {
				oi.lggr.Errorf("error purging stale oidc API token session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
```

**File:** core/sessions/oidcauth/oidc.go (L349-391)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired
func (oi *oidcAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (clsessions.User, error) {
	if len(sessionID) == 0 {
		return clsessions.User{}, errors.New("session ID cannot be empty")
	}
	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc_sessions table for given session ID, user role and email are saved after the id claims is provided and validated
		var foundSession struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundSession,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_sessions WHERE id = $1",
			sessionID, oi.config.SessionTimeout().Duration(),
		); err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				return clsessions.ErrUserSessionExpired
			}
			return err
		}
		if !foundSession.Valid {
			// Sessions expired, purge
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundSession.UserEmail,
			Role:  foundSession.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE id = $1", sessionID); execErr != nil {
				oi.lggr.Errorf("error purging stale OIDC session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
}
```
