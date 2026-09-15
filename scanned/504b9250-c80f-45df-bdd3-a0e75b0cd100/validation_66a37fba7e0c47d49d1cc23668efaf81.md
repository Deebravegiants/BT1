Confirmed: `SetPassword` in `core/sessions/localauth/orm.go:299-306` only updates `hashed_password` and does not touch `token_key` (API token) or call `DeleteAuthToken`/`SetAuthToken`. The API token remains valid indefinitely after a password change, since `FindUserByAPIToken` (`core/sessions/localauth/orm.go:49-53`) is a straight lookup with no linkage to password state or `updated_at`. The password-change flow in both the REST controller (`core/web/user_controller.go:341-359`, `updateUserPassword`) and the GraphQL resolver (`core/web/resolver/mutation.go:934-969`, `UpdateUserPassword`) only calls `ClearNonCurrentSessions` (which purges other **session cookie** rows) and `SetPassword` — neither path revokes the user's API token.

### Title
Password change fails to revoke active API tokens, allowing continued unprivileged access after credential rotation - (File: `core/web/user_controller.go`)

### Summary
When a user (including a non-admin, self-service `view`/`edit` role user) changes their own password via `PATCH /v2/user/password` or the `updateUserPassword` GraphQL mutation, the server invalidates other browser session cookies but leaves any previously-issued API token (`token_key`) fully valid.

### Finding Description
`UserController.updateUserPassword` (`core/web/user_controller.go:341-359`) calls `orm.ClearNonCurrentSessions(ctx, sessionID)` followed by `orm.SetPassword(ctx, user, newPassword)`. `ClearNonCurrentSessions` (`core/sessions/localauth/orm.go:244-251`) only deletes rows from the `sessions` table for the user, scoped by session cookie. `SetPassword` (`core/sessions/localauth/orm.go:299-306`) only updates `hashed_password`; it never touches the `token_key`/`token_secret` columns nor calls `DeleteAuthToken`. The same pattern occurs in the GraphQL resolver `UpdateUserPassword` (`core/web/resolver/mutation.go:934-969`), which likewise calls only `ClearNonCurrentSessions` and `SetPassword`. Consequently, `AuthenticateByToken` (`core/web/auth/auth.go:78-112`) and `FindUserByAPIToken` (`core/sessions/localauth/orm.go:49-53`) will continue to authorize requests using the pre-rotation API token indefinitely, because that lookup path is completely decoupled from the password/credential state. This mirrors the GitLab CVE-2021-22221 root cause: a credential-state transition (there, expiry; here, an explicit user-initiated password change) is not propagated to all authentication surfaces, letting a previously-authorized principal retain access through an alternate channel.

### Impact Explanation
If an API token was compromised (e.g., leaked, phished, or a shared/former device retains it) and the legitimate user rotates their password specifically to cut off that access, the attacker's stolen API token still authenticates as that user with full role privileges (`Admin`/`Edit`), enabling continued job management, bridge creation, key operations, or fund-moving actions available to that role — precisely the "maintain limited access after credential invalidation" impact class the analog is drawn from.

### Likelihood Explanation
Likelihood is moderate: exploitation requires that an attacker already possesses a valid API token issued before the password change (e.g., via prior compromise, session/token capture, or previously being an authorized co-user). The bug does not create initial access — it undermines the *remediation* action a victim takes after suspecting compromise, which is exactly when this gap matters most and is most likely to be relied upon.

### Recommendation
On password change (both `UserController.UpdatePassword` and the GraphQL `UpdateUserPassword` resolver), also revoke the user's existing API token, e.g., by calling `DeleteAuthToken(ctx, user)` (already implemented at `core/web/user_controller.go:318` in the `DeleteAPIToken` handler) inside `updateUserPassword`, forcing the user to explicitly reissue a new token via `CreateAndSetAuthToken` if still needed.

### Proof of Concept
1. As user `alice`, call `POST /v2/user/tokens` to obtain an API `access_key`/`secret` (`CreateAndSetAuthToken`).
2. Using that API token, successfully call an authenticated endpoint (e.g., `GET /v2/bridge_types`) — confirms token works.
3. As `alice`, call `PATCH /v2/user/password` with a new password (simulating remediation after suspected token leak).
4. Re-issue the same original API token from step 1 against `GET /v2/bridge_types` (or any `AuthenticateByToken`-protected route) — the request still succeeds, proving the old, supposedly-revoked credential remains valid post password-change. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** core/sessions/localauth/orm.go (L48-53)
```go
// FindUserByAPIToken will attempt to return an API user via the user's table token_key column.
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1"
	err = o.ds.GetContext(ctx, &user, sql, apiToken)
	return
}
```

**File:** core/sessions/localauth/orm.go (L243-251)
```go
// ClearNonCurrentSessions removes other sessions for the user tied to sessionID.
func (o *orm) ClearNonCurrentSessions(ctx context.Context, sessionID string) error {
	var email string
	if err := o.ds.GetContext(ctx, &email, "SELECT email FROM sessions WHERE id = $1", sessionID); err != nil {
		return err
	}
	_, err := o.ds.ExecContext(ctx, "DELETE FROM sessions WHERE lower(email) = lower($1) AND id != $2", email, sessionID)
	return err
}
```

**File:** core/sessions/localauth/orm.go (L298-306)
```go
// SetAuthToken updates the user to use the given Authentication Token.
func (o *orm) SetPassword(ctx context.Context, user *sessions.User, newPassword string) error {
	hashedPassword, err := utils.HashPassword(newPassword)
	if err != nil {
		return err
	}
	sql := "UPDATE users SET hashed_password = $1, updated_at = now() WHERE email = $2 RETURNING *"
	return o.ds.GetContext(ctx, user, sql, hashedPassword, user.Email)
}
```

**File:** core/web/user_controller.go (L288-330)
```go
// DeleteAPIToken deletes and disables a user's API token.
func (u *UserController) DeleteAPIToken(c *gin.Context) {
	ctx := c.Request.Context()
	var request clsession.ChangeAuthTokenRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to delete API token"))
		return
	}
	err = u.App.AuthenticationProvider().TestPassword(ctx, sessionUser.Email, request.Password)
	if err != nil {
		u.App.GetAuditLogger().Audit(audit.APITokenDeleteAttemptPasswordMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusUnauthorized, errors.New("incorrect password"))
		return
	}
	if err := u.App.AuthenticationProvider().DeleteAuthToken(ctx, &user); err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
	{
		u.App.GetAuditLogger().Audit(audit.APITokenDeleted, map[string]any{"user": user.Email})
		jsonAPIResponseWithStatus(c, nil, "auth_token", http.StatusNoContent)
	}
}
```

**File:** core/web/user_controller.go (L341-359)
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
```

**File:** core/web/resolver/mutation.go (L934-969)
```go
func (r *Resolver) UpdateUserPassword(ctx context.Context, args struct {
	Input UpdatePasswordInput
}) (*UpdatePasswordPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	session, ok := webauth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return nil, errors.New("couldn't retrieve user session")
	}

	dbUser, err := r.App.AuthenticationProvider().FindUser(ctx, session.User.Email)
	if err != nil {
		return nil, err
	}

	if !utils.CheckPasswordHash(args.Input.OldPassword, string(dbUser.HashedPassword)) {
		r.App.GetAuditLogger().Audit(audit.PasswordResetAttemptFailedMismatch, map[string]any{"user": dbUser.Email})

		return NewUpdatePasswordPayload(nil, map[string]string{
			"oldPassword": "old password does not match",
		}), nil
	}

	if err = r.App.AuthenticationProvider().ClearNonCurrentSessions(ctx, session.SessionID); err != nil {
		return nil, clearSessionsError{}
	}

	err = r.App.AuthenticationProvider().SetPassword(ctx, &dbUser, args.Input.NewPassword)
	if err != nil {
		return nil, failedPasswordUpdateError{}
	}

	r.App.GetAuditLogger().Audit(audit.PasswordResetSuccess, map[string]any{"user": dbUser.Email})
	return NewUpdatePasswordPayload(session.User, nil), nil
```

**File:** core/web/auth/auth.go (L75-112)
```go
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
