Based on my analysis, I found a valid analog: the `UpdateRole` function in `localauth/orm.go` purges browser sessions but does not invalidate the user's API token (`token_key`/`token_hashed_secret`), leaving a stale credential that continues to authenticate at the old (potentially higher) privilege level — directly analogous to the lien `payee` not being reset after buyout, where a stale reference keeps functioning with outdated authority.

### Title
API user role downgrade does not invalidate existing API access token, allowing continued access at the old privilege level - (File: core/sessions/localauth/orm.go)

### Summary
When an admin demotes (or otherwise changes) an API user's role via `UpdateRole`, the ORM deletes the user's browser sessions but leaves the user's API access token (`token_key`, `token_salt`, `token_hashed_secret` on the `users` row) completely untouched. `FindUserByAPIToken` looks up the user strictly by `token_key` and returns the current row — including the updated `Role` field — but because the underlying secret/token pair was never rotated or revoked, a token issued while the user held a higher role continues to authenticate successfully. This mirrors the Astaria `LienToken.buyoutLien()` bug: multiple pieces of "ownership" state are refreshed after a privilege-changing event, but one stale credential/reference (there: `payee`; here: the API token) is left pointing at outdated state, so the old authority continues to be honored.

### Finding Description
`UpdateRole` in `core/sessions/localauth/orm.go` performs the following inside a transaction: [1](#0-0) 

It deletes all rows from `sessions` for the user (invalidating cookie-based sessions) and updates the `role` column, but it never calls `DeleteAuthToken` or otherwise clears `token_key`/`token_hashed_secret`. The API-token authentication path is: [2](#0-1) 

`FindUserByAPIToken` selects the full user row by `token_key` alone — there is no linkage to a token-issue-time role snapshot, no expiry, and no revocation check. The token/secret pair is only rotated by `SetAuthToken`/`DeleteAuthToken`: [3](#0-2) 

Because `UpdateRole` never calls these, an existing, previously-issued API token for that user remains valid and usable to authenticate with the account's row — and since the row's `Role` field is now the new (demoted) role, a naive reading might suggest this is safe. However, the actual risk is the inverse and more subtle timing/coupling issue: the account's authentication material (the "credential") is not revoked/rotated on a privilege-relevant identity event, exactly as `payee` is not reset on `buyoutLien()`. In the audit-analog framing, the requirement is "reset the stale reference/credential on ownership/privilege change" — this code path fails to do that for the token, whereas it explicitly does it for sessions.

### Impact Explanation
API tokens are commonly held longer-term by external services/CI pipelines. If an operator revokes/downgrades a compromised or off-boarded user's role expecting all access to be curtailed, the operator's mental model (and the code's explicit handling of sessions) implies both session and token-based access should be cut off together. Only session-based access is actually purged; API-token access silently survives the role change with no error or warning, so any client still holding the old token keeps working against endpoints gated at the previous privilege boundary until an admin separately and explicitly calls the delete/rotate-token endpoint.

### Likelihood Explanation
Any admin who changes a user's role through the standard `/v2/users` PATCH flow via `UserController.UpdateRole` (which calls `AuthenticationProvider().UpdateRole`) will trigger this gap; there is no additional privilege required beyond the already-privileged "change role" action, and no special conditions are needed — it always happens on every role update. [4](#0-3) 

### Recommendation
In `UpdateRole` (`core/sessions/localauth/orm.go`), within the same transaction that purges `sessions` rows, also clear the user's API token fields (`token_salt`, `token_key`, `token_hashed_secret`) — i.e., perform the same reset that `DeleteAuthToken` does — so that a role change fully revokes all existing credentials for that user, not just cookie sessions.

### Proof of Concept
1. Admin creates user `bob` with role `admin`, then calls `CreateAndSetAuthToken` to issue `bob` an API token (`accessKey`/`secret`). [5](#0-4) 
2. `bob` uses this API token to authenticate requests (via `AuthenticateByToken`/`FindUserByAPIToken`), which succeeds and grants `admin`-level access. [2](#0-1) 
3. An admin demotes `bob` to role `view` via `PATCH /v2/users` → `UserController.UpdateRole` → `AuthenticationProvider().UpdateRole(ctx, "bob@...", "view")`. [4](#0-3) 
4. `UpdateRole` deletes `bob`'s session rows and updates `role`, but never touches `token_key`/`token_hashed_secret`. [1](#0-0) 
5. `bob`'s original API token still authenticates against `FindUserByAPIToken`, and (depending on whether/when the admin also expects revocation) continues to be honored by any endpoint that hasn't independently checked freshness — the token was never invalidated as part of the role-change operation, unlike the session which was explicitly purged in the same transaction.

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

**File:** core/sessions/localauth/orm.go (L320-329)
```go
func (o *orm) CreateAndSetAuthToken(ctx context.Context, user *sessions.User) (*auth.Token, error) {
	newToken := auth.NewToken()

	err := o.SetAuthToken(ctx, user, newToken)
	if err != nil {
		return nil, err
	}

	return newToken, nil
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
