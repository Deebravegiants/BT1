Confirmed: `AuthenticateBySession` middleware (`core/web/auth/auth.go:55-71`) calls `AuthorizedUserWithSession` on *every* request, but for the LDAP provider that function only reads the cached role from the local `ldap_sessions` table — it never re-queries LDAP. Re-sync with the upstream directory only happens via `LDAPServerStateSyncer`, which (per `core/sessions/ldapauth/sync.go:56-67`) with the documented default `UpstreamSyncInterval = '0s'` runs `Work(ctx)` exactly **once**, at node startup, and never again.

### Title
Stale LDAP-cached role/session survives permission revocation - ([File: core/sessions/ldapauth/ldap.go])

### Summary
When `WebServer.AuthenticationMethod = 'ldap'`, each authenticated request is authorized via `AuthorizedUserWithSession`, which reads the user's role solely from the locally cached `ldap_sessions` table row, not from the upstream LDAP server. Revalidation against upstream only happens through `LDAPServerStateSyncer`, and with the documented default config (`UpstreamSyncInterval = '0s'`), that sync runs a single time at process startup and is never repeated. Consequently, once a user is authenticated, their cached role and session validity are never re-checked against the upstream directory for the remainder of the node's uptime.

### Finding Description
`AuthenticateBySession` (`core/web/auth/auth.go:55-71`) is invoked as web-server authentication middleware and calls `Authenticator.AuthorizedUserWithSession(ctx, sessionID)` on every incoming request. For the LDAP authenticator, this resolves to: [1](#0-0) 
which performs `SELECT user_email, user_role, ... FROM ldap_sessions WHERE id = $1` and returns the row's cached `user_role` — it never contacts the LDAP server to verify the user is still active or still holds that role.

Cache invalidation is delegated entirely to `LDAPServerStateSyncer.Work()` (`core/sessions/ldapauth/sync.go:93-284`), which re-queries LDAP group membership and issues `UPDATE ldap_sessions SET user_role = ...` / deletes purged users. However `Start()` only schedules this on a recurring ticker if `UpstreamSyncInterval` is non-zero: [2](#0-1) 
With the shipped default (`UpstreamSyncInterval = '0s'`, documented at `core/config/docs/core.toml:268-269` and `docs/CONFIG.md:777-781`), `Work(ctx)` fires only once at startup (`l.Work(ctx)` in the `else` branch) — there is no periodic re-check thereafter.

This mirrors the CVE-2021-34434 bug class: a durable/offline entity's grants (here, an LDAP-backed user session/API token) continue to be honored by the system after the source of truth (the directory/group membership) revokes them, because the local cache is not refreshed on the enforcement path.

### Impact Explanation
If an operator demotes or removes a user from an LDAP admin/edit group (or deactivates the account) while that user holds an active browser session or `ldap_user_api_tokens` API token, the Chainlink node continues to authorize that user at their old (potentially Admin) role indefinitely — until the node process is restarted or an operator explicitly configures a non-zero `UpstreamSyncInterval`. This is a role-privilege-persistence bug: the node's runtime authorization state diverges from the intended access-control source of truth, allowing continued admin/edit actions (bridge management, job runs, key management, etc.) by a de-provisioned user with an unprivileged path (simply keep reusing the existing session cookie/API token).

### Likelihood Explanation
Requires `WebServer.AuthenticationMethod = 'ldap'` to be configured, and requires an admin to actually revoke or downgrade a user while that user has a live session/token — a realistic offboarding scenario. Given the documented default value of `UpstreamSyncInterval` is `'0s'`, this is the out-of-the-box behavior unless an operator proactively overrides it, making the exposure window unbounded by default.

### Recommendation
Re-validate the cached role/active-status against the upstream directory (or at minimum enforce a bounded default sync interval instead of `0s`) on every `AuthorizedUserWithSession` call, or clearly document/enforce that operators must set a short `UpstreamSyncInterval` for revocation to take effect in a timely manner. Consider also invalidating sessions immediately on demand (e.g., an admin-triggered "force resync" action) rather than relying purely on a background ticker.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `WebServer.LDAP.UpstreamSyncInterval` left at default `'0s'`.
2. User `alice` is a member of the LDAP `NodeAdmins` group; she logs in via `/sessions`, creating an `ldap_sessions` row with `user_role = 'admin'`.
3. Node operator removes `alice` from `NodeAdmins` in the upstream LDAP directory (or disables her account) — no chainlink node restart occurs.
4. `alice` continues issuing authenticated requests using her existing session cookie; `AuthenticateBySession` → `AuthorizedUserWithSession` returns the stale `admin` role from `ldap_sessions`, and `RequiresAdminRole` (`core/web/auth/auth.go:237-253`) grants her admin actions.
5. Access persists until the Chainlink node process restarts (triggering the one-time startup `Work()` call) or an operator sets a non-zero `UpstreamSyncInterval`.

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

**File:** core/sessions/ldapauth/sync.go (L56-67)
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
```
