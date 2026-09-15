## Finding: LDAP session/API-token revocation relies solely on an out-of-band, disableable sync job — not on live re-validation

### Title
Stale/Revoked LDAP User Sessions and API Tokens Remain Valid Due to Missing Live Revocation Check - (File: core/sessions/ldapauth/ldap.go)

### Summary
This is the closest reachable analog to the Ethos `verifiedProfileIdForAddress` bug: an authorization-critical lookup function trusts a cached credential/role without checking whether the underlying identity has since been revoked ("compromised"/deactivated) at its source of truth. In chainlink, `ldapAuthenticator.AuthorizedUserWithSession` and `ldapAuthenticator.FindUserByAPIToken` grant access purely from cached rows in `ldap_sessions` / `ldap_user_api_tokens`, checking only expiry — never live LDAP membership/active status. Revocation is applied only by a separate, periodic `LDAPServerStateSyncer.Work` job, which can be entirely disabled by config.

### Finding Description
`AuthorizedUserWithSession` looks up the session purely from the local cache and only validates a time-based expiry window: [1](#0-0) 

Likewise, `FindUserByAPIToken` only checks the token's duration validity from the local cache table, with no check against the upstream LDAP active/group membership state: [2](#0-1) 

The only mechanism that revokes a user who has been removed from an LDAP group or marked inactive upstream is the separate `LDAPServerStateSyncer.Work` background job, which purges sessions/tokens for users no longer present in `upstreamUserStateMap`: [3](#0-2) 

That sync job is driven by `UpstreamSyncInterval`, and the ticker only runs `Work` on an interval: [4](#0-3) 

Critically, the documented default for this interval is `'0s'`, which explicitly **disables** the background sync entirely: [5](#0-4) 

This means with default configuration, once a user authenticates and a session/API token is cached in `ldap_sessions`/`ldap_user_api_tokens`, removing that user from their LDAP admin/edit/run/read group (the equivalent of marking a compromised identity as revoked) has **no effect** on their already-issued session cookie or API token — they remain fully authorized with their originally-cached role until the token/session naturally expires (`SessionTimeout` / `UserAPITokenDuration`, default up to 240h for tokens), because the authorization-path functions themselves never re-check upstream state.

### Impact Explanation
This mirrors the root cause of the Ethos M-1 finding: a security-critical authorization function (`verifiedProfileIdForAddress` there, `AuthorizedUserWithSession`/`FindUserByAPIToken` here) omits a live compromise/revocation check and instead trusts stale cached state. A node operator who revokes a user (e.g., after detecting a compromised/terminated employee credential) by removing them from the LDAP group has no way to immediately invalidate that user's existing session cookie or API token from the node's authentication layer itself — the operator must either wait for the (often disabled) sync interval or manually purge DB rows. During that window, the compromised/revoked identity retains full role-based access (up to Admin) to the Chainlink node's HTTP API, which can move funds, manage jobs, keys, and bridges.

### Likelihood Explanation
This is exploitable in the default configuration (`UpstreamSyncInterval = '0s'`) any time LDAP authentication is enabled and a previously-issued session or long-lived API token exists at the time of revocation — a realistic and common operational scenario (compromised credential response, offboarding). No special privilege is needed by the attacker beyond already holding the (now-revoked) session/token, which is exactly the "stolen credential" scenario described in the original report.

### Recommendation
- In `AuthorizedUserWithSession` and `FindUserByAPIToken`, do not rely solely on cached expiry; perform (or trigger) a check against the current LDAP active/group state before granting access, or at minimum ensure the revocation sync runs unconditionally at a safe minimum interval rather than being fully disable-able via `'0s'`.
- Provide an explicit "force logout/revoke" administrative action that synchronously purges a given user's `ldap_sessions`/`ldap_user_api_tokens` rows, independent of the periodic syncer.
- Warn/reject configuring `UpstreamSyncInterval = '0s'` when `AuthenticationMethod = 'ldap'` is in use, since it silently disables revocation propagation.

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'` and default `LDAP.UpstreamSyncInterval = '0s'`.
2. User logs in via `CreateSession`, receiving a valid session cookie; role is cached in `ldap_sessions`.
3. Administrator detects the credential is compromised and removes the user from all LDAP groups (revoking access upstream).
4. Because `UpstreamSyncInterval` is `0s`, `LDAPServerStateSyncer.Work` never runs to purge the stale `ldap_sessions` row.
5. The attacker continues to use the original session cookie; `AuthenticateBySession` → `AuthorizedUserWithSession` returns the cached (still-privileged) role, because it only checks `created_at + SessionTimeout >= now()`, never upstream membership — the attacker retains full access until the session naturally times out.

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

**File:** core/sessions/ldapauth/sync.go (L76-91)
```go
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
