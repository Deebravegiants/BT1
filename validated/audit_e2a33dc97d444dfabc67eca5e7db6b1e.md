The verified code confirms the claim's technical description is accurate. `AuthenticateBySession` and `AuthenticateByToken` in `core/web/auth/auth.go` call `AuthorizedUserWithSession`/`FindUserByAPIToken` directly with no sync trigger inline, and `LDAPServerStateSyncer.Start` only runs `Work()` continuously if `UpstreamSyncInterval` is non-zero, otherwise it runs `Work()` exactly once at startup.Audit Report

## Title
LDAP-backed API tokens and sessions are not revalidated against the upstream identity provider, allowing disabled/deprovisioned users to retain access - ([File: core/sessions/ldapauth/ldap.go])

## Summary
`FindUserByAPIToken` and `AuthorizedUserWithSession` in `core/sessions/ldapauth/ldap.go` authorize requests purely from locally cached rows in `ldap_user_api_tokens`/`ldap_sessions`, without any live check against the upstream LDAP server's group membership or `ActiveAttribute` (disabled flag). Revalidation against upstream state is delegated entirely to `LDAPServerStateSyncer.Work`, which only runs on a recurring basis if `WebServer.LDAP.UpstreamSyncInterval` is configured non-zero; with the documented default of `'0s'`, `Start()` runs `Work()` exactly once at node boot and never again, so a user deprovisioned/deactivated/removed from groups upstream retains full node API access for the remaining life of their session or API token.

## Finding Description
`FindUserByAPIToken` queries only `ldap_user_api_tokens` by `token_key` and returns the cached `user_role`/email with no upstream contact: [1](#0-0) 

`AuthorizedUserWithSession`, invoked on every session-authenticated request via `AuthenticateBySession`, likewise only reads `ldap_sessions` and checks local expiry, again without any upstream query: [2](#0-1) 

Both are wired directly into the auth middleware with no interposed revalidation step: [3](#0-2) 

By contrast, `FindUser` (used only at initial login) does call `validateUsersActive` against LDAP before granting a role — this check simply is not repeated for subsequent session/token use. [4](#0-3) 

The only mechanism that re-checks upstream group membership/active-state is `LDAPServerStateSyncer.Work`, and its cadence is gated by `UpstreamSyncInterval`: if non-zero, it runs on a ticker; if zero (`IsInstant()` true, the documented default), `Start()` runs `Work()` a single time at startup and never schedules further syncs: [5](#0-4) 

The documented default confirms `UpstreamSyncInterval = '0s'`: [6](#0-5) 

The config comment's claim that "this check is already performed during login/logout actions" does not match the code — `AuthorizedUserWithSession`/`FindUserByAPIToken` (invoked per request, not just at login/logout) perform no such check; only initial `FindUser` at login does.

## Impact Explanation
With `WebServer.AuthenticationMethod = 'ldap'`, `UserApiTokenEnabled = true`, and `UpstreamSyncInterval` left at its shipped default of `'0s'`, a user who is deactivated, removed from all mapped LDAP groups, or deleted upstream continues to hold valid `chainlink` node-API access (admin/edit/run/read, depending on cached role) for the remaining lifetime of their session (`SessionTimeout`) or API token (`UserAPITokenDuration`, default 240h). This maps to an in-scope authorization-revocation-bypass on node API authentication — access that should have been revoked persists, potentially permitting job/spec management or key operations by a deprovisioned identity.

## Likelihood Explanation
Exploitation requires no attacker action beyond already holding a previously valid session/token; it relies on the shipped default configuration (`UpstreamSyncInterval = '0s'`) and on the operator having enabled LDAP auth (and API tokens for the token-based variant), both of which are documented supported configurations rather than obscure or explicitly-warned-against misconfigurations. Given the default value is unsafe out-of-the-box, likelihood of impact in real deployments that don't explicitly set a sync interval is realistic.

## Recommendation
- Change the default `UpstreamSyncInterval` to a safe non-zero value, or make `Start()` always schedule periodic sync (falling back to a minimum safe interval) rather than only syncing once when the interval is zero.
- Have `AuthorizedUserWithSession` and `FindUserByAPIToken` trigger or perform inline revalidation against upstream state when local cache staleness exceeds a safe threshold, instead of relying solely on the out-of-band reaper.
- Correct the misleading doc comment/config description claiming this check happens "during login/logout actions" for every request, and clearly document that a zero `UpstreamSyncInterval` disables continuous revocation enforcement.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'`, `WebServer.LDAP.UserApiTokenEnabled = true`, and leave `UpstreamSyncInterval` unset (defaults to `'0s'`).
2. Log in as an LDAP user mapped to the "Edit" group and issue an API token via `CreateAndSetAuthToken`, stored in `ldap_user_api_tokens`.
3. On the upstream LDAP server, remove the user from all groups or mark them inactive via the configured `ActiveAttribute`.
4. Because `UpstreamSyncInterval` is `0s`, `LDAPServerStateSyncer.Start` ran `Work()` only once at node boot (`core/sessions/ldapauth/sync.go:56-68`) and never purges the now-stale token/session.
5. Call any node API endpoint using the previously issued API token or session cookie; `AuthenticateByToken`/`AuthenticateBySession` → `FindUserByAPIToken`/`AuthorizedUserWithSession` return the cached role from the local table without contacting LDAP, granting continued access despite the upstream revocation.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L114-142)
```go
// FindUser will attempt to return an LDAP user with mapped role by email.
func (l *ldapAuthenticator) FindUser(ctx context.Context, email string) (sessions.User, error) {
	email = strings.ToLower(email)

	// First check for the supported local admin users table
	var foundLocalAdminUser sessions.User
	checkErr := l.ds.GetContext(ctx, &foundLocalAdminUser, "SELECT * FROM users WHERE lower(email) = lower($1)", email)
	if checkErr == nil {
		return foundLocalAdminUser, nil
	}
	// If error is not nil, there was either an issue or no local users found
	if !errors.Is(checkErr, sql.ErrNoRows) {
		// If the error is not that no local user was found, log and exit
		l.lggr.Errorf("error searching users table: %v", checkErr)
		return sessions.User{}, errors.New("error Finding user")
	}

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

**File:** core/web/auth/auth.go (L52-112)
```go
// AuthenticateBySession authenticates the request by the session cookie.
//
// Implements authMethod
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
