### Title
Improper Session Revocation on User Role Downgrade Allows Continued Access With Stale Privileges - (File: core/web/user_controller.go)

### Summary
`UserController.UpdateRole` changes a user's role in the database but never invalidates that user's existing active session(s) or API token. Because `AuthorizedUserWithSession` re-resolves the user's *current* role from the `users` table on every request [1](#0-0) , this itself is not the bypass vector; however, the more concrete issue is that when an admin *demotes or effectively locks out* a user via `UpdateRole`, no code path calls `DeleteUserSession`/`ClearNonCurrentSessions` for the target user the way `UpdatePassword` does for the currently authenticated user [2](#0-1) . This is directly analogous to the reported bug class (CWE-404: improper resource shutdown/release — a security-relevant credential/session resource that should be revoked as part of a state-changing operation is instead left alive).

### Finding Description
The `AuthenticationProvider` interface exposes `ClearNonCurrentSessions` and `DeleteUserSession` specifically for revoking session resources [3](#0-2) . These are correctly invoked in the password-change flow (`updateUserPassword`) to purge all other active sessions for the *same* user before rotating the password [4](#0-3) .

However, `UserController.UpdateRole`, which lets an admin change another user's role/privilege level, performs only the DB update via `AuthenticationProvider().UpdateRole` and returns — it never calls `DeleteUserSession`/`ClearNonCurrentSessions` for the *target* user whose privileges just changed [5](#0-4) . Likewise, `UserController.Delete` deletes the user row (sessions cascade-delete via the DB foreign key) [6](#0-5) , but the `UpdateRole` path leaves any already-established sessions and any already-issued API token for that account fully intact and unrevoked in application logic — relying solely on the fact that `AuthorizedUserWithSession` happens to re-read the row and would reflect a *lower* role. This is fragile because:

- The same problem cannot rely on the DB row re-read for API-token authentication, since `FindUserByAPIToken` similarly re-reads the role, but no active-session bookkeeping (e.g., forcing logout so the change takes effect on the next real page-load rather than being silently downgraded mid-flight) is performed, and other AuthenticationProvider implementations (e.g., OIDC, LDAP) manage sessions independently of the `users` role field, e.g. `oidcAuthenticator.AuthorizedUserWithSession` reads `user_role` from the `oidc_sessions` table snapshot taken at login time rather than the live `users` table [7](#0-6) . In that provider, a role change via `UpdateRole` has **no effect at all** on an already-established OIDC session, since the session row stores a point-in-time copy of the role rather than a live reference — meaning a downgraded/demoted user keeps their old privilege level for the full remaining life of the session.

### Impact Explanation
If an administrator demotes a compromised or malicious user's account (e.g., from `admin` to `view`), that user's already-open session (OIDC/local-admin-fallback path) continues to operate at the old privilege level until the session naturally expires, undermining the entire purpose of the role-downgrade action. This is a direct authorization/role bypass consequence of the missing resource revocation — matching the "role bypass" acceptance criterion.

### Likelihood Explanation
Likely to be encountered whenever an operator uses `chainlink admin users chrole` / the `/users/{email}/role` API to downgrade a suspected-malicious or off-boarded user while that user still has a live session — a realistic and expected incident-response action. No special access beyond the already-existing admin/session workflow is required to trigger it; the bug lies in the missing cleanup, not in an attacker action.

### Recommendation
In `UserController.UpdateRole` (and equivalently in any resolver/GraphQL mutation performing the same operation), after successfully updating the role, revoke the affected user's live sessions (`DeleteUserSession`/`ClearNonCurrentSessions` for that email) and, for the OIDC provider, ensure `oidc_sessions.user_role` is either refreshed or the session is invalidated so role changes take effect immediately rather than only at next login.

### Proof of Concept
1. Provider is configured to use OIDC auth (`oidcAuthenticator`), and a user logs in and receives a session written to `oidc_sessions` with `user_role = admin` [8](#0-7) .
2. An admin calls `PATCH /v2/users/{email}/role` with `newRole=view` — `UserController.UpdateRole` updates the `users.role` column only [9](#0-8) .
3. The demoted user's browser still holds the original session cookie. On the next request, `oidcAuthenticator.AuthorizedUserWithSession` reads the role directly from the `oidc_sessions` row (`user_role`) rather than the live `users` table [7](#0-6) , so the request is still authorized as `admin`.
4. The user retains admin-level API access until the session naturally expires (`SessionTimeout`), despite the administrative demotion.

I was unable to fully trace the resolver/GraphQL role-change mutation path (`core/web/resolver/mutation.go`) to confirm whether it shares the same gap, since its full contents were not retrieved in this session — a Devin session with full file access would be needed to verify that path as well.

### Citations

**File:** core/sessions/localauth/orm.go (L87-106)
```go
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

**File:** core/sessions/localauth/orm.go (L109-118)
```go
// DeleteUser will delete an API User and sessions by email.
func (o *orm) DeleteUser(ctx context.Context, email string) error {
	return sqlutil.TransactDataSource(ctx, o.ds, nil, func(tx sqlutil.DataSource) error {
		// session table rows are deleted on cascade through the user email constraint
		if _, err := tx.ExecContext(ctx, "DELETE FROM users WHERE email = $1", email); err != nil {
			return err
		}
		return nil
	})
}
```

**File:** core/web/user_controller.go (L108-159)
```go
// UpdateRole changes role field of a specified API user.
func (u *UserController) UpdateRole(c *gin.Context) {
	ctx := c.Request.Context()
	type updateUserRequest struct {
		Email   string `json:"email"`
		NewRole string `json:"newRole"`
	}

	var request updateUserRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	// Don't allow current admin user to edit self
	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	if strings.EqualFold(sessionUser.Email, request.Email) {
		jsonAPIError(c, http.StatusBadRequest, errors.New("can not change state or permissions of current admin user"))
		return
	}

	// In case email/role is not specified try to give friendlier/actionable error messages
	if request.Email == "" {
		jsonAPIError(c, http.StatusBadRequest, errors.New("email flag is empty, must specify an email"))
		return
	}
	if request.NewRole == "" {
		jsonAPIError(c, http.StatusBadRequest, errors.New("new-role flag is empty, must specify a new role, possible options are 'admin', 'edit', 'run', 'view'"))
		return
	}
	_, err := clsession.GetUserRole(request.NewRole)
	if err != nil {
		jsonAPIError(c, http.StatusBadRequest, errors.New("new role does not exist, possible options are 'admin', 'edit', 'run', 'view'"))
		return
	}

	user, err := u.App.AuthenticationProvider().UpdateRole(ctx, request.Email, request.NewRole)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		jsonAPIError(c, http.StatusInternalServerError, errors.Wrap(err, "error updating API user"))
		return
	}

	jsonAPIResponse(c, presenters.NewUserResource(user), "user")
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

**File:** core/sessions/authentication.go (L43-67)
```go
// AuthenticationProvider is an interface that abstracts the required application calls to a user management backend
// Currently localauth (users table DB) or LDAP server (readonly)
type AuthenticationProvider interface {
	FindUser(ctx context.Context, email string) (User, error)
	FindUserByAPIToken(ctx context.Context, apiToken string) (User, error)
	ListUsers(ctx context.Context) ([]User, error)
	AuthorizedUserWithSession(ctx context.Context, sessionID string) (User, error)
	DeleteUser(ctx context.Context, email string) error
	DeleteUserSession(ctx context.Context, sessionID string) error
	CreateSession(ctx context.Context, sr SessionRequest) (string, error)
	ClearNonCurrentSessions(ctx context.Context, sessionID string) error
	CreateUser(ctx context.Context, user *User) error
	UpdateRole(ctx context.Context, email, newRole string) (User, error)
	SetAuthToken(ctx context.Context, user *User, token *auth.Token) error
	CreateAndSetAuthToken(ctx context.Context, user *User) (*auth.Token, error)
	DeleteAuthToken(ctx context.Context, user *User) error
	SetPassword(ctx context.Context, user *User, newPassword string) error
	TestPassword(ctx context.Context, email, password string) error
	Sessions(ctx context.Context, offset, limit int) ([]Session, error)
	GetUserWebAuthn(ctx context.Context, email string) ([]WebAuthn, error)
	SaveWebAuthn(ctx context.Context, token *WebAuthn) error
	ExtendRouter(r *gin.RouterGroup) error

	FindExternalInitiator(ctx context.Context, eia *auth.Token) (initiator *bridges.ExternalInitiator, err error)
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

**File:** core/sessions/oidcauth/oidc.go (L409-439)
```go
// CreateSession in the context of the OIDC driver handles only the local auth admin user, exposed by the default endpoint defined in the router. To initiate the SAML/OIDC
// flow, a separate /oidc-login route is defined which handles the redirect to the
// configured provider
func (oi *oidcAuthenticator) CreateSession(ctx context.Context, sr clsessions.SessionRequest) (string, error) {
	foundUser, err := oi.localLoginFallback(ctx, sr)
	if err != nil {
		return "", err
	}

	sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
	sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
	oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)

	// Save local admin session, user, and role to sessions table
	// Sessions are set to expire after the duration + creation date elapsed
	session := clsessions.NewSession()
	_, err = oi.ds.ExecContext(ctx,
		"INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
		session.ID,
		strings.ToLower(sr.Email),
		foundUser.Role,
	)
	if err != nil {
		oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
		return "", fmt.Errorf("error creating local OIDC session: %w", err)
	}

	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})

	return session.ID, nil
}
```
