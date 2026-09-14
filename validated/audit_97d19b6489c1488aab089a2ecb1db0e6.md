Confirmed: `AuthenticateBySession`, `AuthenticateGQL`, `AuthenticateByAPIToken` (via `FindUserByAPIToken`) all call directly into the authenticator's DB-cached lookup on every request, with no upstream re-validation triggered per-request — contradicting the package-level docstring's claim that "this sync happens for every auth endpoint hit." [1](#0-0) [2](#0-1) 

### Title
Stale Role Enforcement in LDAP/OIDC Session and API-Token Cache Between Upstream Sync Intervals - (File: `core/sessions/ldapauth/ldap.go`, `core/sessions/ldapauth/sync.go`)

### Summary
When the pluggable `ldap` or `oidc` `AuthenticationProvider` is configured, a user's role is cached locally in the `ldap_sessions` / `ldap_user_api_tokens` (or `oidc_sessions`) tables at login/token-creation time. Every subsequent authenticated request — whether via cookie session (`AuthenticateBySession`, `AuthenticateGQL`) or API token — is authorized purely against this locally cached role, without contacting the upstream directory. The cache is only refreshed by a background interval job (`LDAPServerStateSyncer.Work`), so an intentional demotion (or removal) of a user by an authorized administrator in the upstream LDAP/OIDC identity provider does not take effect for that user's already-issued session/API token until the next `UpstreamSyncInterval` tick elapses.

### Finding Description
`AuthorizedUserWithSession` explicitly reads `user_role` from `ldap_sessions` and returns it without any upstream check: [3](#0-2) 

Similarly `FindUserByAPIToken` returns the cached role from `ldap_user_api_tokens`: [4](#0-3) 

The OIDC driver has the identical pattern: [5](#0-4) 

Role reconciliation with the upstream directory only happens in `LDAPServerStateSyncer.Work`, which is invoked either once at startup (if `UpstreamSyncInterval` is unset) or on a ticker at the configured interval: [6](#0-5) 

This directly contradicts the package doc comment's claim that the sync "happens for every auth endpoint hit": [7](#0-6) 

All gin auth middlewares (`AuthenticateBySession`, `AuthenticateGQL`) call straight into `AuthorizedUserWithSession` per request with no upstream re-validation call: [1](#0-0) [8](#0-7) 

Contrast this with the local-auth driver, which purges all of a user's sessions synchronously and atomically the instant an admin calls `UpdateRole`: [9](#0-8) 
No equivalent immediate-invalidation path exists for LDAP/OIDC drivers — `UpdateRole` is explicitly unsupported there (`ErrNotSupported`): [10](#0-9) 

### Impact Explanation
If an authorized administrator revokes or downgrades a user's privileges in the upstream LDAP/OIDC group (e.g., removing them from the `Admin` group after detecting misuse, or during offboarding), that user's already-issued browser session cookie and/or API token continues to authorize with the old (higher) role for the entire `UpstreamSyncInterval` window (and until `UpstreamSyncRateLimit` also elapses, potentially delaying it further). This allows continued unauthorized admin-level actions (viewing secrets/config, creating jobs, moving funds via job specs, deleting users, etc.) after the administrator believed access had been revoked.

### Likelihood Explanation
This requires the node to be configured with the optional `ldap` or `oidc` `AuthenticationProvider` (not the default local auth), and depends on operators setting a non-trivial `UpstreamSyncInterval`/`UpstreamSyncRateLimit`. It is a design/timing gap rather than a bypassable check, so exploitation is deterministic (not race-dependent) for the duration of the sync window, but the affected surface is limited to deployments using these pluggable auth drivers.

### Recommendation
For LDAP/OIDC drivers, either: (1) revalidate the user's role against the upstream directory (or at minimum re-check a lightweight "still active/current role" signal) on each `AuthorizedUserWithSession`/`FindUserByAPIToken` call rather than trusting the cached DB row indefinitely between syncs; or (2) document and default to a much shorter `UpstreamSyncInterval`, and update the misleading docstring claim that sync happens "for every auth endpoint hit" to accurately reflect the interval-only behavior so operators can assess risk correctly.

### Proof of Concept
1. Configure chainlink node with `[WebServer.LDAP]` (or OIDC) auth, `UpstreamSyncInterval` set to e.g. `1h`.
2. User `alice` is a member of the upstream `Admin` LDAP group; she logs in via `POST /sessions`, receiving a session cookie whose `ldap_sessions.user_role = admin`.
3. An authorized LDAP administrator removes `alice` from the `Admin` group (demoting her to `View`) directly in the LDAP directory.
4. Within the current sync interval, `alice` replays her existing session cookie against an admin-only endpoint (e.g. `PATCH /v2/users`, `RequiresAdminRole`-protected routes). `AuthorizedUserWithSession` returns the stale cached `admin` role from `ldap_sessions`, and `RequiresAdminRole` grants access — the demotion has not propagated.
5. Access remains until `LDAPServerStateSyncer.Work` next runs and updates/purges `ldap_sessions` for `alice`.

### Citations

**File:** core/web/auth/auth.go (L52-66)
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

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
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

**File:** core/sessions/ldapauth/ldap.go (L474-477)
```go
// UpdateRole is not supported for read only LDAP
func (l *ldapAuthenticator) UpdateRole(ctx context.Context, email, newRole string) (sessions.User, error) {
	return sessions.User{}, sessions.ErrNotSupported
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
