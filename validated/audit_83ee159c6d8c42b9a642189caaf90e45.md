Based on the investigation, both password-change code paths in this repo already validate old vs. new password state — they just don't explicitly reject `newPassword == oldPassword`. Let me confirm there's no explicit "same password" check anywhere.Confirmed: neither `UserController.UpdatePassword` (REST, `core/web/user_controller.go`) nor `UpdateUserPassword` (GraphQL, `core/web/resolver/mutation.go`) nor `VerifyPasswordComplexity` (`core/utils/password.go`) contains any check that rejects `NewPassword == OldPassword`. Both flows: verify old password hash matches → check complexity/length rules → call `SetPassword`, with no equality comparison between old and new password anywhere in the chain.

### Title
Unverified Password Reuse Allows Setting Old Password as New Password - (File: core/web/user_controller.go)

### Summary
The authenticated password-change endpoint `/v2/user/password` (`UserController.UpdatePassword`) and its GraphQL equivalent `UpdateUserPassword` accept a `NewPassword` identical to `OldPassword` without rejection, mirroring the CWE-287/CWE-620 class in the pimcore advisory (old password can be set as new password, violating password policy).

### Finding Description
`UserController.UpdatePassword` in [1](#0-0)  verifies `request.OldPassword` against the stored hash via `utils.CheckPasswordHash`, then only runs `utils.VerifyPasswordComplexity(request.NewPassword, user.Email)` before calling `u.updateUserPassword(c, &user, request.NewPassword)`. `VerifyPasswordComplexity`, defined in [2](#0-1)  only checks length, leading/trailing whitespace, and disallowed substrings (e.g. the user's email) — it never compares `NewPassword` to `OldPassword`. The identical pattern exists in the GraphQL resolver `UpdateUserPassword` at [3](#0-2) , which checks the hash match at line 951 and then unconditionally calls `SetPassword` with the new value with no equality guard. Both `localauth.orm.SetPassword` ( [4](#0-3) ) and the LDAP/OIDC local-admin `SetPassword` fallbacks unconditionally hash and persist whatever value is supplied, with no server-side rejection of "new == old".

### Impact Explanation
This is a low-impact policy weakness, not a bypass of authentication or an unauthorized state change: the request still requires the current session to be authenticated and the correct old password to be supplied. The impact is limited to violating a password-hygiene expectation (a user, or someone with the current password who intends to defeat a forced-rotation/breach-response policy, can "change" the password to the same value). No privilege escalation, credential disclosure, or cross-user impact is possible.

### Likelihood Explanation
High likelihood of the behavior occurring given normal usage (any authenticated user submitting `oldPassword == newPassword` triggers it), but the security-relevant consequence only matters in threat models that rely on forced password rotation (e.g., post-incident credential reset) — a scenario chainlink does not appear to formally support (there's no "force reset" flag in the `User` model or session flow found in this codebase).

### Recommendation
Add an explicit equality check between `request.OldPassword`/`args.Input.NewPassword` and `args.Input.OldPassword` and the current password before calling `SetPassword`, returning a validation error (mirroring the `"oldPassword does not match"` pattern) when they are equal, in both `UserController.UpdatePassword` (`core/web/user_controller.go`) and `Resolver.UpdateUserPassword` (`core/web/resolver/mutation.go`).

### Proof of Concept
1. Authenticate as any local user and obtain a valid session/cookie.
2. `PATCH /v2/user/password` with body `{"oldPassword": "<currentPassword>", "newPassword": "<currentPassword>"}`.
3. Observe `200 OK` and `"Password updated."` — the password is unchanged but the operation succeeds as if a rotation occurred, as validated by the existing test case `TestUserController_UpdatePassword` "Success" case at [5](#0-4)  which uses the same value for both fields and expects `http.StatusOK`.

### Citations

**File:** core/web/user_controller.go (L201-241)
```go
// UpdatePassword changes the password for the current User.
func (u *UserController) UpdatePassword(c *gin.Context) {
	ctx := c.Request.Context()
	var request UpdatePasswordRequest
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
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to update password"))
		return
	}
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
}
```

**File:** core/utils/password.go (L44-70)
```go
func VerifyPasswordComplexity(password string, disallowedStrings ...string) (merr error) {
	errMsg := ErrMsgHeader
	var stringErrs []string

	if LeadingWhitespace.MatchString(password) || TrailingWhitespace.MatchString(password) {
		stringErrs = append(stringErrs, ErrWhitespace.Error())
	}

	if len(password) < MinRequiredLen {
		stringErrs = append(stringErrs, fmt.Sprintf("password is less than %d characters long", MinRequiredLen))
	}

	for _, s := range disallowedStrings {
		if strings.Contains(strings.ToLower(password), strings.ToLower(s)) {
			stringErrs = append(stringErrs, fmt.Sprintf("password may not contain: %q", s))
		}
	}

	if len(stringErrs) > 0 {
		for _, stringErr := range stringErrs {
			errMsg = fmt.Sprintf("%s	%s\n", errMsg, stringErr)
		}
		merr = errors.New(errMsg)
	}

	return
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

**File:** core/web/user_controller_test.go (L64-67)
```go
			name:           "Success",
			reqBody:        fmt.Sprintf(`{"newPassword": "%v", "oldPassword": "%v"}`, cltest.Password, cltest.Password),
			wantStatusCode: http.StatusOK,
		},
```
