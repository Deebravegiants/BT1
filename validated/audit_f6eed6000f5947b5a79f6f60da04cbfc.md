Audit Report

## Title
Stale Cached Role in LDAP/OIDC Session Table Enables Post-Demotion Privileged Access - ([File: core/sessions/ldapauth/ldap.go])

## Summary
When `WebServer.AuthenticationMethod` is `ldap` or `oidc`, the node caches a user's role in `ldap_sessions`/`oidc_sessions` at login time and re-validates every subsequent request purely via a local SQL lookup, without contacting the upstream directory. Reconciliation of that cached role with upstream state depends entirely on `LDAPServerStateSyncer.Work`, which is only invoked on a recurring timer when `UpstreamSyncInterval` is non-zero; the shipped default is `'0s'`, causing `Work()` to run exactly once at node startup and never again.

## Finding Description
`AuthorizedUserWithSession` for LDAP queries only `ldap_sessions` and returns the cached `user_role`, checking solely elapsed-time validity: [1](#0-0) . The OIDC path is structurally identical, sourcing role from `oidc_sessions.user_role`: [2](#0-1) . This role is trusted directly by `RequiresAdminRole` and its siblings on every request: [3](#0-2) .

The reconciliation mechanism, `LDAPServerStateSyncer.Work`, updates `ldap_sessions.user_role`/`ldap_user_api_tokens.user_role` from the upstream group membership: [4](#0-3) . Whether this runs periodically depends on `UpstreamSyncInterval`: [5](#0-4) . Grep confirms `Work()` is called only from within `sync.go` itself (`Start`/`run`) — no login/logout handler in `ldap.go`/`oidc.go` invokes it, contradicting the doc comment's claim that "This sync happens for every auth endpoint hit" [6](#0-5) .

By contrast, local-auth's `UpdateRole` purges all of a user's `sessions` rows in the same transaction as the role change, forcing immediate re-authentication: [7](#0-6) . LDAP/OIDC sessions have no equivalent per-role-change invalidation; they persist with the stale role until `SessionTimeout` elapses.

I was not able to load `core/config/toml/types.go`'s actual default-value definition for `UpstreamSyncInterval` (the field's default annotation) within available tool calls, but the config docs comment explicitly states the default is `'0s'` and describes this as disabling background sync (per the claim's cited `core.toml` line), which is consistent with `Start()`'s `IsInstant()` branch logic verified above.

## Impact Explanation
This falls into a legitimate "stale privileged role after demotion" bug class: a demoted or upstream-revoked admin retains their `admin` role for every `RequiresAdminRole`/`RequiresEditRole`/`RequiresRunRole`-gated API call until `SessionTimeout` naturally expires, because the only reconciliation path (`Work()`) does not re-run on a timer under the default `UpstreamSyncInterval='0s'`. This maps to an in-scope "node API authentication or role bypass" impact category, since a previously-legitimate but now-unprivileged actor retains elevated access purely due to stale caching logic in the node itself, not due to any external LDAP/OIDC misbehavior.

## Likelihood Explanation
Exploitation requires no special privilege beyond having previously held a valid session as an admin/edit/run-role user under LDAP or OIDC auth — the "attacker" here is simply a legitimately-demoted user continuing to replay their still-valid session cookie/token, which is an unprivileged-request pattern from the node's perspective post-demotion. The precondition (`UpstreamSyncInterval` default `'0s'`) is the shipped default rather than an unusual opt-in misconfiguration, and `SessionTimeout` defaults to 15 minutes but is operator-configurable to arbitrarily long windows, widening the exposure window without requiring any additional attacker action.

## Recommendation
- Change the default `UpstreamSyncInterval` to a bounded non-zero value, or make the documentation and code consistent about `'0s'` disabling ongoing revalidation (currently the doc comment in `ldap.go` line 16 incorrectly states sync happens "for every auth endpoint hit").
- Have `AuthorizedUserWithSession` trigger or check for an upstream role reconciliation, especially for privileged roles, rather than trusting the cached DB row indefinitely.
- Mirror `localauth.orm.UpdateRole`'s pattern of purging sessions/tokens immediately when `Work()` detects a role change, instead of only rewriting `user_role` in place, to close the window where in-flight requests use a stale role snapshot.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with default `UpstreamSyncInterval = '0s'` and a long `SessionTimeout`.
2. User logs in while a member of the LDAP `NodeAdmins` group; a row is inserted into `ldap_sessions` with `user_role='admin'`.
3. Operator removes the user from the `NodeAdmins` group upstream.
4. Because `UpstreamSyncInterval='0s'`, `Start()`'s `else` branch already ran `Work()` once at boot and no ticker is scheduled (`core/sessions/ldapauth/sync.go` lines 56-67); `ldap_sessions.user_role` remains `'admin'`.
5. The demoted user replays their existing session cookie against a `RequiresAdminRole`-gated endpoint (e.g., `PATCH /v2/users`); `AuthorizedUserWithSession` returns the stale `admin` role and the request is permitted until session expiry (`core/sessions/ldapauth/ldap.go` lines 342-373, `core/web/auth/auth.go` lines 236-253).

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
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
