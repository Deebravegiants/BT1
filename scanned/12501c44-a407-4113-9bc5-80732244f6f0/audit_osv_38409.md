# [C] Cacti: Pre-authentication SQL injection via rfilter RLIKE clause in graph_view.php

## Summary
Severity: Critical
Advisory: CVE-2026-39893
Aliases: GHSA-69gg-mjfm-jjpc
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-39893
Type: osv

## Details
Cacti is an open source performance and fault management framework. In versions 1.2.30 and prior, the rfilter request variable was concatenated into a RLIKE SQL clause without sanitization. The endpoint does not require authentication (graph viewing supports guest access via the configured guest user), so the SQLi was reachable pre-auth on installs with guest viewing enabled. This issue was fixed in version 1.2.31.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39893.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-69gg-mjfm-jjpc
- https://nvd.nist.gov/vuln/detail/CVE-2026-39893
- https://github.com/Cacti/cacti/pull/7039
