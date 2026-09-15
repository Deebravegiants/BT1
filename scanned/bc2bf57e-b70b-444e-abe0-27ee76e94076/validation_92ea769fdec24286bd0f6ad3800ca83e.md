### Title
Stale role cached in LDAP/OIDC session tables is not revoked when upstream role changes, permitting continued elevated access - ([File: core/sessions/ldapauth/ldap.go])

### Summary
This maps the report's core defect — an authorization grant ("approval") that is not revoked when the underlying ownership/permission changes, allowing the old grant to still be exercised — onto the way `chainlink` caches a user's role in the LDAP/OIDC session tables at login time and never re-validates or updates it for the lifetime of the session.

### Finding Description
For the local-auth provider, `AuthorizedUserWithSession` re-reads the user's current role from the `users` table on every request, so a role downgrade or account disablement takes effect immediately (`core/sessions/localauth/orm.go` lines 87-106) [1](#0-0) .

For the LDAP and OIDC authentication providers, however, the role is fetched from the identity provider **only once, at session-creation time**, and is then persisted (cached) in the `ldap_sessions` / `oidc_sessions` tables. Every subsequent authorization check for that session simply reads the cached `user_role` column back out of the sessions table without contacting LDAP/OIDC again: [2](#0-1) [3](#0-2) 

Both `UpdateRole` implementations for LDAP and OIDC explicitly state role management is not supported locally — role is derived solely from upstream group membership at login: [4](#0-3) 

The LDAP provider does have a background sync task (`core/sessions/ldapauth/sync.go`) that polls the upstream LDAP server, but this reconciles the local `users`/group-membership mirror — not necessarily the `user_role` value already baked into every *live* `ldap_sessions` row. If a user is demoted or removed from an admin group upstream, their currently open session (which can live up to the configured `SessionTimeout`) keeps returning the old, cached `UserRole` value from `AuthorizedUserWithSession` until the session naturally expires, exactly analogous to the NFT bug where a stale `getApproved` value continues to authorize a transfer after the underlying ownership changed. This is functionally equivalent to failing to clear an approval/permission when the authoritative state (group membership/role) changes.

By contrast, note that `UpdateUserPassword` for local users at least revokes *other* sessions via `ClearNonCurrentSessions` on password change [5](#0-4) , but there is no equivalent mechanism to force LDAP/OIDC sessions to re-validate role on a role/group change from the identity provider side.

### Impact Explanation
An unprivileged actor whose LDAP/OIDC group membership is revoked (e.g. removed from the admin group after being fired, or downgraded from admin to view) retains their previously-granted role/permissions for the remainder of the active session window (bounded by `SessionTimeout`), potentially enabling continued admin-level actions (job management, key management, fund-affecting operations) against the node's API after they should have lost that access — a role/permission bypass analogous to the reported unrevoked-approval NFT recovery.

### Likelihood Explanation
Likelihood is moderate: it requires (a) LDAP or OIDC authentication mode enabled (not the default local auth), (b) an existing active session, and (c) the identity provider revoking/demoting the user's role after the session was created but before it expires or is otherwise cleared. This is a normal offboarding/role-change scenario for any org using LDAP/OIDC-integrated node access, so it is a realistic operational occurrence rather than a contrived edge case.

### Recommendation
- On each `AuthorizedUserWithSession` call for LDAP/OIDC, either re-derive the role from the (possibly cached, but freshly synced) local mirror of upstream group membership rather than trusting the value frozen into the session row at creation time, or reduce `SessionTimeout` and force periodic re-authentication.
- Have the LDAP background sync task (`core/sessions/ldapauth/sync.go`) actively update/invalidate the `user_role` in `ldap_sessions` (and the OIDC equivalent) whenever a user's group membership changes upstream, mirroring the "clear approval on transfer" fix pattern from the report.
- Alternatively, expose an explicit session-revocation hook that identity-provider administrators can trigger to immediately invalidate all sessions for a demoted/removed user, similar to `ClearNonCurrentSessions`.

### Proof of Concept
1. Configure the node with LDAP (or OIDC) auth and place `userA` in the admin group.
2. `userA` logs in; `AuthorizedUserWithSession` inserts a row into `ldap_sessions` with `user_role = admin`.
3. An LDAP administrator removes `userA` from the admin group (demotes to view-only) in the directory.
4. `userA`'s existing session cookie is still valid (within `SessionTimeout`); every subsequent request calls `AuthorizedUserWithSession`, which reads the stale `user_role = admin` value straight from `ldap_sessions` (`core/sessions/ldapauth/ldap.go` lines 356-372) without re-checking LDAP group membership.
5. `userA` continues to perform admin-only actions (e.g., via `RequiresAdminRole`-gated endpoints, `core/web/auth/auth.go` lines 236-253) until the session naturally times out, despite no longer holding admin privileges upstream.

### Citations

**File:** core/sessions/localauth/orm.go (L83-106)
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

**File:** core/web/user_controller.go (L341-360)
```go
func (u *UserController) updateUserPassword(c *gin.Context, user *clsession.User, newPassword string) error {
	ctx := c.Request.Context()
	sessionID, err := getCurrentSessionID(c)
	if err != nil {
		return err
	}
	orm := u.App.AuthenticationProvider()
	if err := orm.ClearNonCurrentSessions(ctx, sessionID); err != nil {
		u.App.GetLogger().Errorf("failed to clear non current user sessions: %s", err)
		return errors.New("unable to update password")
	}
	if err := orm.SetPassword(ctx, user, newPassword); err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			return errUnsupportedForAuth
		}
		u.App.GetLogger().Errorf("failed to update current user password: %s", err)
		return errors.New("unable to update password")
	}
	return nil
}
```
