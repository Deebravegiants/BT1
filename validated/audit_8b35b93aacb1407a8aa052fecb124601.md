### Title
Missing audit-log emission for API user creation, deletion, and role changes - ([File: core/web/user_controller.go])

### Summary
The `Governed`-contract event-emission gap described in the external report has a direct analog in the Chainlink node's audit-logging system: `UserController.Create`, `UserController.Delete`, and `UserController.UpdateRole` in `core/web/user_controller.go` never call `App.GetAuditLogger().Audit(...)`, even though these are exactly the kind of sensitive, privilege-affecting actions (creating an admin/API user, deleting a user, changing a user's role) that the audit logger exists to record.

### Finding Description
The audit log is Chainlink's analog to Solidity events — it is the mechanism used across the web controllers to make sensitive state changes observable to operators/off-chain monitoring. Many controllers correctly call `u.App.GetAuditLogger().Audit(...)` after sensitive changes, e.g. password reset success (`audit.PasswordResetSuccess`), API token creation/deletion (`audit.APITokenCreated`, `audit.APITokenDeleted`) in `UserController.UpdatePassword`, `NewAPIToken`, and `DeleteAPIToken` [1](#0-0) [2](#0-1) [3](#0-2) .

However, three of the most sensitive functions in the same controller — user creation, user role modification, and user deletion — return success without any audit call:
- `Create` provisions a brand-new API user with an arbitrary role (including `admin`) and never audits the action [4](#0-3) .
- `UpdateRole` elevates or downgrades a user's permission level (e.g., promoting a `view`-only user to `admin`) and never audits the action [5](#0-4) .
- `Delete` removes an API user (and all of that user's sessions) and never audits the action [6](#0-5) .

The underlying ORM-level operation for role change, `UpdateRole` in `core/sessions/localauth/orm.go`, silently purges all of the target user's sessions and rewrites their role directly in the database with no logging hook at all [7](#0-6) .

This matches the report's root-cause pattern precisely: some parts of the system (here, password reset and API-token lifecycle) received the fix from the referenced PR, while access-control-adjacent operations (user creation/deletion/role-change — the direct Go analog to `Governed`'s admin/authorization functions) were left out of the fix, exactly as the report's "Update" note states for the `Governed` contract.

### Impact Explanation
Any account with admin-level access to the node's `/v2/users` API (a legitimate admin, or an attacker who compromises admin credentials/session) can create new admin users, delete existing users, or change a user's role from `view` to `admin` (or vice versa, e.g. demoting another admin) without the action ever appearing in the audit trail. This weakens incident response and forensic capability: an attacker who escalates privileges via `UpdateRole`, plants a persistent backdoor admin account via `Create`, or removes a legitimate admin via `Delete` leaves no audit-log trace, even though the audit logger is explicitly designed to catch this class of event elsewhere in the same file. This is a detection/accountability gap rather than a direct authentication bypass, but it directly enables silent, unauditable privilege escalation and persistence for anyone who already has (or obtains) admin API access.

### Likelihood Explanation
Any admin user (or an attacker with a stolen admin session/API token) exercising the standard, always-reachable `/v2/users` endpoints will trigger this gap on every call — there is no special precondition. Given that adjacent, less-sensitive functions in the exact same file (password reset, API token issuance) do emit audit events, the omission in `Create`/`UpdateRole`/`Delete` is a straightforward, easily verified gap rather than a theoretical one.

### Recommendation
Add `u.App.GetAuditLogger().Audit(...)` calls with new audit event types (e.g. `audit.UserCreated`, `audit.UserRoleUpdated`, `audit.UserDeleted`) to `UserController.Create`, `UserController.UpdateRole`, and `UserController.Delete` in `core/web/user_controller.go`, following the same pattern already used in `UpdatePassword`, `NewAPIToken`, and `DeleteAPIToken`. Include the target email and (for `UpdateRole`) old/new role in the audit payload, and consider also logging the acting admin's identity for full traceability, consistent with the report's general recommendation to emit events/logs for all sensitive state changes.

### Proof of Concept
1. Authenticate as an existing admin user against the node's `/v2/users` API.
2. Call `PATCH /v2/users` with body `{"email":"<target>","newRole":"admin"}` — corresponding to `UserController.UpdateRole` [5](#0-4) .
3. Observe that the role change succeeds (HTTP 200, target user's sessions purged and role updated per `orm.UpdateRole` [7](#0-6) ), but no entry is written via `GetAuditLogger().Audit(...)`, unlike the equivalent flow for `POST /v2/user/token` (`NewAPIToken`) which does write `audit.APITokenCreated` [8](#0-7) .
4. Repeat with `POST /v2/users` (`Create`) and `DELETE /v2/users/:email` (`Delete`) to confirm the same absence of audit emission for account creation and deletion.

### Citations

**File:** core/web/user_controller.go (L52-106)
```go
func (u *UserController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	type newUserRequest struct {
		Email    string `json:"email"`
		Password string `json:"password"`
		Role     string `json:"role"`
	}

	var request newUserRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	userRole, err := clsession.GetUserRole(request.Role)
	if err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}

	if verr := clsession.ValidateEmail(request.Email); verr != nil {
		jsonAPIError(c, http.StatusBadRequest, verr)
		return
	}

	if verr := utils.VerifyPasswordComplexity(request.Password, request.Email); verr != nil {
		jsonAPIError(c, http.StatusBadRequest, verr)
		return
	}

	user, err := clsession.NewUser(request.Email, request.Password, userRole)
	if err != nil {
		jsonAPIError(c, http.StatusBadRequest, errors.Errorf("error creating API user: %s", err))
		return
	}
	if err = u.App.AuthenticationProvider().CreateUser(ctx, &user); err != nil {
		// If this is a duplicate key error (code 23505), return a nicer error message
		var pgErr *pgconn.PgError
		if ok := errors.As(err, &pgErr); ok {
			if pgErr.Code == "23505" {
				jsonAPIError(c, http.StatusBadRequest, errors.Errorf("user with email %s already exists", request.Email))
				return
			}
		}
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorw("Error creating new API user", "err", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("error creating API user"))
		return
	}

	jsonAPIResponse(c, presenters.NewUserResource(user), "user")
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

**File:** core/web/user_controller.go (L162-199)
```go
func (u *UserController) Delete(c *gin.Context) {
	ctx := c.Request.Context()
	email := c.Param("email")

	// Attempt find user by email
	user, err := u.App.AuthenticationProvider().FindUser(ctx, email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		jsonAPIError(c, http.StatusBadRequest, errors.Errorf("specified user not found: %s", email))
		return
	}

	// Don't allow current admin user to delete self
	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	if strings.EqualFold(sessionUser.Email, email) {
		jsonAPIError(c, http.StatusBadRequest, errors.New("can not delete currently logged in admin user"))
		return
	}

	if err = u.App.AuthenticationProvider().DeleteUser(ctx, email); err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorw("Error deleting API user", "err", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("error deleting API user"))
		return
	}

	jsonAPIResponse(c, presenters.NewUserResource(user), "user")
}
```

**File:** core/web/user_controller.go (L239-241)
```go
	u.App.GetAuditLogger().Audit(audit.PasswordResetSuccess, map[string]any{"user": user.Email})
	jsonAPIResponse(c, presenters.NewUserResource(user), "user")
}
```

**File:** core/web/user_controller.go (L274-286)
```go
	newToken := auth.NewToken()
	if err := u.App.AuthenticationProvider().SetAuthToken(ctx, &user, newToken); err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	u.App.GetAuditLogger().Audit(audit.APITokenCreated, map[string]any{"user": user.Email})
	jsonAPIResponseWithStatus(c, newToken, "auth_token", http.StatusCreated)
}
```

**File:** core/web/user_controller.go (L327-329)
```go
		u.App.GetAuditLogger().Audit(audit.APITokenDeleted, map[string]any{"user": user.Email})
		jsonAPIResponseWithStatus(c, nil, "auth_token", http.StatusNoContent)
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
