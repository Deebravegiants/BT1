# [H] Better Auth has an account takeover issue via OAuth auto-link to unverified pre-registered email

## Summary
Severity: High
Advisory: GHSA-g38m-r43w-p2q7
CVE: CVE-2026-53516
CWE: CWE-287, CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-g38m-r43w-p2q7
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0 <1.6.11

## Details
### Am I affected?

Users are affected if all of the following are true:

- Their application uses `better-auth` at a version `< 1.6.11` on the stable line, or any current `next` pre-release.
- `emailAndPassword.enabled: true` is set in their application's `betterAuth({ ... })` configuration.
- At least one OAuth or SSO provider is configured (any built-in social provider, or `genericOAuth(...)`, or any provider via `@better-auth/sso`).
- `account.accountLinking.disableImplicitLinking` is not set to `true`.
- `account.accountLinking.enabled` is not set to `false`.

Setting either `disableImplicitLinking: true` or `enabled: false` closes the hole at the cost of breaking the standard "add another login method" UX. `emailAndPassword.requireEmailVerification: true` does not mitigate, because the link-time `emailVerified` flip promotes the attacker's row to verified, after which the password login becomes usable.

Fix:

1. Upgrade to `better-auth@1.6.11` or later.
2. If developers cannot upgrade, see workarounds below.

### Summary

The OAuth callback's auto-link gate in `handleOAuthUserInfo` admits an implicit account link whenever the provider asserts `email_verified: true`, without requiring the local user row's `emailVerified` to also be `true`. An attacker who pre-registers a victim's email through `/sign-up/email` (which writes a row with `emailVerified: false`) can have the victim's later OAuth identity bound to the attacker's user row, granting both a password login and the victim's OAuth identity on the same account. This is the pre-account-hijacking class — the same shape as Microsoft "nOAuth" (2023) and the Sign in with Apple JWT flaw (2020).

### Details

The auto-link gate validates only the OAuth provider's `userInfo.emailVerified` claim. The local row's `emailVerified` field is never read. When no `(accountId, providerId)` match exists, the user lookup falls back to email, which surfaces any pre-registered row at that email.

A separate post-link step promotes the local `emailVerified` to `true` when the provider's claim is `true` and the local email matches the provider's email. This step is correct for legitimate first-time linking, but combined with the missing local-side check it becomes load-bearing for the takeover: after the link, the attacker's password row is treated as verified, defeating `requireEmailVerification: true` as a mitigation.

The fix adds the local-side ownership check to the gate: implicit linking now also rejects when `dbUser.user.emailVerified` is `false`. The same primitive lives in `one-tap` and inherits the same fix shape; the SSO `domainVerified` short-circuit follows separately as a hardening change.

### Patches

Fixed in `better-auth@1.6.11`. Implicit linking now refuses to attach an OAuth identity to a local account whose `emailVerified` flag is `false`. The same gate change applies in the `one-tap` sign-in plugin, which previously had its own simpler linking path. The Google ID-token `email_verified` claim is also normalized through `toBoolean` so a string `"false"` is treated as falsy (some Google responses send the string, which the prior code treated as truthy).

The public surface for the new gate is `account.accountLinking.requireLocalEmailVerified`, defaulted to `true`. Applications whose users sign up through OAuth without ever verifying their email locally can opt out with `account: { accountLinking: { requireLocalEmailVerified: false } }` to retain the legacy permissive behavior. The option is marked `@deprecated`; the gate at each call site carries a `FIXME` pointing at the next-minor follow-up that drops the option and makes the check unconditional.

Test fixtures across the `admin`, `oidc-provider`, `mcp`, `generic-oauth`, `last-login-method`, and `oauth-provider` suites now pre-verify created users via a `databaseHooks.user.create.before` hook (or the `disableTestUser` opt-in on the oauth-provider RP fixture) so those suites continue to exercise their role and flow logic rather than tripping the new gate.

### Workarounds

If developers cannot upgrade their applications immediately:

- **Disable implicit linking**: set `account.accountLinking.disableImplicitLinking: true`. Forces all linking through the authenticated `/link-social` endpoint where the user must already be signed in.
- **Disable linking entirely**: set `account.accountLinking.enabled: false`. Closes the hole but breaks the multi-login-method UX entirely.

`emailAndPassword.requireEmailVerification: true` alone does not mitigate, because the link-time `emailVerified` flip promotes the attacker's row to verified.

### Impact

- **Account takeover via pre-account hijacking**: the attacker holds a working password login plus the victim's OAuth identity on the same account, granting persistent access.
- **`requireEmailVerification: true` bypass**: the attacker's password login becomes usable post-link.
- **Cross-flow reach**: every OAuth and SSO sign-in path that calls `handleOAuthUserInfo` is affected (built-in social providers, generic-oauth, oauth-proxy, SSO OIDC, SSO SAML, one-tap).

### Credit

Reported by @avrmeduard.

### Resources

- [CWE-287: Improper Authentication](https://cwe.mitre.org/data/definitions/287.html)
- [CWE-345: Insufficient Verification of Data Authenticity](https://cwe.mitre.org/data/definitions/345.html)
- [Sudhodanan & Paverd, Pre-hijacked accounts: an empirical study of security failures in user account creation on the web (USENIX Security 2022)](https://www.usenix.org/conference/usenixsecurity22/presentation/sudhodanan)

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-g38m-r43w-p2q7
- https://nvd.nist.gov/vuln/detail/CVE-2026-53516
- https://github.com/better-auth/better-auth/pull/9578
- https://github.com/better-auth/better-auth/commit/da7e50beee849c59a2ed1ec6b3a38cc6ab9fb563
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.6.11
