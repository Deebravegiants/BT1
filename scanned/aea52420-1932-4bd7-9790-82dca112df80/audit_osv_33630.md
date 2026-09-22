# [C] Missing Path Validation Enables Path Traversal in Controller.php

## Summary
Severity: Critical
Advisory: CVE-2025-47788
Aliases: GHSA-x9vw-6vfx-7rx5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-05-15
Source: https://osv.dev/vulnerability/CVE-2025-47788
Type: osv

## Details
Atheos is a self-hosted browser-based cloud IDE. Prior to v602, similar to GHSA-rgjm-6p59-537v/CVE-2025-22152, the `$target` parameter in `/controller.php` was not properly validated, which could allow an attacker to execute arbitrary files on the server via path traversal. v602 contains a fix for the issue.

## References
- https://github.com/Atheos/Atheos/security/advisories/GHSA-x9vw-6vfx-7rx5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47788.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-47788
- https://github.com/Atheos/Atheos/commit/97fe76871578d2011ebe9281f3a005c5df85162b
