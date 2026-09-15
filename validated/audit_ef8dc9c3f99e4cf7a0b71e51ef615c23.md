This confirms the claim: `Resolver.UpdateUserPassword` in `core/web/resolver/mutation.go` performs old-password verification and then calls `SetPassword` directly with `args.Input.NewPassword`, with no complexity check anywhere in the function.All code citations in the report are confirmed accurate. `core/web/user_controller.go` L230-233 enforces `utils.VerifyPasswordComplexity` before persisting the new password, while `core/web/resolver/mutation.go` L934-970 (`Resolver.UpdateUserPassword`) has no equivalent call and goes straight from the old-password check to `SetPassword`, which itself performs no validation (`core/sessions/localauth/orm.go` L298-306). This is a genuine inconsistency reachable by any authenticated session via the GraphQL API, with no admin/operator/host access required, and it degrades the node's password policy for an in-scope authentication-adjacent security control.

Audit Report

## Title
GraphQL password-change mutation bypasses password complexity requirements - (File: core/web/resolver/mutation.go)

## Summary
The GraphQL `updateUserPassword` mutation, resolved by `Resolver.UpdateUserPassword`, allows an authenticated user to set an arbitrarily weak new password (empty, single character, containing their own email, etc.) because it never calls `utils.VerifyPasswordComplexity`, unlike the equivalent REST endpoint `UserController.UpdatePassword`.

## Finding Description
`UserController.UpdatePassword` validates the old password and then explicitly calls `utils.VerifyPasswordComplexity(request.NewPassword, user.Email)` before persisting the new password [1](#0-0) . `utils.VerifyPasswordComplexity` enforces a 16-50 character minimum, rejects leading/trailing whitespace, and rejects passwords containing the user's email [2](#0-1) .

In contrast, `Resolver.UpdateUserPassword` authenticates the session, verifies the old password, clears non-current sessions, and then calls `SetPassword` directly with `args.Input.NewPassword` — with no call to `utils.VerifyPasswordComplexity` or any other strength check anywhere in the function [3](#0-2) . `SetPassword` in the local-auth ORM performs no validation of its own; it simply hashes and stores whatever string it receives [4](#0-3) .

A repo-wide search confirms `utils.VerifyPasswordComplexity` is only referenced in `core/utils/password_test.go`, `core/web/user_controller.go`, `core/cmd/key_store_authenticator.go`, `core/config/toml/types.go`, `core/sessions/user.go`, and its own definition in `core/utils/password.go` — `core/web/resolver/mutation.go` is absent, confirming the GraphQL password-change path bypasses the complexity enforcement present on the REST path.

## Impact Explanation
Any authenticated Chainlink node user (the mutation only requires `authenticateUser`, not an admin role) can set their own account password to an empty string or a trivially guessable value via the GraphQL API, undermining the node's password policy that is otherwise enforced at user creation and via the REST password-change endpoint. This weakens account security and materially increases exposure to credential-stuffing or brute-force account takeover for accounts that can control job specs, bridges, and other sensitive node operations exposed over the node's API — an in-scope authentication/role-boundary weakening on the node API.

## Likelihood Explanation
High. No special privilege beyond a valid session is required, the mutation is reachable through the standard GraphQL endpoint, and the flaw is a straightforward missing validation, not a race condition or contrived edge case. It is deterministically reproducible on every request.

## Recommendation
Add `utils.VerifyPasswordComplexity(args.Input.NewPassword, dbUser.Email)` in `Resolver.UpdateUserPassword` immediately after the old-password verification and before calling `SetPassword`, mirroring the check in `UserController.UpdatePassword`, and surface complexity failures via the existing `NewUpdatePasswordPayload` input-error pattern.

## Proof of Concept
1. Authenticate as any Chainlink node user (obtain a valid session cookie via `/sessions` login).
2. Send the GraphQL mutation:
```graphql
mutation {
  updateUserPassword(input: { oldPassword: "<current password>", newPassword: "a" }) {
    ... on UpdatePasswordSuccess {
      user { email }
    }
    ... on InputErrors {
      errors { path message code }
    }
  }
}
```
3. Observe the mutation succeeds (`UpdatePasswordSuccess`) despite `newPassword` being far below the mandated 16-character minimum, whereas the equivalent REST call `PATCH /v2/user/password` with the same body is rejected with `422 Unprocessable Entity` due to `utils.VerifyPasswordComplexity` in `UserController.UpdatePassword`.

### Citations

**File:** core/web/user_controller.go (L225-233)
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
```

**File:** core/utils/password.go (L20-70)
```go
const PasswordComplexityRequirements = `
Must have a length of 16-50 characters
Must not comprise:
	Leading or trailing whitespace (note that a trailing newline in the password file, if present, will be ignored)
`

const MinRequiredLen = 16

var LeadingWhitespace = regexp.MustCompile(`^\s+`)
var TrailingWhitespace = regexp.MustCompile(`\s+$`)

var (
	ErrMsgHeader = fmt.Sprintf(`
Expected password complexity:
Must be at least %d characters long
Must not comprise:
	Leading or trailing whitespace
	A user's API email

Faults:
`, MinRequiredLen)
	ErrWhitespace = errors.New("password contains a leading or trailing whitespace")
)

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
