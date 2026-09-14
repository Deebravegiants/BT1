### Title
Stale cached role/session data allows revoked or demoted OIDC/LDAP users to retain elevated access - ([File: core/sessions/oidcauth/oidc.go])

### Summary
The OIDC and LDAP authentication providers cache a user's role and session validity in local tables (`oidc_sessions`, `oidc_user_api_tokens`, `ldap_sessions`, `ldap_user_api_tokens`) at the moment of login/token issuance. Subsequent authorization checks (`AuthorizedUserWithSession`, `FindUserByAPIToken`) validate solely against this local cache and a local expiry timer, without re-querying the upstream identity provider on each request. If a user's group membership/role is downgraded or revoked upstream, the locally cached session or API token continues to authorize the old (potentially higher-privileged) role until either the cache entry expires or an optional background sync task runs.

### Finding Description
`oidcAuthenticator.AuthorizedUserWithSession` reads the cached `user_role` straight out of the `oidc_sessions` table and only checks `created_at + SessionTimeout >= now()` for validity — it never re-validates against the upstream OIDC provider's current claims for that request: [1](#0-0) 

Likewise, `FindUserByAPIToken` returns the role cached in `oidc_user_api_tokens` at token-creation time, checked only against `UserAPITokenDuration` (default `240h0m0s`, i.e., 10 days): [2](#0-1) 

The equivalent LDAP implementation has the identical pattern — `AuthorizedUserWithSession` and `FindUserByAPIToken` both trust the locally cached `user_role`/token entry: [3](#0-2) 

Reconciliation with the upstream identity source is documented as happening only "for every auth endpoint hit, and via the defined sync interval," and that sync interval defaults to disabled (`UpstreamSyncInterval = '0s'`): [4](#0-3) [5](#0-4) 

This is structurally the same bug class as CVE-2014-5253: authorization state (Keystone's domain-scoped token; here, the cached role tied to a session/API token) is not actively revoked/re-validated when the source of truth (domain validity in Keystone; upstream group/role membership in LDAP/OIDC) changes, allowing continued use of stale, higher-privileged access.

By contrast, the local (non-SSO) authenticator does not have this problem — `AuthorizedUserWithSession` in `localauth/orm.go` re-reads the live `users` table on every call, so a role downgrade takes effect immediately: [6](#0-5) 

### Impact Explanation
An admin who demotes or removes a user's group membership at the upstream OIDC/LDAP identity provider does not immediately revoke that user's Chainlink node access. The user's existing browser session (valid for up to `SessionTimeout`, default 15m, but renewed on each authorized request since there is no absolute cap tied to the upstream state) or, more critically, their long-lived API token (valid up to `UserAPITokenDuration`, default 240h/10 days) continues to authenticate them with their old cached role. This is an authorization/role-revocation bypass reachable directly via standard API/session authentication for any user whose privileges were supposed to be reduced or removed — a legitimate node operator concern, not a malicious-peer or mocked-only scenario.

### Likelihood Explanation
This is triggered by a completely standard, expected admin action (revoking or downgrading a user's role in the external LDAP/OIDC directory) combined with the default configuration (`UpstreamSyncInterval = '0s'`, sync disabled). No attacker action beyond continuing to use an already-issued, previously-valid session cookie or API token is required, making exploitation trivial once the underlying condition (stale cache) exists.

### Recommendation
- Re-validate role/authorization state against the upstream provider (or at minimum re-check a shorter-lived, non-cached local record) on every authenticated request, not only at login/logout or on the optional sync interval.
- Provide an explicit, forced-revocation mechanism (e.g., admin-triggered "revoke all sessions/tokens for user") that immediately purges `oidc_sessions`/`oidc_user_api_tokens` and `ldap_sessions`/`ldap_user_api_tokens` rows independent of the sync interval.
- Consider defaulting `UpstreamSyncInterval` to a non-zero value and documenting the security implication of leaving it disabled.

### Proof of Concept
1. Configure the node with `AuthenticationMethod = 'oidc'` (or `'ldap'`) and leave `UpstreamSyncInterval = '0s'` (default).
2. User `alice` authenticates and is granted the `Admin` role via her OIDC group claim; `oidc_sessions` stores `user_role = 'admin'` for her session ID, and/or she creates a long-lived API token cached in `oidc_user_api_tokens`.
3. Node operator removes `alice` from the `NodeAdmins` group at the OIDC IdP.
4. `alice` continues to call authenticated node API endpoints using her existing session cookie or API token; `AuthorizedUserWithSession`/`FindUserByAPIToken` (core/sessions/oidcauth/oidc.go:349-391, 297-338) return the stale cached `admin` role without contacting the IdP, granting continued admin-level access for up to the session timeout or token duration (10 days by default for API tokens).

### Citations

**File:** core/sessions/oidcauth/oidc.go (L297-338)
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
}
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

**File:** docs/CONFIG.md (L777-782)
```markdown
### UpstreamSyncInterval
```toml
UpstreamSyncInterval = '0s' # Default
```
UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server

```

**File:** core/sessions/localauth/orm.go (L83-107)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired, and update session's LastUsed field.
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired, and update session's LastUsed field.
func (o *orm) AuthorizedUserWithSession(ctx context.Context, sessionID string) (user sessions.User, err error) {
	if len(sessionID) == 0 {
		return sessions.User{}, sessions.ErrEmptySessionID
	}

	email, err := o.findValidSession(ctx, sessionID)
	if err != nil {
		return sessions.User{}, sessions.ErrUserSessionExpired
	}

	user, err = o.findUser(ctx, email)
	if err != nil {
		return sessions.User{}, sessions.ErrUserSessionExpired
	}

	if err := o.updateSessionLastUsed(ctx, sessionID); err != nil {
		return sessions.User{}, err
	}

	return user, nil
}
```
