# [M] Directus Lacks Session Tokens Invalidation

## Summary
Severity: Medium
Advisory: GHSA-g65h-35f3-x2w3
CVE: CVE-2024-34709
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-05-13
Source: https://github.com/advisories/GHSA-g65h-35f3-x2w3
Type: github-advisory

## Affected
- npm: `directus` — affected >=10.10.0 <10.11.0

## Details
### Summary
Currently session tokens function like the other JWT tokens where they are not actually invalidated when logging out. The `directus_session` gets destroyed and the cookie gets deleted but if you captured the cookie value it will still work for the entire expiry time which is set to 1 day by default. Making it effectively a long lived unrevokable stateless token instead of the stateful session token it was meant to be.
When authenticating a session token JWT, Directus should also check whether the associated `directus_session` both still exists and has not expired (although the token should expire at the same time or before the session) to ensure leaked tokens are not valid indefinitely.

## Steps to reproduce
- Copy the current session token from the cookie
- Refresh and or log out
- Use the saved session token to check if it is still valid

### Impact
The lack of proper session expiration may improve the likely success of certain attacks. For example, a user might access a web site from a shared computer (such as at a library, Internet cafe, or open work environment). Incorrect token invalidation could allow an attacker to use the browser's history to access a Directus instance session previously accessed by the victim.

## References
- https://github.com/directus/directus/security/advisories/GHSA-g65h-35f3-x2w3
- https://nvd.nist.gov/vuln/detail/CVE-2024-34709
- https://github.com/directus/directus/commit/a6172f8a6a0f31a6bf4305a090de172ebfb63bcf
- https://github.com/directus/directus
