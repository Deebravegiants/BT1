# [H] CakePHP: Potential Authentication bypass with CookieAuthenticator

## Summary
Severity: High
Advisory: CVE-2026-77337
Aliases: GHSA-h7xh-9h2x-2m37
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-77337
Type: osv

## Details
CakePHP Authentication is an authentication plugin for CakePHP that can also be used in PSR-7 based applications. Versions before 2.11.2, from 3.0.0 through 3.3.6, and from 4.0.0 through 4.2.0 allow authentication bypass and potential CPU or memory exhaustion when CookieAuthenticator uses unencrypted, forgeable legacy tokens. This issue is fixed in versions 2.11.2, 3.3.7, and 4.2.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77337.json
- https://github.com/cakephp/authentication/security/advisories/GHSA-h7xh-9h2x-2m37
- https://nvd.nist.gov/vuln/detail/CVE-2026-77337
- https://github.com/cakephp/authentication/commit/c94d9a5380e7f4fdf38d338a9de2223a5b087159
- https://github.com/cakephp/authentication/pull/806
- https://github.com/cakephp/authentication/pull/807
