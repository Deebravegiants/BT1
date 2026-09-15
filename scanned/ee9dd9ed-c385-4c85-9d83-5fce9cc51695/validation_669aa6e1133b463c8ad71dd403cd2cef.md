Confirmed: `VerifyPasswordComplexity` is never called in `core/web/resolver/mutation.go`, and the GraphQL `UpdateUserPassword` mutation calls `SetPassword` directly, bypassing the complexity check enforced in the REST `UserController.UpdatePassword` path. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
GraphQL `UpdateUserPassword` mutation bypasses password complexity validation enforced elsewhere - (File: core/web/resolver/mutation.go)

### Summary
The `TelcoinDistributor` report describes a setter (`setChallengePeriod`) that omits a validation check that the constructor enforces, allowing an invariant to be silently broken through an alternate code path. The Chainlink analog is `Resolver.UpdateUserPassword` in `core/web/resolver/mutation.go`, which sets a new user password via `AuthenticationProvider().SetPassword` without ever invoking `utils.VerifyPasswordComplexity`, even though the equivalent REST endpoint (`UserController.UpdatePassword`) and user creation path (`UserController.Create`, `sessions.NewUser`/`ValidateAndHashPassword`) both enforce this check.

### Finding Description
Password complexity is treated as a security invariant across the codebase: user creation (`sessions.ValidateAndHashPassword` in `core/sessions/user.go`) and REST password updates (`UserController.UpdatePassword` in `core/web/user_controller.go`) both call `utils.VerifyPasswordComplexity` before persisting a new password.

However, the underlying data-layer setter `orm.SetPassword` (`core/sessions/localauth/orm.go`) performs no complexity validation itself — it relies entirely on callers to validate beforehand, just like `TelcoinDistributor`'s `setChallengePeriod` relies on callers to avoid a zero value that only the constructor checked.

The GraphQL mutation `Resolver.UpdateUserPassword` in `core/web/resolver/mutation.go` is one such caller. It authenticates the user, verifies the old password, clears other sessions, and calls `SetPassword` directly with `args.Input.NewPassword` — with no call to `utils.VerifyPasswordComplexity` anywhere in this function or its dependencies. This means any authenticated user (via the API/UI GraphQL endpoint, requires any authenticated role) can set an arbitrarily weak password (e.g., a single character), completely bypassing the length/whitespace/email-exclusion requirements enforced by the REST-facing surface.

### Impact Explanation
An authenticated node operator user (of any role, since the mutation only requires `authenticateUser`) can weaken their own account's password to a trivial value through the GraphQL API, defeating the password strength policy that the project explicitly documents and enforces elsewhere. This undermines brute-force resistance for that user's session/API credentials and is inconsistent with the security assumption that all Chainlink node users have passwords meeting `utils.PasswordComplexityRequirements`.

### Likelihood Explanation
High likelihood: this is directly reachable by any authenticated user through the standard GraphQL mutation surface with no additional privilege required — the only "attacker" precondition is knowing the current password, which is trivially the case for a legitimate user weakening their own credentials.

### Recommendation
Add a `utils.VerifyPasswordComplexity(args.Input.NewPassword, dbUser.Email)` call (mirroring `UserController.UpdatePassword`) in `Resolver.UpdateUserPassword` before calling `SetPassword`, and return a structured input error (as the REST path does) rather than proceeding to update the password. Consider centralizing the complexity check inside `SetPassword` itself so all callers are protected uniformly, consistent with defense-in-depth and how the Sherlock report recommended enforcing the invariant at the setter level.

### Proof of Concept
1. Log in as any user with any role via GraphQL authentication.
2. Call the `updatePassword` GraphQL mutation with `oldPassword` set to the correct current password and `newPassword` set to a trivially weak value, e.g. `"a"`.
3. Observe that `Resolver.UpdateUserPassword` proceeds without calling `utils.VerifyPasswordComplexity`, and `SetPassword` succeeds, storing the hash of `"a"` as the new password — contrast with attempting the same weak password via the REST `PATCH /v2/user/password` endpoint, which is correctly rejected with a complexity error.

### Citations

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

**File:** core/web/user_controller.go (L201-233)
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
