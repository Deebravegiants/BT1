# [C] rConfig Core 8.0.0 < 8.2.10 Unauthorized Admin Registration via web.php

## Summary
Severity: Critical
Advisory: CVE-2026-77915
Aliases: GHSA-w3hx-9cxg-5ccr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-77915
Type: osv

## Details
rConfig Core 8.0.0 before 8.2.10 contains an authentication bypass vulnerability that allows unauthenticated attackers to self-register accounts with full Administrator privileges due to a duplicate bare Auth::routes() call in routes/web.php that re-enables the POST /register route after it was explicitly disabled. Attackers can register a new account that is immediately authenticated with Admin-level access because the registration controller does not assign a role and the users.role column defaults to Admin, enabling access to stored device credentials, user data, and API token issuance.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77915.json
- https://github.com/rconfig/rconfig/releases#release-core-8.2.10
- https://github.com/rconfig/rconfig/security/advisories/GHSA-w3hx-9cxg-5ccr
- https://nvd.nist.gov/vuln/detail/CVE-2026-77915
- https://www.vulncheck.com/advisories/rconfig-unauthorized-admin-registration-via-web-php
- https://github.com/rconfig/rconfig
