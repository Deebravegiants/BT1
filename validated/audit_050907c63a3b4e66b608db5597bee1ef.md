## Finding: Password Change Does Not Revoke Existing API Tokens

This chainlink repo contains a direct analog to CVE-2021-39872. When a Chainlink node user resets their password (either via the REST endpoint or the GraphQL mutation), previously issued API tokens remain valid indefinitely, allowing continued node access exactly as in the GitLab CVE.

### Title
Password Reset Fails to Revoke Existing API Tokens, Allowing Continued Node Access - (File: core/sessions/localauth/orm.go)

### Summary
The local-auth `SetPassword` implementation only updates the `hashed_password` column and never touches the user's stored API token (`token_key`/`token_hashed_secret`). The two call sites that perform a self-service password change — the GraphQL `UpdateUserPassword` resolver and the REST `UpdatePassword`/`updateUserPassword` handler — only clear *other cookie sessions* via `ClearNonCurrentSessions`, but never revoke the user's API token via `DeleteAuthToken`. As a result, an API token acquired before a password reset continues to authenticate successfully after the password is changed.

### Finding Description
`SetPassword` updates only the password hash: [1](#0-0) 

`ClearNonCurrentSessions` only deletes rows from the `sessions` table (browser cookie sessions), leaving the `users.token_key`/`token_hashed_secret` columns untouched: [2](#0-1) 

Both password-change entry points call these two functions and nothing else — no call to `DeleteAuthToken`: [3](#0-2) [4](#0-3) 

Meanwhile, API token authentication (`AuthenticateByToken`) looks up the user solely by `token_key` and validates the HMAC secret — it has no dependency on the current password or a password-change timestamp: [5](#0-4) [6](#0-5) 

This mirrors the GitLab CVE's root cause precisely: password rotation invalidates the interactive session mechanism (cookie sessions here, GitLab's password-based sessions there) but not the token-based access mechanism (API tokens here, personal/git access tokens there).

Note: the LDAP (`core/sessions/ldapauth/ldap.go`) and OIDC (`core/sessions/oidcauth/oidc.go`) authenticators are less affected in practice since `SetPassword`/`TestPassword` for those providers largely fall back to a local admin account or return `ErrNotSupported`, but the primary/default local-auth path is fully exposed.

### Impact Explanation
An attacker who has obtained a valid API token for a Chainlink node user (e.g., via credential leak, insider threat, or a compromised CI secret) retains full API access — including operator/admin-role actions depending on the token's role — even after the legitimate user detects the compromise and changes their password. Since the whole point of a password reset in this scenario is to cut off unauthorized access, this represents a real access-control failure with potential for continued unauthorized job management, config changes, or key/secret operations depending on the token's role.

### Likelihood Explanation
The flaw is triggered by the normal, expected password-reset flow — no special conditions or race required. Any user with a previously created API token (`NewAPIToken`/`CreateAPIToken`) who changes their password via the standard REST or GraphQL flow leaves that token active. This is deterministic and 100% reproducible, not a timing or race condition.

### Recommendation
Have `SetPassword` (or its callers in `mutation.go`/`user_controller.go`) also invoke `DeleteAuthToken` (or explicitly rotate `token_key`/`token_hashed_secret`) whenever a password reset occurs, so previously issued API tokens are revoked along with cookie sessions. Alternatively, tie API token validity to a `updated_at`/`password_changed_at` comparison enforced in `FindUserByAPIToken`.

### Proof of Concept
1. As user A, create an API token: `POST /v2/users/tokens` (invokes `UserController.NewAPIToken`, sets `token_key`/`token_hashed_secret`).
2. Using the returned `AccessKey`/`Secret`, call any authenticated REST endpoint successfully (`AuthenticateByToken` succeeds).
3. As user A, change the password via `PATCH /v2/user/password` or the `updateUserPassword` GraphQL mutation — this calls `ClearNonCurrentSessions` + `SetPassword` only.
4. Repeat step 2 with the *same* original API token/secret — the request still succeeds because `token_key`/`token_hashed_secret` were never modified, demonstrating continued access post-password-reset.

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

**File:** core/web/resolver/mutation.go (L934-970)
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

**File:** core/web/auth/auth.go (L78-112)
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

	c.Set(SessionUserKey, &user)

	return nil
}
```
