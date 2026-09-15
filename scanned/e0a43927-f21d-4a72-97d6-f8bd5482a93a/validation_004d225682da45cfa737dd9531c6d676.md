### Title
Any Single Admin Account Can Take Over the Node's Trusted Admin Group by Deleting or Demoting All Other Admins - (File: `core/web/user_controller.go`)

### Summary
The Chainlink node's API user management treats all `admin`-role accounts as an equally-privileged flat trust group, exactly analogous to the `Trust.isTrusted` mapping in the referenced report. There is no higher-level "owner" authority above the `admin` role. Once any single account with the `admin` role is compromised or turns malicious, it can call `UpdateRole`/`Delete` on every other user — including every other admin — while only being blocked from touching its *own* account. This lets one bad or stolen admin credential unilaterally seize exclusive control over the node's entire trusted-user group.

### Finding Description
The `UserController.UpdateRole` and `UserController.Delete` handlers only protect the *currently authenticated* admin from modifying/deleting themselves — they impose no restriction on modifying or deleting *other* admin accounts: [1](#0-0) [2](#0-1) 

Both endpoints are gated only by `RequiresAdminRole`, which merely checks `user.Role == UserRoleAdmin` — it does not distinguish between a "root"/owner admin and any other admin that was later granted the role: [3](#0-2) 

The CLI equivalents (`chainlink admin users chrole` / `chainlink admin users delete`) hit the same unauthenticated-by-hierarchy endpoints: [4](#0-3) 

Because any admin can call `PATCH /v2/users` (demote another admin to `view`) or `DELETE /v2/users/:email` (delete another admin outright) for *any other* account, a single malicious or compromised admin can iterate through the full user list (via `GET /v2/users`, i.e. `UserController.Index`) and either demote or delete every other admin, leaving itself as the sole trusted account — the exact "single trusted account takeover" pattern described in the bug report, just implemented as Chainlink's local-auth RBAC instead of Solidity's `Trust.sol`.

### Impact Explanation
An attacker with a single compromised/malicious admin credential (this could arise via phishing, leaked API token, or an insider) can permanently lock out all legitimate operators from the node's Operator UI/API by demoting or deleting their accounts. Once in exclusive control, the attacker can manage bridges, external initiators, job specs, keys, and other admin-only functionality (`core/web/auth/auth_test.go` route table shows `/v2/users`, `/v2/bridge_types`, `/v2/keys/*`, `/v2/external_initiators` all admin/edit gated) without any competing trusted party able to intervene, revoke the attacker, or recover access — a direct availability/control-takeover impact on node administration.

### Likelihood Explanation
Likelihood is moderate: it requires an attacker to already control (or have had granted) one admin-level account — the same "external requirement" caveat the original judge used to downgrade severity to Medium. No cryptographic or database-level control is bypassed; the flaw is a pure authorization-design gap (flat admin trust with no owner hierarchy), so once the precondition (a rogue/compromised admin) is met, exploitation is a couple of ordinary authenticated API calls (`GET /v2/users` then `PATCH`/`DELETE` per other admin).

### Recommendation
Introduce a hierarchy above the flat `admin` role — e.g., a distinguished "owner"/"root" account (analogous to Rari Capital's `Auth.sol` owner pattern cited in the report) that is the only account allowed to create/demote/delete other `admin`-role users, while regular admins can manage `edit`/`run`/`view` users but not peer admins. Alternatively, require multi-admin approval (or at minimum audit-log alerting plus a cannot-demote-the-last-N-admins safeguard) before an admin action can remove or demote another `admin` account, preventing any single admin from unilaterally reducing the trusted admin group to just themselves.

### Proof of Concept
1. Attacker obtains valid session/API token for `admin_A` (compromise, phishing, or insider grant).
2. Attacker calls `GET /v2/users` (`UserController.Index`) to enumerate all other users, including other `admin`s (`admin_B`, `admin_C`, ...).
3. For each other admin, attacker calls `DELETE /v2/users/{email}` (`UserController.Delete`) — this succeeds because the only self-check is `strings.EqualFold(sessionUser.Email, email)`, which does not fire for other accounts: [5](#0-4) 
4. Alternatively, attacker calls `PATCH /v2/users` with `{"email": "admin_B@x.com", "newRole": "view"}` (`UserController.UpdateRole`) to strip admin rights from every other admin, again bypassed only for self: [6](#0-5) 
5. After iterating over all other admins, `admin_A` is the sole remaining trusted admin account, with full unilateral control over the node — mirroring the reported `Trust.setIsTrusted` takeover scenario.

### Citations

**File:** core/web/user_controller.go (L108-158)
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
```

**File:** core/web/user_controller.go (L177-196)
```go
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
```

**File:** core/web/auth/auth.go (L236-253)
```go
// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```

**File:** core/cmd/admin_commands.go (L108-136)
```go
				{
					Name:   "chrole",
					Usage:  "Changes an API user's role",
					Action: s.ChangeRole,
					Flags: []cli.Flag{
						cli.StringFlag{
							Name:     "email",
							Usage:    "email of user to be edited",
							Required: true,
						},
						cli.StringFlag{
							Name:     "new-role, newrole",
							Usage:    "new permission level role to set for user. Options: 'admin', 'edit', 'run', 'view'.",
							Required: true,
						},
					},
				},
				{
					Name:   "delete",
					Usage:  "Delete an API user",
					Action: s.DeleteUser,
					Flags: []cli.Flag{
						cli.StringFlag{
							Name:     "email",
							Usage:    "Email of API user to delete",
							Required: true,
						},
					},
				},
```
