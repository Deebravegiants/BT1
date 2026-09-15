## Analog Found

### Title
Stale Cached RBAC Role in LDAP/OIDC Sessions Enables Privilege Retention After Upstream Demotion - (File: `core/sessions/ldapauth/ldap.go`)

### Summary
The Capgo CVE describes a demoted `super_admin`'s stale `org_users.user_right` value not being cleared on role-binding deletion, letting the user keep calling privileged RPCs. Chainlink's pluggable LDAP and OIDC `AuthenticationProvider` implementations have the same class of bug: once a user authenticates, their RBAC role is cached in a local table (`ldap_sessions` / `ldap_user_api_tokens` / `oidc_sessions`) and every subsequent authenticated request re-uses that cached role instead of re-checking the upstream identity provider, so a demotion at the identity provider does not take effect until the cached record is separately synced or expires.

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession`, which is invoked by the `auth.Authenticate` gin middleware on every authenticated HTTP/GraphQL request, resolves the user's role purely from the local `ldap_sessions` table, not from a live LDAP group lookup: [1](#0-0) 

The same caching pattern is used for API tokens: [2](#0-1) 

and for the OIDC driver's session lookup: [3](#0-2) 

The only mechanism that refreshes these cached roles against the upstream LDAP server is the background `LDAPServerStateSyncer.Work` job, gated by a ticker on `UpstreamSyncInterval`: [4](#0-3) 

`UpstreamSyncInterval` defaults to `'0s'`, which the docs state disables the background sync entirely: [5](#0-4) 

The package-level doc comment for `ldapauth` claims the sync "happens for every auth endpoint hit," but `AuthorizedUserWithSession` (the function actually called on every authenticated request through `auth.Authenticate`/`AuthenticateBySession`) contains no call into the syncer — it only performs a local SQL lookup of the cached `user_role` column: [6](#0-5) [7](#0-6) 

By contrast, the local-auth (`localauth`) driver correctly purges sessions and rewrites the role transactionally on every `UpdateRole` call, avoiding this class of bug: [8](#0-7) 

...but the LDAP/OIDC drivers rely on out-of-band syncing that is disabled by default and, for API tokens, only re-validates on expiry after `UserAPITokenDuration` (default 240h/10 days): [9](#0-8) 

Downstream, this stale cached role is what every RBAC gate (`RequiresAdminRole`, `RequiresEditRole`, `RequiresRunRole`, and the GraphQL equivalents) checks: [10](#0-9) [11](#0-10) 

### Impact Explanation
If an operator removes a user from the LDAP "Admin" group (or downgrades their OIDC claim) to revoke admin access, that user's existing session or API token retains the old cached `admin` role for the full session/token lifetime (or indefinitely if `UpstreamSyncInterval` stays at its default disabled value and the user never logs out). This directly maps to the Capgo bug class: a demoted privileged principal retains privileged RPC/API access — here, admin-only chainlink endpoints such as user management (`/v2/users`), key export/import, and external initiator management — because the authorization check trusts a stale cached role column instead of re-validating against the current source of truth.

### Likelihood Explanation
This requires no attacker sophistication beyond simply continuing to use a session/API token that was valid at time of admin grant; the vulnerable code path (`AuthorizedUserWithSession`) is hit on literally every authenticated request, and the mitigating sync job is off by default (`UpstreamSyncInterval = '0s'`). Any deployment using the LDAP or OIDC authentication driver with default sync settings is exposed as soon as an admin is demoted upstream but their local session/token isn't independently invalidated.

### Recommendation
Re-validate the user's role against the upstream provider (or at minimum force a sync) on every privileged request, or drastically shorten/force `UpstreamSyncInterval` to a mandatory non-zero value with role/session revalidation baked into `AuthorizedUserWithSession` and `FindUserByAPIToken`, similar to how `localauth.UpdateRole` immediately purges sessions on role change.

### Proof of Concept
1. Configure chainlink node with `AuthenticationMethod = "ldap"` and default `UpstreamSyncInterval = '0s'`.
2. User `alice` is a member of the LDAP Admin group; she logs in, creating a row in `ldap_sessions` with `user_role = 'admin'`.
3. Operator removes `alice` from the Admin LDAP group (demotion) without also revoking her existing chainlink session or triggering a sync.
4. `alice` continues to call `AuthorizedUserWithSession` via any admin-gated endpoint (e.g., `/v2/users`, `/v2/keys/eth/export/...`); `RequiresAdminRole` succeeds because the cached `ldap_sessions.user_role` is still `'admin'`, granting continued admin access until the session naturally expires.

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

**File:** core/sessions/ldapauth/sync.go (L76-117)
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

**File:** docs/CONFIG.md (L771-776)
```markdown
### UserAPITokenDuration
```toml
UserAPITokenDuration = '240h0m0s' # Default
```
UserAPITokenDuration is the duration of time an API token is active for before expiring

```

**File:** docs/CONFIG.md (L777-787)
```markdown
### UpstreamSyncInterval
```toml
UpstreamSyncInterval = '0s' # Default
```
UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server

### UpstreamSyncRateLimit
```toml
UpstreamSyncRateLimit = '2m0s' # Default
```
UpstreamSyncRateLimit defines a duration to limit the number of query/API calls to the upstream LDAP provider. It prevents the sync functionality from being called multiple times within the defined duration
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

**File:** core/web/auth/auth.go (L236-253)
```go
// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```

**File:** core/sessions/localauth/orm.go (L259-296)
```go
// UpdateRole overwrites role field of the user specified by email.
func (o *orm) UpdateRole(ctx context.Context, email, newRole string) (sessions.User, error) {
	var userToEdit sessions.User

	if newRole == "" {
		return userToEdit, pkgerrors.New("user role must be specified")
	}

	err := sqlutil.TransactDataSource(ctx, o.ds, nil, func(tx sqlutil.DataSource) error {
		// First, attempt to load specified user by email
		if err := tx.GetContext(ctx, &userToEdit, "SELECT * FROM users WHERE lower(email) = lower($1)", email); err != nil {
			return pkgerrors.New("no matching user for provided email")
		}

		// Patch validated role
		userRole, err := sessions.GetUserRole(newRole)
		if err != nil {
			return err
		}
		userToEdit.Role = userRole

		_, err = tx.ExecContext(ctx, "DELETE FROM sessions WHERE email = lower($1)", email)
		if err != nil {
			o.lggr.Errorw("Failed to purge user sessions for UpdateRole", "err", err)
			return pkgerrors.New("error updating API user")
		}

		sql := "UPDATE users SET role = $1, updated_at = now() WHERE lower(email) = lower($2) RETURNING *"
		if err := tx.GetContext(ctx, &userToEdit, sql, userToEdit.Role, email); err != nil {
			o.lggr.Errorw("Error updating API user", "err", err)
			return pkgerrors.New("error updating API user")
		}

		return nil
	})

	return userToEdit, err
}
```

**File:** core/web/resolver/auth.go (L45-55)
```go
// Authenticates the user from the session cookie and asserts has 'admin' role
func authenticateUserIsAdmin(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role != sessions.UserRoleAdmin {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}
```
