### Title
GraphQL `updateUserPassword` mutation allows setting an empty/weak password with no complexity validation - ([File: core/web/resolver/mutation.go])

### Summary
The GraphQL mutation resolver `Resolver.UpdateUserPassword` in `core/web/resolver/mutation.go` accepts a new password and passes it directly to `SetPassword` without ever calling `utils.VerifyPasswordComplexity` (or any other server-side validation). This mirrors the CVE-2025-63800 bug class — a password-change endpoint that omits validation, letting an authenticated user set an effectively unusable/empty password and potentially self-lock or weaken the account.

### Finding Description
The REST endpoint `UserController.UpdatePassword` correctly validates the new password's complexity before persisting it: [1](#0-0) 

However, the GraphQL equivalent, `Resolver.UpdateUserPassword`, only verifies the *old* password matches, then calls `ClearNonCurrentSessions` and `SetPassword` directly with `args.Input.NewPassword` — with no call to `utils.VerifyPasswordComplexity` or `sessions.ValidateAndHashPassword`: [2](#0-1) 

The GraphQL schema only enforces `newPassword: String!` (non-null), which does not prevent an empty string: [3](#0-2) 

The underlying `SetPassword` implementation for the local auth provider performs no complexity or emptiness check either — it simply hashes and stores whatever value is given: [4](#0-3) 

Password complexity (including a minimum 16-character length requirement, which alone rejects empty strings) is only enforced via `utils.VerifyPasswordComplexity`, defined once and expected to be invoked at every password-setting call site: [5](#0-4) 

Compare this to `ValidateAndHashPassword`, the intended "single point of logic for user password validations" used elsewhere (e.g. user creation): [6](#0-5) 

The GraphQL password-change path bypasses this single point of validation entirely.

### Impact Explanation
An authenticated node operator user (of any role) can call the `updateUserPassword` GraphQL mutation with `newPassword: ""` (or any short/weak string) after supplying their correct current password. The backend will accept it, clear other sessions, and persist an effectively empty/trivial password hash. This weakens account authentication and could facilitate account takeover or accidental lockout, directly matching the CVE's core issue: a password-change endpoint that silently accepts empty/weak passwords due to missing server-side validation.

### Likelihood Explanation
High likelihood of exploitation is straightforward: any authenticated user (regardless of role) reaching the GraphQL API can trigger this with a single mutation call once they know their own current password — no special privilege escalation or race condition needed.

### Recommendation
Add the same complexity validation used in the REST controller to the GraphQL resolver — call `utils.VerifyPasswordComplexity(args.Input.NewPassword, dbUser.Email)` (or reuse `sessions.ValidateAndHashPassword`) in `Resolver.UpdateUserPassword` before invoking `SetPassword`, and return an `InputErrors` payload on failure to match the REST behavior.

### Proof of Concept
1. Authenticate as any existing user (role `view`/`edit`/`admin`) and obtain a valid session.
2. Send the GraphQL mutation:
```graphql
mutation {
  updateUserPassword(input: { oldPassword: "<correctCurrentPassword>", newPassword: "" }) {
    ... on UpdatePasswordSuccess { user { email } }
    ... on InputErrors { errors { path message code } }
  }
}
```
3. Observe the mutation succeeds (`UpdatePasswordSuccess`) and the account password is now an empty string in the database, whereas the equivalent REST call `PATCH /v2/user/password` with the same body returns `422 Unprocessable Entity` due to `VerifyPasswordComplexity` rejecting the short/empty password (see `core/web/user_controller_test.go` lines 49-55 for the REST-side rejection behavior — `core/web/user_controller_test.go:49-55`).

### Citations

**File:** core/web/user_controller.go (L225-237)
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

**File:** core/web/schema/type/user.graphql (L6-9)
```text
input UpdatePasswordInput {
    oldPassword: String!
    newPassword: String!
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

**File:** core/sessions/user.go (L68-83)
```go
// ValidateAndHashPassword is the single point of logic for user password validations
func ValidateAndHashPassword(plainPwd string) (string, error) {
	if err := utils.VerifyPasswordComplexity(plainPwd); err != nil {
		return "", pkgerrors.Wrapf(err, "password insufficiently complex:\n%s", utils.PasswordComplexityRequirements)
	}
	if len(plainPwd) > MaxBcryptPasswordLength {
		return "", pkgerrors.Errorf("must enter a password less than %v characters", MaxBcryptPasswordLength)
	}

	pwd, err := utils.HashPassword(plainPwd)
	if err != nil {
		return "", err
	}

	return pwd, nil
}
```
