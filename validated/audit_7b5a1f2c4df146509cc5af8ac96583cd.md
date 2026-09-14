### Title
Deactivated LDAP User Retains Full Node Access Until Background Sync Runs (Default Disabled) - ([File: core/sessions/ldapauth/ldap.go])

### Summary
When Chainlink is configured with `WebServer.AuthenticationMethod = 'ldap'`, per-request session validation in `AuthorizedUserWithSession` only checks a locally cached `ldap_sessions` row and its expiry timestamp — it never re-queries the upstream LDAP directory for the user's `active`/organizational status on that request. Revocation of a deactivated user is delegated entirely to a separate background job (`LDAPServerStateSyncer.Work`) that is disabled by default (`UpstreamSyncInterval = '0s'`), so a deactivated user's existing session (and API token) keeps working exactly like the reported CI4MS `active=0` bypass.

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession` (used by both cookie-session auth and GraphQL auth) validates a session purely from the local `ldap_sessions` table: [1](#0-0) 

It checks `created_at + SessionTimeout >= now()`, but performs no upstream call to `validateUsersActive` and no re-check of group membership. The only code path that re-validates a user's active/group status against the LDAP server is `LDAPServerStateSyncer.Work`, and it is gated behind `UpstreamSyncInterval`: [2](#0-1) 

The documented default for `UpstreamSyncInterval` is `'0s'`, which the code treats as "instant"/disabled recurring sync — the sync only runs once at node `Start()`: [3](#0-2) 

This means once a session (or `ldap_user_api_tokens` entry, purged the same way in `Work`) is created, the only enforcement points for `active` status are `FindUser`/`CreateSession`/`ListUsers` (i.e., login time and admin listing), never per-request session authorization: [4](#0-3) 

The middleware that gates the entire authenticated API surface and GraphQL calls this same function without any additional active check: [5](#0-4) [6](#0-5) 

The comment in the package doc overstates the guarantee ("This sync happens for every auth endpoint hit"), but the code shows sync is only interval- or startup-driven, not tied to individual auth requests.

### Impact Explanation
An operator who deactivates a user in the upstream LDAP directory (or removes them from all role groups) expects that user to immediately lose access to the Chainlink node's admin/API surface (job management, key/secret operations, bridge configuration, fund-moving admin actions, etc., depending on role). With the default config, that user retains full authenticated access (their existing role) for the remaining life of their session — bounded by `SessionTimeout` (default `15m`, up to `240h` for API tokens via `UserAPITokenDuration`) — because deactivation is never checked in `AuthorizedUserWithSession`. This is a session-based privilege/access-revocation bypass analogous to the CI4MS `active=0` bug (unrevoked backend access for a deactivated identity).

### Likelihood Explanation
This requires the node to be configured with LDAP authentication (`WebServer.AuthenticationMethod = 'ldap'`) and does not require any special exploit technique — it is triggered purely by the default configuration (`UpstreamSyncInterval = '0s'`), which is the documented default. Any environment relying on LDAP for access control and expecting real-time deactivation enforcement is affected without any additional attacker action beyond continuing to use an already-issued session/API token.

### Recommendation
- Re-validate the user's `active` status (and/or current group membership) against LDAP (or a short-TTL cache) inside `AuthorizedUserWithSession`, not only during `FindUser`/`CreateSession`.
- Do not treat `UpstreamSyncInterval = 0` as "disable periodic revocation checks"; instead default to a safe non-zero interval, or force a lightweight active-check on every `AuthorizedUserWithSession` call regardless of the configured sync interval.
- Update the `ldapauth` package documentation to accurately reflect that sync/revocation is not tied to "every auth endpoint hit" unless this is actually implemented.

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'` and default `UpstreamSyncInterval = '0s'`.
2. User logs in successfully; `CreateSession` inserts a row into `ldap_sessions` with role and `created_at` [7](#0-6) .
3. Admin deactivates the user in the LDAP directory (sets inactive attribute / removes from all role groups).
4. Because `UpstreamSyncInterval` is `0s`, `LDAPServerStateSyncer.run()` never fires again after startup, so `ldap_sessions` is never purged for this user [2](#0-1) .
5. The deactivated user continues issuing authenticated requests; `AuthenticateBySession`/`AuthenticateGQL` call `AuthorizedUserWithSession`, which only checks local expiry and returns the (still cached) role, granting continued access until `SessionTimeout` elapses [8](#0-7) .

### Citations

**File:** core/sessions/ldapauth/ldap.go (L130-142)
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

**File:** core/sessions/ldapauth/ldap.go (L437-452)
```go
	// Save session, user, and role to database. Given a session ID for future queries, the LDAP server will not be queried
	// Sessions are set to expire after the duration + creation date elapsed, and are synced on an interval against the upstream
	// LDAP server
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

**File:** core/config/docs/core.toml (L268-269)
```text
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
UpstreamSyncInterval = '0s' # Default
```

**File:** core/web/auth/auth.go (L52-71)
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
```

**File:** core/web/auth/gql.go (L25-47)
```go
func AuthenticateGQL(authenticator Authenticator, lggr logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := c.Request.Context()
		session := sessions.Default(c)
		sessionID, ok := session.Get(SessionIDKey).(string)
		if !ok {
			return
		}

		user, err := authenticator.AuthorizedUserWithSession(ctx, sessionID)
		if err != nil {
			if errors.Is(err, clsessions.ErrUserSessionExpired) {
				lggr.Warnw("Failed to authenticate session", "err", err)
			} else {
				lggr.Errorw("Failed call to AuthorizedUserWithSession, unable to get user", "err", err)
			}
			return
		}

		ctx = WithGQLAuthenticatedSession(c.Request.Context(), user, sessionID)

		c.Request = c.Request.WithContext(ctx)
	}
```
