Audit Report

## Title
Password Reset Fails to Revoke Existing API Tokens, Allowing Continued Node Access - (File: core/sessions/localauth/orm.go)

## Summary
`SetPassword` in `core/sessions/localauth/orm.go` only updates the `hashed_password` column and never rotates or clears the user's `token_key`/`token_hashed_secret`/`token_salt` fields [1](#0-0) . Both self-service password-change entry points — the GraphQL `UpdateUserPassword` resolver and the REST `updateUserPassword` handler — call `ClearNonCurrentSessions` (which only deletes cookie-session rows) followed by `SetPassword`, and never call `DeleteAuthToken` [2](#0-1) [3](#0-2) . Consequently an API token issued prior to a password reset remains valid and continues to authenticate via `AuthenticateByToken`/`FindUserByAPIToken` indefinitely after the password is changed.

## Finding Description
`ClearNonCurrentSessions` only deletes rows from the `sessions` table, keyed by session ID/email, and has no interaction with the `token_key` or `token_hashed_secret` columns [4](#0-3) . `SetPassword` similarly touches only `hashed_password` and `updated_at` [1](#0-0) . The code base does have a dedicated revocation primitive, `DeleteAuthToken`, which clears `token_salt`, `token_key`, and `token_hashed_secret` [5](#0-4) , but it is invoked only from the separate, explicit "delete API token" flow in `UserController.DeleteAPIToken` (which itself requires re-entering the password) [6](#0-5)  — it is never invoked as part of the password-change flows.

Both password-change call sites confirm this gap:
- GraphQL: `Resolver.UpdateUserPassword` calls `ClearNonCurrentSessions` then `SetPassword`, with no `DeleteAuthToken` call [7](#0-6) .
- REST: `UserController.updateUserPassword` calls the identical pair of ORM methods, again omitting `DeleteAuthToken` [3](#0-2) .

On the authentication side, `AuthenticateByToken` resolves the user strictly via `FindUserByAPIToken` (a `token_key` lookup) and then HMAC-validates the secret — there is no check against password state, `updated_at`, or any "credentials rotated" flag [8](#0-7)  and [9](#0-8) . This confirms the existing checks (session-clearing, password-hash update) are insufficient to sever token-based access, and the broken security assumption is that a password reset severs *all* forms of authenticated access rather than only cookie-based sessions.

## Impact Explanation
This maps to the in-scope "node API authentication or role bypass" impact category: any previously issued API token continues to grant full API access at its assigned role (including operator/admin-capable actions such as job management, key operations, or config changes) even after the account holder performs a password reset intended to cut off that access. This is a genuine access-control/authorization lifecycle defect in the node's own code, not a misconfiguration, host compromise, or third-party dependency issue, and directly parallels the accepted real-world analog, GitLab's CVE-2021-39872.

## Likelihood Explanation
The flaw is deterministic and requires no race condition or unusual configuration: a user creates an API token via `NewAPIToken`, later triggers a normal password reset via either the REST `PATCH /v2/user/password` or GraphQL `updateUserPassword` mutation, and the original token remains fully functional afterward. Reproduction requires only actions available to a standard authenticated user against the node's own public API surface — no operator/admin/host access beyond the victim's own account is needed to demonstrate the defect (the "already have a token" precondition here is the very security boundary password-reset is supposed to enforce, not an out-of-scope credential-leak precondition for privilege escalation).

## Recommendation
Have `SetPassword` (or its two callers in `mutation.go` and `user_controller.go`) also invoke `DeleteAuthToken` — or explicitly rotate `token_key`/`token_hashed_secret`/`token_salt` — whenever a password reset occurs, so that previously issued API tokens are revoked in lockstep with cookie sessions. As an alternative, bind API token validity to a `password_changed_at` timestamp checked in `FindUserByAPIToken`/`AuthenticateByToken`.

## Proof of Concept
1. As user A, create an API token: `POST /v2/users/tokens` (invokes `UserController.NewAPIToken`, populating `token_key`/`token_hashed_secret`).
2. Using the returned `AccessKey`/`Secret`, call any authenticated REST endpoint — succeeds via `AuthenticateByToken`.
3. As user A, change the password via `PATCH /v2/user/password` (or the `updateUserPassword` GraphQL mutation) — this calls only `ClearNonCurrentSessions` + `SetPassword`.
4. Repeat step 2 with the same original API token/secret — the request still succeeds because `token_key`/`token_hashed_secret` were never modified, demonstrating continued access after the password reset. A Go integration test can assert this by calling `orm.SetPassword` and then verifying `orm.FindUserByAPIToken` + `sessions.AuthenticateUserByToken` still succeed with the pre-reset token.

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

**File:** core/sessions/localauth/orm.go (L342-346)
```go
// DeleteAuthToken clears and disables the users Authentication Token.
func (o *orm) DeleteAuthToken(ctx context.Context, user *sessions.User) error {
	sql := "UPDATE users SET token_salt = '', token_key = '', token_hashed_secret = '', updated_at = now() WHERE email = $1 RETURNING *"
	return o.ds.GetContext(ctx, user, sql, user.Email)
}
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

**File:** core/web/auth/auth.go (L78-107)
```go
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
```
