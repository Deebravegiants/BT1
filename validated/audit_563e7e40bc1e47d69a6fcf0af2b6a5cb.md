### Title
Missing audit-log events for user creation, deletion, and role change - ([File: core/web/user_controller.go])

### Summary
Chainlink's off-chain analog to Solidity event emission is the `AuditLogger` (`u.App.GetAuditLogger().Audit(...)`), used throughout `core/web` controllers to record sensitive state changes for compliance/monitoring/SIEM ingestion. In `core/web/user_controller.go`, the `Create`, `UpdateRole`, and `Delete` handlers for the `UserController` — which create new API users, change an existing user's privilege role, and delete API users, respectively — perform their sensitive mutations without ever calling `Audit(...)`, unlike the sibling handlers `UpdatePassword`, `NewAPIToken`, and `DeleteAPIToken` in the same file, which consistently emit audit events (`audit.PasswordResetSuccess`, `audit.APITokenCreated`, `audit.APITokenDeleted`, etc.).

### Finding Description
`UserController.Create` [1](#0-0)  calls `u.App.AuthenticationProvider().CreateUser(ctx, &user)` to persist a brand-new API user (with an attacker/administrator-chosen role, including `admin`) but never logs the action via the `AuditLogger`.

`UserController.UpdateRole` [2](#0-1)  calls `u.App.AuthenticationProvider().UpdateRole(ctx, request.Email, request.NewRole)` — a privilege-escalation-relevant operation that can promote or demote any other user's role (e.g., to `admin`) — but the handler returns the updated resource without emitting any audit event.

`UserController.Delete` [3](#0-2)  removes an API user account entirely and also does not emit an audit event.

By contrast, every other sensitive mutation in the same controller does emit an audit record: `UpdatePassword` logs `audit.PasswordResetAttemptFailedMismatch`/`audit.PasswordResetSuccess` [4](#0-3) , and API token issuance/revocation log `audit.APITokenCreated`/`audit.APITokenDeleted` [5](#0-4) [6](#0-5) . This inconsistency mirrors the reported bug class: sensitive state-changing operations (ownership/role changes, account creation/removal) silently execute without generating the notification trail that off-chain monitors rely on.

### Impact Explanation
Loss of audit trail for user role changes and account lifecycle events (`Create`/`Delete`) undermines detection of unauthorized privilege escalation or account tampering. If credentials to the admin API are compromised or an insider abuses access, granting themselves/another account `admin` role via `UpdateRole`, or creating a new hidden `admin` account via `Create`, or removing accounts via `Delete`, would leave no entry in the audit log stream that security teams use for incident detection and forensic reconstruction — while password resets and API token changes for the very same users would be logged. This is a monitoring/detection gap, not a direct authentication or fund-movement bypass.

### Likelihood Explanation
These endpoints (`/v2/users` `POST`/`PATCH`/`DELETE`) are only reachable by already-authenticated, privileged (`admin`) users per the router configuration, so exploitation requires an admin-level session or credential compromise. However, that is exactly the threat model audit logs are meant to cover (detecting misuse by a compromised or malicious insider admin account), so the likelihood of this gap mattering in a real incident is moderate.

### Recommendation
Add `u.App.GetAuditLogger().Audit(...)` calls in `UserController.Create`, `UserController.UpdateRole`, and `UserController.Delete`, following the existing pattern used in `UpdatePassword`/`NewAPIToken`/`DeleteAPIToken`. Introduce new audit event types (e.g., `audit.UserCreated`, `audit.UserRoleUpdated`, `audit.UserDeleted`) in `core/logger/audit/audit_types.go`, and log the affected user's email and (for `UpdateRole`) old/new role values, plus the acting admin's identity where available.

### Proof of Concept
1. Authenticate as an admin user.
2. `PATCH /v2/users` with `{"email": "<victim>@example.com", "newRole": "admin"}` — the role is silently escalated via `UpdateRole` [7](#0-6)  with no corresponding audit record, unlike a concurrent password reset for the same user which would produce an `audit.PasswordResetSuccess` entry.
3. `POST /v2/users` to create a new hidden admin account, or `DELETE /v2/users/:email` to remove an account — both complete without any audit log entry, in contrast to `NewAPIToken`/`DeleteAPIToken` on the same controller.
4. Inspect the audit log stream (as configured via `AuditLogger`) to confirm no entries were emitted for any of the three operations, verifying the detection gap.

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

**File:** core/web/user_controller.go (L161-199)
```go
// Delete deletes an API user and any sessions by email
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

**File:** core/web/user_controller.go (L225-240)
```go
	if !utils.CheckPasswordHash(request.OldPassword, string(user.HashedPassword)) {
		u.App.GetAuditLogger().Audit(audit.PasswordResetAttemptFailedMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusConflict, errors.New("old password does not match"))
		return
	}
	if err := utils.VerifyPasswordComplexity(request.NewPassword, user.Email); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
	if err := u.updateUserPassword(c, &user, request.NewPassword); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	u.App.GetAuditLogger().Audit(audit.PasswordResetSuccess, map[string]any{"user": user.Email})
	jsonAPIResponse(c, presenters.NewUserResource(user), "user")
```

**File:** core/web/user_controller.go (L270-284)
```go
		u.App.GetAuditLogger().Audit(audit.APITokenCreateAttemptPasswordMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusUnauthorized, errors.New("incorrect password"))
		return
	}
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
```

**File:** core/web/user_controller.go (L312-328)
```go
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
```
