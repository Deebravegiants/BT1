# [C] Open ISES Tickets < 3.44.2 Hardcoded MySQL Database Credentials in loader.php

## Summary
Severity: Critical
Advisory: CVE-2026-48241
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-48241
Type: osv

## Details
Open ISES Tickets before 3.44.2 contains hardcoded MySQL database credentials in loader.php (a public-facing database utility) that are committed to the source repository. Any actor with access to the public source tree (or an unauthenticated attacker with read access to the file on a deployed installation) can read the username, password, and database name and use them to connect to the database if it is reachable from their network.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48241.json
- https://github.com/openises/tickets/releases/tag/v3.44.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48241
- https://www.vulncheck.com/advisories/open-ises-tickets-hardcoded-mysql-credentials-in-loader-php
- https://github.com/openises/tickets/commit/ecfeb406a016766cae81c749e14b5145a9f2dbff
