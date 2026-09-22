# [M] Strapi is vulnerable to Insufficient Session Expiration

## Summary
Severity: Medium
Advisory: GHSA-4r8w-3jww-m2rp
CVE: CVE-2025-3930
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-4r8w-3jww-m2rp
Type: github-advisory

## Affected
- npm: `@strapi/strapi` — affected >=0 <5.24.1

## Details
Strapi uses JSON Web Tokens (JWT) for authentication. After logout or account deactivation, the JWT is not invalidated, which allows an attacker who has stolen or intercepted the token to freely reuse it until its expiration date (which is set to 30 days by default, but can be changed). The existence of /admin/renew-token endpoint allows anyone to renew near-expiration tokens indefinitely, further increasing the impact of this attack. This issue has been fixed in version 5.24.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3930
- https://cert.pl/en/posts/2025/06/CVE-2025-3930
- https://github.com/strapi/strapi
- https://strapi.io
- https://strapi.io/blog/security-disclosure-of-vulnerabilities-cve-October-2025
