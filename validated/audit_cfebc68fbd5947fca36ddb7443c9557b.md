### Title
Stale Cached Role in LDAP/OIDC Session Table Enables Post-Demotion Privileged Access - ([File: core/sessions/ldapauth/ldap.go])

### Summary
When Chainlink's `WebServer.AuthenticationMethod` is set to `ldap` or `oidc`, the node caches the authenticated user's `role` in a local `ldap_sessions` / `oidc_sessions` table at login time. Every subsequent HTTP request re-validates the session by SQL lookup, but the role value returned comes exclusively from this locally cached row — it is not re-fetched from the upstream LDAP directory or OIDC identity provider on a per-request basis. The only mechanism intended to reconcile the cached role with the upstream source of truth is `LDAPServerStateSyncer.Work`, but this is gated behind `UpstreamSyncInterval`, which defaults to `'0s'` — a value that causes the syncer to run `Work()` exactly once, at node startup, and never again on a timer.

### Finding Description
`AuthorizedUserWithSession` for the LDAP provider queries only the local `ldap_sessions` table and returns the `user_role` value stored there, checking merely that the session hasn't expired by elapsed time: [1](#0-0) 

The equivalent OIDC path behaves identically, sourcing the role from `oidc_sessions.user_role`: [2](#0-1) 

This role is consulted by `RequiresAdminRole`/`RequiresEditRole`/`RequiresRunRole` middleware on every subsequent authenticated request: [3](#0-2) 

The single mechanism designed to keep the cached role fresh — `LDAPServerStateSyncer` — updates `ldap_sessions.user_role`/`ldap_user_api_tokens.user_role` to match the upstream state: [4](#0-3) 

But this sync is only invoked on a recurring ticker if `UpstreamSyncInterval` is non-zero; with the documented default of `'0s'`, `Start()` calls `Work()` a single time at node boot and never schedules further reconciliation: [5](#0-4) [6](#0-5) 

No other code path invokes `Work()` — it is only referenced within `sync.go` itself, so there is no login/logout-triggered resync despite what the config documentation implies. This means once a user's `ldap_sessions`/`oidc_sessions` row is created with `role='admin'`, that role is trusted for every request until the row's `created_at + SessionTimeout` expires, with no revalidation against the live LDAP group membership or OIDC claims in between — structurally the same "authorize against a stale cached role instead of the live source of truth" bug class as the Open WebUI `SESSION_POOL` issue, just backed by a DB row instead of an in-memory map.

By contrast, `localauth.orm.UpdateRole` is not vulnerable to this class — it explicitly purges all of the user's `sessions` rows in the same transaction as the role update, forcing immediate re-authentication: [7](#0-6) 

### Impact Explanation
An admin who is demoted (or has their upstream LDAP/OIDC group membership revoked) while using LDAP or OIDC authentication retains their cached `admin` role for every authenticated HTTP/GraphQL API call — including `RequiresAdminRole`-gated endpoints — until their session naturally expires per `SessionTimeout` (default 15 minutes, operator-configurable to much longer values), because the default `UpstreamSyncInterval='0s'` disables any periodic reconciliation. This affects `RequiresAdminRole`, `RequiresEditRole`, and `RequiresRunRole` gated actions across the node's HTTP/GraphQL API surface, not merely a collaborative-notes feature as in the original report, extending the practical impact to node administration actions performed via a stale privileged session.

### Likelihood Explanation
Exploitation requires no special network position: it is triggered purely by the demoted/former-admin user continuing to send ordinary authenticated API requests with their existing session cookie — the exact "unprivileged (post-demotion) client request" pattern called out as in-scope. The only precondition is operating with LDAP or OIDC authentication and the default `UpstreamSyncInterval`, which per `core.toml` is the shipped default, making this a realistic misconfiguration-free scenario rather than an edge case.

### Recommendation
- Change the default `UpstreamSyncInterval` to a bounded non-zero value, or explicitly document/warn that `'0s'` disables ongoing role revalidation.
- Additionally, have `AuthorizedUserWithSession` for the LDAP/OIDC providers perform (or trigger) an upstream role check when the cached row's role is `admin` (or at minimum on a lighter, request-scoped cadence), rather than relying solely on the periodic `Work()` sync.
- Mirror `localauth.orm.UpdateRole`'s behavior by purging/marking-stale the corresponding `ldap_sessions`/`oidc_sessions`/`*_user_api_tokens` rows immediately whenever a `Work()` sync detects a role change for a user, rather than only updating the role value in place (which still leaves a window where in-flight requests using an already-fetched, pre-update role snapshot could race).

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with default `UpstreamSyncInterval = '0s'` and a long `SessionTimeout`.
2. User B logs in while a member of the LDAP `NodeAdmins` group; `ldapauth.CreateSession` inserts an `ldap_sessions` row with `user_role='admin'`.
3. An operator removes User B from the `NodeAdmins` LDAP group upstream.
4. Because `UpstreamSyncInterval='0s'`, `LDAPServerStateSyncer.Work` runs only once at node startup and is never re-invoked; User B's `ldap_sessions.user_role` remains `'admin'`.
5. User B continues issuing requests with their existing session cookie against `RequiresAdminRole`-gated endpoints (e.g., `PATCH /v2/users`); `AuthorizedUserWithSession` returns the stale `admin` role, and `RequiresAdminRole` permits the request until the session's `created_at + SessionTimeout` expires.

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

**File:** core/sessions/ldapauth/sync.go (L245-275)
```go
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

**File:** core/config/docs/core.toml (L268-268)
```text
# UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
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
