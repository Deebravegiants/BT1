# [C] Auth.js: Email normalizer validates the address before Unicode normalization, allowing a homoglyph @ bypass

## Summary
Severity: Critical
Advisory: GHSA-7rqj-j65f-68wh
CVE: CVE-2026-73420
CWE: CWE-180
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-7rqj-j65f-68wh
Type: github-advisory

## Affected
- npm: `@auth/core` — affected >=0.1.0 <0.41.3
- npm: `next-auth` — affected >=4.10.3 <4.24.15
- npm: `next-auth` — affected >=5.0.0-beta.1 <5.0.0-beta.32

## Details
## Summary

The default email-address normalizer used by the email/magic-link sign-in flow validates the address **before** applying Unicode normalization. An address can contain a Unicode character that is not an ASCII `@` (U+0040) but canonicalizes to one under NFKC/NFKD normalization (the normalization commonly applied by mail libraries and services for internationalized email). Such an address passes the normalizer's single-`@` check, but a downstream mail library that normalizes the string then sees two `@` separators and may deliver the passwordless sign-in link to a different recipient than intended. This is an instance of validating before canonicalizing.

## Am I affected?

You may be affected if **all** of the following hold:

- You use `next-auth` `>= 4.0.0, < 4.24.14`, or `@auth/core` `>= 0.1.0, < 0.41.3`.
- You have the email / magic-link (passwordless) provider enabled.
- You rely on the built-in default identifier normalizer (you have not supplied your own `normalizeIdentifier`).
- Your `sendVerificationRequest` implementation uses a mail library or delivery service that applies Unicode normalization to recipient addresses (most internationalized-email/SMTPUTF8-capable senders do).

You are **not** affected if you do not use the email provider, or if your normalizer/mailer rejects or canonicalizes non-ASCII addresses before they are validated.

## Impact

- Account takeover: an attacker who knows a victim's email address can request a magic link that is delivered to an attacker-controlled mailbox, then use it to sign in as the victim.
- No victim interaction is required to misroute the link; the attacker initiates the flow.

## Patched version

The fix applies Unicode (NFKC) normalization before the address is validated, so homoglyph separators are collapsed and rejected up front. Upgrade to the first release containing this fix (pending; this advisory will be updated with the exact patched version before publication). No application code changes are required after upgrading.

## Workarounds

If you cannot upgrade immediately:

- Supply a custom `normalizeIdentifier` on the email provider that calls `identifier.normalize("NFKC")` (and lower-cases/trims) **before** any validation, and rejects addresses that do not contain exactly one `@` after normalization.
- Or reject any address whose local part or domain contains non-ASCII characters, if your user base does not require internationalized email addresses.

## Credit

Reported by @kakashi-kx. Thank you for the responsible disclosure.

## References
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-7rqj-j65f-68wh
- https://github.com/nextauthjs/next-auth/commit/19d2feb24359fa8c79418907fc68d9ec8152ca94
- https://github.com/nextauthjs/next-auth/commit/a63eee12a1a20cb35209e44195b097868517b9a0
- https://github.com/nextauthjs/next-auth
- https://github.com/nextauthjs/next-auth/releases/tag/@auth/core@0.41.3
- https://github.com/nextauthjs/next-auth/releases/tag/next-auth@4.24.15
- https://github.com/nextauthjs/next-auth/releases/tag/next-auth@5.0.0-beta.32
