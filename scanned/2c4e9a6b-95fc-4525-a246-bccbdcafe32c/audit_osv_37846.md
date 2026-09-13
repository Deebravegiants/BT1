# [C] FOSSBilling: Authentication bypass allows unauthenticated administrator creation

## Summary
Severity: Critical
Advisory: CVE-2026-33543
Aliases: GHSA-28mh-j262-q49w
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-33543
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. Versions 0.7.2 and prior expose a guest API endpoint, /api/guest/staff/create, intended for initial administrator bootstrap. Due to a flawed admin-existence check, the endpoint remains usable after an administrator already exists. The flawed guard check uses is_countable() on a value that returns a Model_Admin object or null rather than a countable type, causing the expression to always evaluate as true and bypass the intended protection. As a result, an attacker can reach the unprotected endpoint to create a new administrator account and immediately authenticate, gaining a fully privileged admin session even when an admin already exists. This issue has been fixed in version 0.8.0.

## References
- https://github.com/FOSSBilling/FOSSBilling/releases/tag/0.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33543.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-28mh-j262-q49w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33543
