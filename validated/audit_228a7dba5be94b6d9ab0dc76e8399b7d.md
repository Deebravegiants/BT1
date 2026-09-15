Confirmed: `UserController.UpdatePassword` / `updateUserPassword` only calls `ClearNonCurrentSessions` and `SetPassword`, but never touches the API token fields (`token_key`, `token_hashed_secret`) via `DeleteAuthToken`.This confirms `AuthenticateByToken` (`core/web/auth/auth.go:78-112`) authenticates purely via the `X-API-KEY`/`X-API-SECRET` pair stored in `token_key`/`token_hashed_secret` columns, which is completely independent of the `hashed_password` column touched by `SetPassword`. The router wires `/v2/user/password` to `UserController.UpdatePassword`, whose `updateUserPassword` helper only calls `ClearNonCurrentSessions` (deletes other cookie-based sessions) and `SetPassword` (updates `hashed_password`) — it never calls `DeleteAuthToken`/`SetAuthToken`.

### Title
Password change fails to revoke existing API tokens, allowing continued authenticated access with stale credentials - (File: core/web/user_controller.go)

### Summary
When a user changes their password via `PATCH /v2/user/password` (or the equivalent GraphQL `updateUserPassword` mutation), the server only clears other cookie-based web sessions and updates the hashed password. It never invalidates the user's existing API token (`token_key`/`token_hashed_secret`), so any party holding that token pair can continue to authenticate as the user indefinitely, even after the password is changed as a security response.

### Finding Description
`UserController.UpdatePassword` delegates to `updateUserPassword`, which performs exactly two actions: `orm.ClearNonCurrentSessions(ctx, sessionID)` and `orm.SetPassword(ctx, user, newPassword)`. [1](#0-0) 

The GraphQL resolver `UpdateUserPassword` follows the identical pattern. [2](#0-1) 

Neither path calls `DeleteAuthToken` or `SetAuthToken`/`CreateAndSetAuthToken`. As a result, the `token_key`/`token_hashed_secret` columns set the last time the user issued `NewAPIToken` remain unchanged. [3](#0-2) 

API token based authentication (`AuthenticateByToken`) is entirely decoupled from the password/session subsystem — it looks up the user solely by `token_key` and compares the token secret against `token_hashed_secret`, with no reference to `hashed_password` or the sessions table at all. [4](#0-3) 

This is the direct analog of the reported bug class: a credential-rotation action (password change) is expected by the user (and by the CLI prompt itself, which explicitly states "This will terminate any other sessions") to revoke prior standing access, but a parallel, still-valid authentication artifact (the API token/secret pair) is left completely untouched — exactly like OpenDaylight Karaf's stale cache continuing to accept the old password after a change. [5](#0-4) 

### Impact Explanation
If an unprivileged attacker has obtained a user's API key/secret (e.g. via log leakage, a compromised CI pipeline, a leaked config file, or a prior session), the legitimate user's remediation step of changing their password does not lock the attacker out. The attacker can continue to call any authenticated `X-API-KEY`/`X-API-SECRET` endpoint — including job/bridge management, run triggering, and (depending on role) admin-level API token/user management endpoints — indefinitely, defeating the security purpose of a password rotation. This is a direct authentication/credential-lifecycle bypass reachable by any party possessing the leaked token, without needing to compromise the current password.

### Likelihood Explanation
Likelihood is elevated because: (1) password rotation is the standard operator response to a suspected credential compromise, and users reasonably expect it to invalidate all outstanding access as advertised by the CLI's own messaging; (2) API tokens are long-lived, static secrets that are commonly persisted in scripts/CI, making them plausible artifacts to leak or need to be revoked; (3) no additional privilege or race condition is required — the attacker simply keeps using a token that was valid before the password change and remains valid after.

### Recommendation
Call `DeleteAuthToken` (or rotate/invalidate the API token) as part of `updateUserPassword` in `core/web/user_controller.go` and the equivalent `UpdateUserPassword` GraphQL resolver in `core/web/resolver/mutation.go`, so that a password change also revokes any existing API token, forcing the user to explicitly reissue one via `NewAPIToken` with the new password.

### Proof of Concept
1. As user `alice`, call `POST /v2/user/token` with the current password to obtain an API key/secret pair (`NewAPIToken` in `core/web/user_controller.go`).
2. An attacker obtains this key/secret (e.g., leaked in logs/CI).
3. `alice`, suspecting compromise, changes her password via `PATCH /v2/user/password`.
4. The attacker continues to issue requests using the previously obtained `X-API-KEY`/`X-API-SECRET` headers against any authenticated endpoint (e.g. `GET /v2/bridge_types`) — these requests still succeed because `AuthenticateByToken` never checks against the rotated password and `token_key`/`token_hashed_secret` were never cleared by the password change flow.

### Citations

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

**File:** core/web/resolver/mutation.go (L959-966)
```go
	if err = r.App.AuthenticationProvider().ClearNonCurrentSessions(ctx, session.SessionID); err != nil {
		return nil, clearSessionsError{}
	}

	err = r.App.AuthenticationProvider().SetPassword(ctx, &dbUser, args.Input.NewPassword)
	if err != nil {
		return nil, failedPasswordUpdateError{}
	}
```

**File:** core/sessions/localauth/orm.go (L331-346)
```go
// SetAuthToken updates the user to use the given Authentication Token.
func (o *orm) SetAuthToken(ctx context.Context, user *sessions.User, token *auth.Token) error {
	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(token, salt)
	if err != nil {
		return pkgerrors.Wrap(err, "user")
	}
	sql := "UPDATE users SET token_salt = $1, token_key = $2, token_hashed_secret = $3, updated_at = now() WHERE email = $4 RETURNING *"
	return o.ds.GetContext(ctx, user, sql, salt, token.AccessKey, hashedSecret, user.Email)
}

// DeleteAuthToken clears and disables the users Authentication Token.
func (o *orm) DeleteAuthToken(ctx context.Context, user *sessions.User) error {
	sql := "UPDATE users SET token_salt = '', token_key = '', token_hashed_secret = '', updated_at = now() WHERE email = $1 RETURNING *"
	return o.ds.GetContext(ctx, user, sql, user.Email)
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

**File:** core/cmd/shell.go (L1070-1073)
```go
func (c changePasswordPrompter) Prompt() (web.UpdatePasswordRequest, error) {
	fmt.Println("Changing your chainlink account password.")
	fmt.Println("NOTE: This will terminate any other sessions.")
	oldPassword := c.prompter.PasswordPrompt("Password:")
```
