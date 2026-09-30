# [C] Cacti  has Pre-Authentication SQL Injection via unanchored FILTER_VALIDATE_REGEXP in graph_view.php

## Summary
Severity: Critical
Advisory: CVE-2026-39955
Aliases: GHSA-gp82-qhrg-crv7
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-39955
Type: osv

## Details
Cacti is an open source performance and fault management framework. Versions 1.2.30 and prior have pre-authentication SQL Injection via unanchored FILTER_VALIDATE_REGEXP in graph_view.php. This issue has been fixed in version 1.2.31.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39955.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-gp82-qhrg-crv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-39955
- https://github.com/Cacti/cacti/commit/4c09efaebf3a9faec66969d0b5c4aceaf397f37f
