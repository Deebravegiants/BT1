# [C] Craft CMS: Passkey login accepts replayed WebAuthn assertions

## Summary
Severity: Critical
Advisory: GHSA-wg23-69c2-gjc8
CWE: CWE-294
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-wg23-69c2-gjc8
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.5

## Details
Craft CMS passkey login accepts WebAuthn requestOptions from the unauthenticated login request body and does not persist the updated credential counter returned by the WebAuthn assertion validator. A captured passkey login request body can therefore be replayed because the old challenge is accepted again, and the stored credential counter remains stale.

Craft CMS 5.10.3 and current `5.x` HEAD accept `PublicKeyCredentialRequestOptions` from the unauthenticated `users/login-with-passkey` request body and do not persist the updated `PublicKeyCredentialSource` returned/mutated by `web-auth/webauthn-lib` after assertion validation.

As a result, a captured passkey login request body is not one-time-use. Reposting the same `requestOptions` and `response` can result in validation against the same stale credential counter and create another Craft session for that user. This weakens passkeys from a fresh, server-challenged authentication ceremony into a replayable bearer artifact if one successful assertion body is exposed.


## Attack Scenario

1. A victim successfully logs in with a passkey.
2. The `POST /actions/users/login-with-passkey` body containing `requestOptions` and `response` is captured from an application/request log, debugging proxy, browser extension, compromised analytics layer, or another request-body disclosure point.
3. The attacker reposts the same body to `users/login-with-passkey`.
4. Craft deserializes the attacker-supplied `requestOptions`, so the old challenge remains accepted for validation.
5. The WebAuthn validator compares the assertion's `signCount` against the stale stored credential counter.
6. Because Craft did not persist the updated credential source on the original login, the same stale stored counter is used again.
7. The same captured assertion validates and Craft creates another authenticated session for the victim account.

This is exactly what WebAuthn's challenge and signature-counter lifecycle is meant to prevent: a successful assertion should be bound to a server-issued challenge and should update server-side credential state so it cannot be used again.

## Impact

An attacker who obtains one successful passkey login request body can replay it to create additional authenticated Craft sessions for that user. This defeats WebAuthn’s intended one-time challenge and signature-counter replay protection, reducing a passkey assertion to a reusable bearer artifact if exposed through request logging, a debugging proxy, a compromised same-origin script layer, or another request-body disclosure path.

The impact is an account/session takeover of the affected passkey account after a single assertion body is captured. The issue is in Craft’s native passkey login flow and affects fresh Craft installations with passkeys enabled.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-wg23-69c2-gjc8
- https://github.com/craftcms/cms/commit/d71a66d69cf8852bcfca4484ca718750b5a316d6
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/5.10.5
