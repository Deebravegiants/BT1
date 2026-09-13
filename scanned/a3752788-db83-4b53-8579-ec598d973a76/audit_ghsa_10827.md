# [C] AVideo has Unauthenticated SQL Injection via JSON Request Bypass in objects/videos.json.php

## Summary
Severity: Critical
Advisory: GHSA-pv87-r9qf-x56p
CVE: CVE-2026-28501
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-pv87-r9qf-x56p
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Impact

An unauthenticated SQL Injection vulnerability exists in AVideo within the objects/videos.json.php and objects/video.php components.

The application fails to properly sanitize the catName parameter when it is supplied via a JSON-formatted POST request body. Because JSON input is parsed and merged into $_REQUEST after global security checks are executed, the payload bypasses the existing sanitization mechanisms.

This allows an unauthenticated attacker to:

- Execute arbitrary SQL queries
- Perform full database exfiltration
- Extract sensitive data including administrator usernames, password hashes, session identifiers and user records
- Potentially escalate privileges by cracking password hashes offline
- Chain with authenticated vulnerabilities to achieve full system compromise

This vulnerability is classified as:
- CWE-89: Improper Neutralization of Special Elements used in an SQL Command (SQL Injection)


## Patches

This vulnerability has been fixed in version 23.

Users must upgrade to version 23 or later.


## Workarounds

There is no reliable workaround.

The only recommended mitigation is to upgrade immediately to version 23 upon its release.


## References

Internal security report.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-pv87-r9qf-x56p
- https://nvd.nist.gov/vuln/detail/CVE-2026-28501
- https://github.com/WWBN/AVideo/commit/0c10be681c64044618ab94473251bd7c9b114fa1
- https://github.com/WWBN/AVideo
- https://github.com/WWBN/AVideo/releases/tag/24.0
