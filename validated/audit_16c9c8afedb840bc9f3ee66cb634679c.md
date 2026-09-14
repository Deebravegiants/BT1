This confirms the analog. `ClearNonCurrentSessions` in `core/sessions/authentication.go` is invoked only when a user changes their password (in `core/web/user_controller.go`'s `updateUserPassword`, called from `UpdatePassword`), and via the GraphQL mutation in `core/web/resolver/mutation.go`. It is never invoked when a WebAuthn/MFA credential is registered.

<cite repo="AYontt/chainlink--006" path="core/web/webauthn_controller.go" start="62,88,103" end="62,101,103" />

### Title
Existing sessions are not terminated after WebAuthn (MFA) enrollment, allowing a hijacked session to persist post-2FA registration - (File: core/web/webauthn_controller.go)

### Summary
`WebAuthnController.FinishRegistration` saves a newly enrolled WebAuthn credential to the user's account but never invalidates the user's other active sessions, unlike the password-change flow which explicitly calls `ClearNonCurrentSessions`.

### Finding Description
When a user (or an admin acting on a user's behalf via the same authenticated-user flow) completes MFA/WebAuthn enrollment, `FinishRegistration` validates the challenge, persists the credential with `sessions.AddCredentialToUser`, and writes an audit log entry `audit.Auth2FAEnrolled` — but at no point does it call `AuthenticationProvider().ClearNonCurrentSessions(ctx, sessionID)`.
<cite repo="AYontt/chainlink--006" path="core/web/webauthn_controller.go" start="62,88,94,101" end="62,101,101" />

Compare this to the password reset flow, `UserController.updateUserPassword`, which explicitly clears all other sessions for the account before setting the new password:
<cite repo="AYontt/chainlink--006" path="core/web/user_controller.go" start="341,351" end="341,351" />

The `AuthenticationProvider` interface itself defines `ClearNonCurrentSessions(ctx, sessionID) error` as a first-class capability that is implemented consistently across all three authenticators (`localauth`, `ldapauth`, `oidcauth`), each of which deletes all other session rows for the user's email while preserving the current one: [1](#0-0) 

This same pattern of session cleanup on "other sensitive account changes" is absent from the WebAuthn enrollment path across all backends — `localauth`, `ldapauth`, and `oidcauth` implementations of `SaveWebAuthn`/credential storage do not touch the sessions table.

This is the exact bug class described in the OpenProject advisory: registering/confirming a new 2FA device should invalidate pre-existing sessions, because if an attacker already has a stolen/leaked session cookie (e.g. via XSS, a shared machine, or a previously compromised credential), the legitimate user's act of "securing" their account with MFA gives no protection — the attacker's already-authenticated session token remains valid indefinitely (until natural session-timeout/reaper expiry).

### Impact Explanation
An unprivileged attacker who has obtained a valid session cookie for a chainlink node's Operator UI user (through session theft, XSS, shared workstation, etc.) retains full session access indefinitely even after the legitimate user notices something is wrong and adds a hardware/WebAuthn key to "lock down" the account. Given a chainlink node's UI/API grants job management, key management, and other privileged operations depending on role, an unrevoked stolen session directly threatens unauthorized job runs or config/key changes. The severity is bounded by the requirement that a session was already compromised through some other means; this bug prevents the standard mitigation (adding 2FA) from working as expected.

### Likelihood Explanation
Likelihood of the precondition (an already-stolen but still-valid session existing) is scenario-dependent and not itself introduced by this bug. Given that precondition, exploitation of this gap is deterministic and requires no special access — any account that adds a WebAuthn credential while another live session exists (attacker's or otherwise) leaves that other session unrevoked. `SessionTimeout` defaults to 15 minutes for LDAP/local auth reevaluation intervals but core "sessions" table rows for local/OIDC/LDAP auth are only expired by the session reaper on its own schedule, not immediately upon MFA enrollment. [2](#0-1) 

### Recommendation
In `WebAuthnController.FinishRegistration` (`core/web/webauthn_controller.go`), after successfully persisting the new credential via `sessions.AddCredentialToUser`, call `w.App.AuthenticationProvider().ClearNonCurrentSessions(ctx, sessionID)` using the current request's session ID (obtainable the same way `getCurrentSessionID` does in `core/web/user_controller.go`), mirroring the password-change flow, before returning success to the client.

### Proof of Concept
1. Attacker obtains a valid session cookie for `victim@example.com` (e.g., via XSS or a shared/unlocked browser), without any WebAuthn/MFA registered on the account.
2. Victim notices suspicious activity and, believing they are securing the account, logs in normally and calls `POST /webauthn/begin` then `POST /webauthn/finish` to register a hardware security key, per `WebAuthnController.BeginRegistration`/`FinishRegistration`.
3. `FinishRegistration` stores the new credential and audits `Auth2FAEnrolled`, but issues no call analogous to `ClearNonCurrentSessions`.
4. The attacker's previously stolen session cookie remains valid and continues to authenticate against `AuthorizedUserWithSession`/session lookups, granting full access to the account despite the victim's newly-enrolled MFA device — until the session naturally expires or is manually revoked.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L442-448)
```go
func (oi *oidcAuthenticator) ClearNonCurrentSessions(ctx context.Context, sessionID string) error {
	var email string
	if err := oi.ds.GetContext(ctx, &email, "SELECT user_email FROM oidc_sessions WHERE id = $1", sessionID); err != nil {
		return err
	}
	_, err := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE lower(user_email) = lower($1) AND id != $2", email, sessionID)
	return err
```

**File:** core/config/docs/core.toml (L241-241)
```text
SessionTimeout = '15m0s' # Default
```
