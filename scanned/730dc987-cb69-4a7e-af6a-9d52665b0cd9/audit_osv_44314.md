# [H] Stalwart Mail Server through 0.16.19 Authorization Code Disclosure via Unvalidated OAuth redirect_uri

## Summary
Severity: High
Advisory: CVE-2026-81036
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-81036
Type: osv

## Details
Stalwart Mail Server does not compare an OAuth redirect target against any registered destination in its default configuration. The validation routine in crates/http/src/auth/oauth/registration.rs returns success immediately when the client-authentication requirement is disabled, and that requirement is false in the shipped settings, so the supplied redirect value is neither matched against a registered client nor otherwise constrained. The value is stored with the authorization code, and the login page reads it back and sends the browser to it with the code attached. A request naming a destination the attacker controls therefore delivers a valid authorization code there once the account holder authenticates, and because the token endpoint checks only that the redirect presented at exchange matches the one recorded with the code, the same party can exchange it for access and refresh tokens and read the account's mail.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81036.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81036
- https://www.vulncheck.com/advisories/stalwart-mail-server-through-0.16.19-authorization-code-disclosure-via-unvalidated-oauth-redirect-uri
- https://github.com/stalwartlabs/stalwart/issues/3205
- https://github.com/stalwartlabs/stalwart
- https://github.com/stalwartlabs/stalwart/blob/v0.16.19/crates/http/src/auth/oauth/registration.rs
