# [C] HireFlow: Use of Hard-coded Credentials

## Summary
Severity: Critical
Advisory: CVE-2026-45336
Aliases: GHSA-x53g-jr84-jrv5
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-45336
Type: osv

## Details
HireFlow is a web-based interview management system for managing candidates, scheduling interviews, and tracking hiring progress. In 1.2 and earlier, app.py assigns a hard-coded Flask secret_key used to sign session cookies, allowing unauthenticated attackers who know the public source value to forge cookies containing role=admin and user_id values and bypass authentication. The advisory lists version 1.3 as fixed.

## References
- https://github.com/StratonWebDesigners/HireFlow/releases/tag/v1.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45336.json
- https://github.com/StratonWebDesigners/HireFlow/security/advisories/GHSA-x53g-jr84-jrv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45336
