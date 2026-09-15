Confirmed: `AuthenticateBySession` and `AuthenticateByToken` in `core/web/auth/auth.go` call directly into `AuthorizedUserWithSession`/`FindUserByAPIToken`, with no re-sync or `Work()` call on the per-request path, contradicting the ldap.go header comment's claim that "sync happens for every auth endpoint hit."

Audit Report

## Title
Deactivated LDAP user's cached session/API token remains fully authorized until sync cycle or natural expiry - ([File: core/sessions/ldapauth/ldap.go])

## Summary
`AuthorizedUserWithSession` and `FindUserByAPIToken` in the LDAP authenticator only check local cache expiry (`created_at + duration >= now()`) and never re-validate the upstream `ActiveAttribute`/group membership, while the only code path that does re-validate against upstream (`LDAPServerStateSyncer.Work`) runs solely on a startup-once basis when `UpstreamSyncInterval` is left at its documented default of `'0s'`. This allows a user deactivated in the upstream LDAP directory after establishing a session/token to retain full authenticated access for the remaining `SessionTimeout`/`UserAPITokenDuration` window.

## Finding Description
At login, `ldapAuthenticator.FindUser` checks the "is active" flag via `validateUsersActive` and rejects inactive users [1](#0-0) . However, the per-request hot paths do not repeat this check:
- `AuthorizedUserWithSession` only validates the cached `ldap_sessions` row's TTL against `now()`, returning the cached role without any upstream re-check [2](#0-1) .
- `FindUserByAPIToken` behaves identically for `ldap_user_api_tokens`, checking only TTL expiry [3](#0-2) .

Both are invoked directly by the gin middleware `AuthenticateBySession` and `AuthenticateByToken` in `core/web/auth/auth.go` on every authenticated request, with no intervening sync call [4](#0-3) .

The only mechanism that re-validates upstream active status and purges stale sessions/tokens is `LDAPServerStateSyncer.Work`, invoked either on a ticker (if `UpstreamSyncInterval` is non-zero) or exactly once at process `Start()` if the interval is zero — never per-request [5](#0-4) . This directly contradicts the package's own header documentation, which claims "This sync happens for every auth endpoint hit" [6](#0-5)  — that comment is inaccurate relative to the actual code path.

`UpstreamSyncInterval` defaults to `'0s'` in the documented config, which the doc comment states disables background interval sync, leaving only the one-time startup sync [7](#0-6) .

## Impact Explanation
This is a session/token revocation bypass: an account deactivated upstream (or removed from all RBAC groups) continues to have full authenticated access with its previously cached role (up to Admin) for up to `SessionTimeout` (web session) or `UserAPITokenDuration` (API token, default 240h/10 days), rather than being immediately locked out. This maps to the "node API authentication or role bypass" impact category, since the local/OIDC authenticators enforce revocation by deleting rows directly, while LDAP relies purely on cache TTL plus an unreliable/rarely-run background sync.

## Likelihood Explanation
Likelihood is high for any deployment using the documented default `UpstreamSyncInterval = '0s'`, since revocation validation then occurs only once at node startup. Any subsequent upstream deactivation of an already-sessioned/tokened user is invisible to the node until natural TTL expiry or a full node restart. This does not require attacker privilege escalation from zero — it is a legitimate, previously-authenticated-then-revoked user retaining unauthorized continued access, which is a realistic and repeatable scenario in production LDAP deployments (e.g., offboarding an employee).

## Recommendation
- Re-validate the cached user's upstream active/group status inline within `AuthorizedUserWithSession` and `FindUserByAPIToken` (with appropriate caching/rate limiting to bound LDAP load), rather than relying solely on TTL.
- Do not silently interpret `UpstreamSyncInterval = 0s` as "validate only once at startup forever" — require a bounded re-validation cadence or document this limitation prominently as a security-relevant operational requirement.
- Correct the misleading header comment in `ldap.go` claiming sync happens on every auth endpoint hit, since it does not match the implementation.

## Proof of Concept
1. Configure a node with LDAP auth, `ActiveAttribute` configured, and `UpstreamSyncInterval = '0s'` (the documented default).
2. Log in as a valid LDAP user to create a session (`FindUser` succeeds, row inserted into `ldap_sessions`), and/or call `SetAuthToken` to create an `ldap_user_api_tokens` row.
3. Without restarting the node, deactivate the user upstream (flip `ActiveAttribute` away from `ActiveAttributeAllowedValue`) or remove them from all RBAC groups.
4. Continue issuing authenticated requests using the existing session cookie/API token.
5. Observe `AuthenticateBySession`/`AuthenticateByToken` still succeed via `AuthorizedUserWithSession`/`FindUserByAPIToken`, returning the stale cached role, until `SessionTimeout`/`UserAPITokenDuration` naturally elapses or the node is restarted (triggering the one-time `Work()` sync).

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
```

**File:** core/sessions/ldapauth/ldap.go (L131-142)
```go
	// First query for user "is active" property if defined
	usersActive, err := l.validateUsersActive([]string{email})
	if err != nil {
		if errors.Is(err, ErrUserNotInUpstream) {
			return sessions.User{}, ErrUserNotInUpstream
		}
		l.lggr.Errorf("error in validateUsers call: %v", err)
		return sessions.User{}, errors.New("error running query to validate user active")
	}
	if !usersActive[0] {
		return sessions.User{}, errors.New("user not active")
	}
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

**File:** core/web/auth/auth.go (L55-112)
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

var _ authMethod = AuthenticateBySession

// AuthenticateByToken authenticates a User by their API token.
//
// Implements authMethod
func AuthenticateByToken(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	token := &auth.Token{
		AccessKey: c.GetHeader(APIKey),
		Secret:    c.GetHeader(APISecret),
	}
	if token.AccessKey == "" {
		return auth.ErrorAuthFailed
	}

	if token.Secret == "" {
		return auth.ErrorAuthFailed
	}

	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || errors.Is(err, clsessions.ErrUserSessionExpired) {
			return auth.ErrorAuthFailed
		}
		return err
	}

	ok, err := clsessions.AuthenticateUserByToken(token, &user)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	c.Set(SessionUserKey, &user)

	return nil
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

**File:** core/config/docs/core.toml (L268-269)
```text
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
```
