### Title
Missing audit-event emission on sensitive API-user account changes (create, role change, delete) - ([File: core/web/user_controller.go])

### Summary
`UserController.Create`, `UserController.UpdateRole`, and `UserController.Delete` in `core/web/user_controller.go` perform sensitive account-management actions (creating an API user with an assigned role, changing an existing API user's privilege role, and deleting an API user) but never write an audit-log entry on success. This is inconsistent with the rest of the same controller, which does emit audit events for comparably or less sensitive actions (`PasswordResetSuccess`, `APITokenCreated`, `APITokenDeleted`, and the failed-attempt variants).

### Finding Description
The `UserController` handles node administrator/API-user management via `/v2/users` endpoints. Looking at the controller:

- `Create` (core/web/user_controller.go:52-106) creates a new API user with a caller-specified `Role` (admin/edit/run/view) via `u.App.AuthenticationProvider().CreateUser(ctx, &user)`, but no `u.App.GetAuditLogger().Audit(...)` call follows a successful creation. [1](#0-0) 

- `UpdateRole` (core/web/user_controller.go:109-159) changes an existing user's role — a privilege-escalation/de-escalation action — via `u.App.AuthenticationProvider().UpdateRole(ctx, request.Email, request.NewRole)`, but again no audit event is emitted on success. [2](#0-1) 

- `Delete` (core/web/user_controller.go:162-199) removes an API user account via `u.App.AuthenticationProvider().DeleteUser(ctx, email)`, again with no audit event on success. [3](#0-2) 

By contrast, in the very same file, `UpdatePassword` and `NewAPIToken`/`DeleteAPIToken` — arguably less impactful than a full role change or account creation/removal — do emit audit events both on failure and success: [4](#0-3) [5](#0-4) [6](#0-5) 

This mirrors the exact bug class from the report: sensitive state-changing operations (analogous to `ClaimsManager`'s `setGovernanceAddress`/`setStakingAddress`, or `ServiceProviderFactory`'s `updateDelegateOwnerWallet`) silently succeed without any tamper-evident record. Here the sensitive actions are role/account changes reachable via the node's admin HTTP API (`ExternalInitiatorsController.Create`, in the same package, correctly does emit `audit.ExternalInitiatorCreated` for comparison, confirming the audit logger is the established pattern for this class of change and was simply omitted here). [7](#0-6) 

### Impact Explanation
If an admin-role credential is compromised (or a malicious/compromised admin misuses their access), they can create new API users with arbitrary roles, promote/demote any other user's privilege role, or delete accounts — all without producing any audit trail. This undermines forensic detection of unauthorized privilege escalation or account tampering, and operators relying on the audit log for security monitoring/compliance will have a blind spot specifically around user/role lifecycle management, the most security-critical category of admin actions.

### Likelihood Explanation
Low technical likelihood of exploitation by itself since these endpoints already require admin-role authentication (`AuthenticateByToken`/`AuthenticateBySession` with `UserRoleAdmin` enforced by router middleware, not shown here but implied by admin-only route wiring). However, the missing logging is unconditionally triggered on every legitimate or illegitimate use of these three endpoints — it is not a rare edge case — so any misuse of an admin credential (via phishing, leaked API token, insider threat) related to user/role management will go unrecorded with certainty.

### Recommendation
Add `u.App.GetAuditLogger().Audit(...)` calls after each successful sensitive operation in `core/web/user_controller.go`:
- After successful `CreateUser` in `Create`, e.g. `audit.APIUserCreated` with `{"email": user.Email, "role": user.Role}`.
- After successful `UpdateRole` in `UpdateRole`, e.g. `audit.APIUserRoleUpdated` with `{"email": request.Email, "newRole": request.NewRole}`.
- After successful `DeleteUser` in `Delete`, e.g. `audit.APIUserDeleted` with `{"email": email}`.

These new audit event type constants should be added to `core/logger/audit/audit_types.go` alongside the existing `APITokenCreated`/`APITokenDeleted`/`PasswordResetSuccess` constants, following the same pattern already used for `ExternalInitiatorCreated`.

### Proof of Concept
1. Authenticate as an admin-role user.
2. `POST /v2/users` with `{"email":"attacker@example.com","password":"...","role":"admin"}` → new admin user created; no audit log entry produced (verify via `AuditLogger` output / audit log file, which only contains entries for password-reset/API-token flows, never for this call). Reference: `UserController.Create` at [1](#0-0) .
3. `PATCH /v2/users` with `{"email":"victim@example.com","newRole":"admin"}` → victim's role silently escalated to admin, no audit entry. Reference: `UserController.UpdateRole` at [2](#0-1) .
4. `DELETE /v2/users/victim@example.com` → account removed, no audit entry. Reference: `UserController.Delete` at [3](#0-2) .
5. Compare against `POST /v2/external_initiators`, which does correctly produce an `audit.ExternalInitiatorCreated` entry, confirming the omission is specific to the user-management handlers. Reference: [7](#0-6) .

### Citations

**File:** core/web/user_controller.go (L82-106)
```go
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

**File:** core/web/user_controller.go (L142-159)
```go
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

**File:** core/web/user_controller.go (L188-199)
```go
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

**File:** core/web/user_controller.go (L225-239)
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
```

**File:** core/web/user_controller.go (L268-285)
```go
	err = u.App.AuthenticationProvider().TestPassword(ctx, sessionUser.Email, request.Password)
	if err != nil {
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
	jsonAPIResponseWithStatus(c, newToken, "auth_token", http.StatusCreated)
```

**File:** core/web/user_controller.go (L312-329)
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
	}
```

**File:** core/web/external_initiators_controller.go (L87-97)
```go
	if err := eic.App.BridgeORM().CreateExternalInitiator(ctx, ei); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	eic.App.GetAuditLogger().Audit(audit.ExternalInitiatorCreated, map[string]any{
		"externalInitiatorID":   ei.ID,
		"externalInitiatorName": ei.Name,
		"externalInitiatorURL":  ei.URL,
	})

```
