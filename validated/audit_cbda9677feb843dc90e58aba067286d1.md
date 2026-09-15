The code review confirms the claim's factual accuracy exactly as stated. Password change flow does not revoke API tokens.

Audit Report

## Title
Password change fails to revoke active API tokens, allowing continued unprivileged access after credential rotation - (File: `core/web/user_controller.go`)

## Summary
`UserController.updateUserPassword` and the GraphQL `UpdateUserPassword` resolver only call `ClearNonCurrentSessions` (which purges other browser session-cookie rows) and `SetPassword` (which only updates `hashed_password`), while never calling `DeleteAuthToken` to revoke the user's API token (`token_key`/`token_hashed_secret`). As a result, a previously issued API token remains fully valid indefinitely after a password change, since `FindUserByAPIToken` performs a straight lookup by `token_key` with no linkage to password state.

## Finding Description
`UserController.updateUserPassword` (`core/web/user_controller.go:341-359`) calls `orm.ClearNonCurrentSessions(ctx, sessionID)` and `orm.SetPassword(ctx, user, newPassword)`. `ClearNonCurrentSessions` (`core/sessions/localauth/orm.go:243-251`) deletes rows only from the `sessions` table. `SetPassword` (`core/sessions/localauth/orm.go:298-306`) updates only `hashed_password` and `updated_at`; it never touches `token_key`, `token_salt`, or `token_hashed_secret`, nor does it invoke `DeleteAuthToken` (`core/sessions/localauth/orm.go:342-346`). The identical gap exists in `Resolver.UpdateUserPassword` (`core/web/resolver/mutation.go:934-969`), which also calls only `ClearNonCurrentSessions` and `SetPassword`. Because `AuthenticateByToken` (`core/web/auth/auth.go:75-112`) authenticates purely via `FindUserByAPIToken` (`core/sessions/localauth/orm.go:48-53`), a `SELECT * FROM users WHERE token_key = $1` lookup with no reference to `hashed_password` or `updated_at`, the token authentication path is completely decoupled from password/credential state. The codebase does demonstrate awareness that tokens must sometimes be explicitly revoked — `DeleteAPIToken` (`core/web/user_controller.go:288-330`) calls `DeleteAuthToken` — but that call is never wired into the password-change flow.

## Impact Explanation
This maps to the node API authentication/role-bypass impact category: an attacker holding a previously issued, valid API token (e.g., obtained via device compromise, prior legitimate co-access, or a leak) retains full authenticated access with the token owner's role privileges even after the legitimate user performs the standard remediation action of rotating their password. This defeats the security purpose of password rotation as an incident-response/credential-hygiene control specifically for the alternate (API token) authentication surface.

## Likelihood Explanation
The finding is a broken remediation guarantee rather than a novel initial-access vector: it requires the attacker to already hold a valid API token issued to the victim account. This precondition is a leaked/stolen credential scenario for the *token*, which is used here only to illustrate why password rotation should sever token access — the underlying defect (the password-change code path never calling `DeleteAuthToken`) is a genuine, deterministic code omission, verifiable purely by reading `updateUserPassword` and `SetPassword`, independent of how the attacker originally obtained the token.

## Recommendation
In both `UserController.updateUserPassword` (`core/web/user_controller.go:341-359`) and `Resolver.UpdateUserPassword` (`core/web/resolver/mutation.go:934-969`), call `orm.DeleteAuthToken(ctx, user)` alongside `ClearNonCurrentSessions` and `SetPassword`, so that any previously issued API token is invalidated whenever the password changes, forcing reissuance via `CreateAndSetAuthToken` if API access is still required.

## Proof of Concept
1. As user `alice` (`view`/`edit` or `admin` role), call `POST /v2/user/tokens` to obtain an API `access_key`/`secret` via `CreateAndSetAuthToken`.
2. Use the token's `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers to call an authenticated endpoint (e.g., `GET /v2/bridge_types`) via `AuthenticateByToken` — confirm success.
3. As `alice`, call `PATCH /v2/user/password` (or the `updateUserPassword` GraphQL mutation) with a new password.
4. Re-issue the same original API token from step 1 against `GET /v2/bridge_types` — the request still succeeds, proving `SetPassword` (`core/sessions/localauth/orm.go:298-306`) left `token_key`/`token_hashed_secret` untouched and `updateUserPassword` (`core/web/user_controller.go:341-359`) never invoked `DeleteAuthToken`.