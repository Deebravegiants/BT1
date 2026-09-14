### Title
Deactivated/revoked LDAP users retain full API access via cached sessions and API tokens without re-checking `ActiveAttribute` - (File: core/sessions/ldapauth/ldap.go)

### Summary
The reported ZealousSwapFarms bug is a class of "two paths to the same privileged state, one enforces a security restriction, the other does not." The `withdraw` path enforces the locking-period check, while `emergencyWithdraw` grants the same fund-withdrawal outcome while skipping it. The same bug class exists in the chainlink LDAP authentication provider: `FindUser` (used on fresh login / session creation) enforces the upstream "active" check via `validateUsersActive`, but the two other paths that grant equivalent, continuing authenticated access — `AuthorizedUserWithSession` and `FindUserByAPIToken` — never call this check, so once a session or API token is cached, a since-deactivated/removed LDAP user keeps full node access until the next background sync interval fires (which is disabled by default).

### Finding Description
`FindUser` in `core/sessions/ldapauth/ldap.go` explicitly re-validates the "is active" LDAP attribute before returning a role for a directory user: [1](#0-0) 

This check is only exercised on the initial-login/`FindUser` code path (used by `CreateSession`/login flow). However, once a session is created, subsequent request authentication goes through `AuthorizedUserWithSession`, which reads the cached role straight from the local `ldap_sessions` table without any active-status check: [2](#0-1) 

Similarly, `FindUserByAPIToken` — used by `AuthenticateByToken` for every unprivileged API request — reads directly from `ldap_user_api_tokens` and only checks token expiration, never re-verifying the upstream "active" attribute: [3](#0-2) 

Both of these methods are wired into the web authentication middleware as equally-trusted entry points for granting `SessionUserKey` (the authenticated user/role used by every controller): [4](#0-3) 

The package doc for `ldapauth` itself acknowledges the intended remediation mechanism — a periodic sync — but that sync is optional and disabled by default: [5](#0-4) [6](#0-5) 

So exactly like `emergencyWithdraw` skipping the `lockingPeriod` check that `withdraw` enforces, `AuthorizedUserWithSession`/`FindUserByAPIToken` skip the "active" check that `FindUser` enforces, even though all three paths converge to grant the same privileged, continuing access to the node's API.

### Impact Explanation
An LDAP user who is deactivated, removed from all RBAC groups, or fully removed from the directory (e.g. an offboarded employee or a user whose access was revoked for a security incident) continues to have full role-based access to the Chainlink node API for as long as their session or API token remains valid (`SessionTimeout`, default `15m0s`, or `UserAPITokenDuration`, default `240h` — 10 days) unless the operator has explicitly configured a non-zero `UpstreamSyncInterval` (default `0s`, i.e. disabled). Because API tokens can be created with lifetimes up to 10 days by default and `UpstreamSyncInterval` is disabled out of the box, this is a meaningful window during which access that the identity provider has revoked remains fully honored by the node — an authentication/authorization bypass of the intended access-revocation control, directly analogous to the reported bypass of the intended locking-period control.

### Likelihood Explanation
This requires no attacker sophistication beyond already holding a previously-issued, still-unexpired session cookie or API token (a legitimate, unprivileged actor who has simply been deactivated upstream). Given `UpstreamSyncInterval = '0s'` is the shipped default (sync disabled), and `UserAPITokenDuration` defaults to 240h, this is trivially reachable in any deployment that hasn't explicitly hardened the LDAP sync configuration.

### Recommendation
Re-validate the upstream "active" attribute (or equivalently short-circuit via forced sync) inside `AuthorizedUserWithSession` and `FindUserByAPIToken`, not only in `FindUser`, so that revoked/deactivated users lose access immediately rather than only at the next scheduled sync. Alternatively, enforce a non-zero, bounded default for `UpstreamSyncInterval` and/or cap `SessionTimeout`/`UserAPITokenDuration` so the exposure window is small regardless of configuration.

### Proof of Concept
1. Configure LDAP auth with `ActiveAttribute` set and a user active in the directory.
2. User logs in normally; `FindUser` validates `ActiveAttribute` is true, session row is written to `ldap_sessions`, and/or an API token is issued and stored in `ldap_user_api_tokens`.
3. Administrator deactivates the user upstream (sets `ActiveAttribute` to inactive) or removes them from RBAC groups entirely, with `UpstreamSyncInterval` left at its default `0s` (disabled).
4. The user continues to call any Chainlink node API endpoint using the existing session cookie or API token.
5. `AuthenticateBySession`/`AuthenticateByToken` in `core/web/auth/auth.go` calls `AuthorizedUserWithSession`/`FindUserByAPIToken`, both of which return the cached role without checking `ActiveAttribute`, so the request succeeds with full privileges despite the user being deactivated upstream — bypassing the intended access-revocation restriction, analogous to bypassing the withdraw locking period via `emergencyWithdraw`.

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

**File:** core/config/docs/core.toml (L268-271)
```text
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
# UpstreamSyncRateLimit defines a duration to limit the number of query/API calls to the upstream LDAP provider. It prevents the sync functionality from being called multiple times within the defined duration
UpstreamSyncRateLimit = '2m0s' # Default
```
