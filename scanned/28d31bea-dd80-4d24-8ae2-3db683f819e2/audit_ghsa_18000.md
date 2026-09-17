# [M] Payload's SQLite adapter Session Fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-26rv-h2hf-3fw4
CVE: CVE-2025-4644
CWE: CWE-384
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-26rv-h2hf-3fw4
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <3.44.0
- npm: `@payloadcms/next` — affected >=0 <3.44.0
- npm: `@payloadcms/graphql` — affected >=0 <3.44.0

## Details
A Session Fixation vulnerability existed in Payload's SQLite adapter due to identifier reuse during account creation. A malicious attacker could create a new account, save its JSON Web Token (JWT), and then delete the account, which did not invalidate the JWT. As a result, the next newly created user would receive the same identifier, allowing the attacker to reuse the JWT to authenticate and perform actions as that user.

This issue has been fixed in version 3.44.0 of Payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4644
- https://github.com/payloadcms/payload/commit/26d709dda6e512ce347557eaa2057db6e0cbf809
- https://cert.pl/en/posts/2025/08/CVE-2025-4643
- https://github.com/payloadcms/payload
