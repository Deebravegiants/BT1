Confirmed: `oidcAuthenticator.sessionReaper` (`core/sessions/oidcauth/reaper.go`) only purges stale `oidc_sessions` rows — it never re-syncs `oidc_user_api_tokens` against the upstream IdP, and `DeleteAuthToken` (`core/sessions/oidcauth/oidc.go:551`) is only invoked through `UserController.DeleteAPIToken` / `Resolver.DeleteAPIToken`, both of which are strictly self-service and require the requester's own current password (`core/web/user_controller.go:289-330`, `core/web/resolver/mutation.go:1024-1059`). There is no admin-facing endpoint that revokes another user's API token.

### Title
Admin/operator has no way to immediately revoke an OIDC-authenticated user's API token, permanently valid until expiry — (File: core/sessions/oidcauth/oidc.go)

### Summary
The Hats Protocol report describes a class of bug where an entity that is supposed to be revocable/controllable by an admin (a linked tophat's eligibility) is instead permanently immutable, so misbehaving/offboarded actors retain elevated privileges the admin cannot strip. The same structural bug class appears in Chainlink's OIDC authentication provider: a user's locally cached API token role is fixed for its full configured duration and can only be deleted by the token owner themselves, with no external-initiator/admin-driven revocation path, and no background process re-validates the token against the upstream identity provider.

### Finding Description
When `WebServer.AuthenticationMethod` is set to `oidc`, users obtain an API token via `CreateAndSetAuthToken` → `SetAuthToken` (`core/sessions/oidcauth/oidc.go:500-548`), which inserts a row into `oidc_user_api_tokens` containing the user's email, cached `user_role`, and a hashed secret. Subsequent API-token authentication is handled entirely by `FindUserByAPIToken` (`core/sessions/oidcauth/oidc.go:297-338`), which validates the token purely by checking `created_at + UserAPITokenDuration >= now()` [1](#0-0) . It never re-queries the OIDC provider or checks whether the account/role still exists or is still authorized.

`DeleteAuthToken` — the only mechanism that removes a token early — is exposed exclusively through self-service endpoints that require the caller's own session and their own current password: `UserController.DeleteAPIToken` (`core/web/user_controller.go:289-330`) and the GraphQL `DeleteAPIToken` resolver (`core/web/resolver/mutation.go:1024-1059`). Neither takes an arbitrary target email; both operate on `webauth.GetAuthenticatedUser`/`GetGQLAuthenticatedSession`'s own identity. `UserController.Delete` (which deletes an entire user record via `AuthenticationProvider().DeleteUser`) is unsupported for OIDC as well as LDAP — LDAP explicitly returns `ErrNotSupported` (`core/sessions/ldapauth/ldap.go:376-378`), and OIDC's `sessionReaper` (`core/sessions/oidcauth/reaper.go:37-44`) only purges stale `oidc_sessions`, never touches `oidc_user_api_tokens`.

Contrast this with LDAP, which does implement a corrective mechanism: `LDAPServerStateSyncer.Work` re-queries the upstream directory on every login/logout and (optionally) on a timer, purging or downgrading `ldap_user_api_tokens` rows for users who are removed from groups or marked inactive (`core/sessions/ldapauth/sync.go:180-275`). The OIDC provider has no equivalent syncer at all — `application.go` only wires an `oidcauth.NewSessionReaper` for OIDC (`core/services/chainlink/application.go:600-608`), which reaps sessions but does not exist for `oidc_user_api_tokens`.

The result: once an OIDC-backed node operator creates a long-lived API token (`UserAPITokenDuration` defaults to `240h0m0s` — 10 days, per `core/config/docs/core.toml:233`), a node admin has no supported path to invalidate it before expiry if the token owner is compromised, terminated, or has their upstream role/claims changed — mirroring the Hats bug where an admin cannot revoke a tophat wearer's eligibility because the value was permanently fixed with no unlink/relink-style corrective hook.

### Impact Explanation
An OIDC-issued API token retains its originally cached role and full API access for up to its configured duration (default 10 days) with no in-band way for the node operator/admin to force revocation. If the user's OIDC group membership/claims are downgraded or removed (e.g. an employee is terminated, or a credential leaks), that user (or whoever holds the leaked token) keeps privileged Chainlink node API access — including any operations gated on their cached role — until natural token expiry, contradicting the intended "revoke on demand" administrative capability that exists for password-based sessions (`SessionsController.Destroy`) and for LDAP (`LDAPServerStateSyncer`).

### Likelihood Explanation
This requires no attacker sophistication beyond already having obtained a valid API token (via compromise, insider access, or being an about-to-be-offboarded legitimate user) — a routine operational scenario for any node running with `AuthenticationMethod = oidc` and `UserAPITokenEnabled = true`. The gap is a straightforward missing-control issue, not a exploit chain, so likelihood of the underlying gap being present in any OIDC deployment is high; actual impact depends on whether/when such a token is misused.

### Recommendation
Add an admin-facing token-revocation path for OIDC (and mirror it for LDAP local API-token entries), e.g. an `AuthenticationProvider` method to delete a specific user's API token by email/admin action rather than only self-service by password, and/or implement an `oidc_user_api_tokens` sync/reaper analogous to `LDAPServerStateSyncer.Work` that periodically re-validates cached roles/tokens against the upstream OIDC provider and purges tokens for deactivated or downgraded accounts.

### Proof of Concept
1. Configure a node with `WebServer.AuthenticationMethod = "oidc"` and `WebServer.OIDC.UserAPITokenEnabled = true`.
2. User A logs in via OIDC with an elevated claim/role and calls the "create API token" flow, invoking `CreateAndSetAuthToken` → row inserted into `oidc_user_api_tokens` with `user_role` cached (`core/sessions/oidcauth/oidc.go:500-548`).
3. Upstream identity provider revokes/downgrades User A (removes them from the admin group, disables account, or the token leaks to another party).
4. Node admin has no endpoint to invalidate User A's token; `DeleteAPIToken` requires User A's own session and password (`core/web/user_controller.go:289-330`).
5. Requests presenting the token continue to succeed via `FindUserByAPIToken`, which only checks `created_at + UserAPITokenDuration >= now()` (`core/sessions/oidcauth/oidc.go:313-321`), for up to 10 days by default, regardless of the upstream revocation.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L313-321)
```go
		if err := tx.GetContext(ctx, &foundUserToken,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_user_api_tokens WHERE token_key = $1",
			apiToken, oi.config.UserAPITokenDuration().Duration(),
		); err != nil {
			return err
		}
		if !foundUserToken.Valid {
			return clsessions.ErrUserSessionExpired
		}
```
