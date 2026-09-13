# [M] ChurchCRM: Username Enumeration via Differential Response in Public Login API

## Summary
Severity: Medium
Advisory: CVE-2026-40485
Aliases: GHSA-x2qh-xmhq-4jpx
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40485
Type: osv

## Details
ChurchCRM is an open-source church management system. In versions prior to 7.2.0, the public API login endpoint (/api/public/user/login) returns distinguishable HTTP response codes based on whether a username exists: 404 for non-existent users and 401 for valid users with incorrect passwords. An unauthenticated attacker can exploit this difference to enumerate valid usernames, with no rate limiting or account lockout to impede the process. This issue has been fixed in version 7.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40485.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-x2qh-xmhq-4jpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40485
- https://github.com/ChurchCRM/CRM/commit/214694eb83778e1f5e52b3dfa2a99d0e965c1850
- https://github.com/ChurchCRM/CRM/pull/8607
