Confirmed: `TestPassword` in `core/sessions/localauth/orm.go:308-318` verifies only the bcrypt password hash and has no interaction with WebAuthn/MFA state at all, unlike `CreateSession` which explicitly loads `GetUserWebAuthn` and enforces the WebAuthn challenge/response flow before issuing a session.

### Title
API token issuance/authentication bypasses WebAuthn (MFA) enforced at session login - (File: core/web/user_controller.go, core/sessions/localauth/orm.go, core/web/auth/auth.go)

### Summary
GitLab CVE-2021-39890 allowed 2FA to be bypassed for LDAP users by authenticating through an alternate mechanism (HTTP Basic Auth) that never invoked the 2FA check enforced on normal session-based login. Chainlink has the same class of bug: session-based login (`CreateSession`) enforces WebAuthn/MFA if the user has enrolled a hardware key, but the alternate authentication path used for the entire `/v2/*` API surface — long-lived API access-key/secret tokens — is minted and later verified without any WebAuthn check whatsoever.

### Finding Description
`CreateSession` in `core/sessions/localauth/orm.go:144-230` is the only code path in the codebase that checks `GetUserWebAuthn` <cite repo="Alyssadaypin/chainlink--010" path="core/sessions/localauth/orm.go" start="164-179" /> and requires a valid WebAuthn attestation (`sr.WebAuthnData`, `FinishWebAuthnLogin`) before creating a cookie session for a user who has MFA enrolled <cite repo="Alyssadaypin/chainlink--010" path="core/sessions/localauth/orm.go" start="181-211" />.

However, issuing a brand-new API token (`POST /v2/user/token` → `UserController.NewAPIToken`, and the GraphQL `createAPIToken` mutation) only requires calling `TestPassword`, which checks nothing but the bcrypt hash:
<cite repo="Alyssadaypin/chainlink--010" path="core/web/user_controller.go" start="267-273" />
<cite repo="Alyssadaypin/chainlink--010" path="core/sessions/localauth/orm.go" start="308-318" />
<cite repo="Alyssadaypin/chainlink--010" path="core/web/resolver/mutation.go" start="1006-1013" />

Once minted, that token is used through `AuthenticateByToken` in `core/web/auth/auth.go:78-112`, which authenticates purely by comparing the access key/secret against the DB — again with no WebAuthn/MFA involvement:
<cite repo="Alyssadaypin/chainlink--010" path="core/web/auth/auth.go" start="78-112" />

This authenticated token is accepted on the entire `/v2/*` route group (`v2Routes`), which includes admin, edit, and run-role endpoints such as user management, bridge management, external initiators, and fund transfers:
<cite repo="Alyssadaypin/chainlink--010" path="core/web/router.go" start="245-282" />

So the WebAuthn/MFA protection that is supposed to gate access to a Chainlink node's operator account is fully bypassable once an attacker obtains only the account password (not the second factor): the attacker calls the password-only `NewAPIToken`/`createAPIToken` endpoint to mint a persistent credential, then uses that credential via `AuthenticateByToken` to access privileged `/v2/*` endpoints indefinitely, never triggering the MFA challenge that `CreateSession` would have required for cookie-based login.

### Impact Explanation
An attacker who has obtained only a node operator's password (e.g., via phishing, credential reuse, or a leaked config) can mint a durable API token and use it to fully bypass the account's WebAuthn 2FA protection, gaining ongoing programmatic access to job/bridge management, external initiator management, and (with admin role) fund-transfer/user-management endpoints — precisely the security guarantee 2FA is meant to provide against password-only compromise.

### Likelihood Explanation
Moderate-to-high. It requires only knowledge of the victim's password (the exact threat model MFA is designed to defend against), and the token-minting endpoints (`/v2/user/token`, GraphQL `createAPIToken`) are reachable by any authenticated password holder without any additional secret. No LDAP/OIDC/network-layer or privileged access is required — this is reachable purely from an unprivileged client with stolen credentials.

### Recommendation
Require WebAuthn verification (equivalent to the check in `CreateSession`) before permitting `NewAPIToken`/`DeleteAPIToken`/`createAPIToken`/`deleteAPIToken` operations for any user who has WebAuthn credentials enrolled, and/or require re-verification of WebAuthn on `AuthenticateByToken` for MFA-enrolled accounts (e.g., short-lived tokens re-validated periodically, or binding token issuance to a freshly MFA'd session).

### Proof of Concept
1. Enroll WebAuthn/MFA for an account (`POST /v2/enroll_webauthn`), confirming that subsequent `POST /sessions` (`CreateSession`) requires a WebAuthn challenge-response as shown in `core/sessions/localauth/orm_test.go:264-297`.
2. As an attacker who has only the account's plaintext password (no WebAuthn device), call `POST /v2/user/token` with `{"password": "<victim password>"}` — per `core/web/user_controller.go:267-273`, this succeeds because only `TestPassword` is checked.
3. Use the returned `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` (or equivalent API-key headers) against any `/v2/*` route — `AuthenticateByToken` in `core/web/auth/auth.go:78-112` grants full session-equivalent access, with no WebAuthn step ever performed.