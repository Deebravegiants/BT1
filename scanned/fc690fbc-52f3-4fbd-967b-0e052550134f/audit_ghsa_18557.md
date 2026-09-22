# [M] Filemanager is vulnerable to Relative Path Traversal through filemanager.php

## Summary
Severity: Medium
Advisory: GHSA-r7q6-6fmq-mx4c
CVE: CVE-2025-46002
CWE: CWE-23
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-18
Source: https://github.com/advisories/GHSA-r7q6-6fmq-mx4c
Type: github-advisory

## Affected
- Packagist: `simogeo/filemanager` — affected >=0

## Details
An issue in Filemanager v2.5.0 and below allows attackers to execute a directory traversal via sending a crafted HTTP request to the filemanager.php endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-46002
- https://github.com/simogeo/Filemanager
- https://github.com/simogeo/Filemanager/releases/tag/v1.7.0
- https://github.com/simogeo/Filemanager/releases/tag/v1.8.0
- https://github.com/simogeo/Filemanager/releases/tag/v2.0.0
- https://github.com/simogeo/Filemanager/releases/tag/v2.1.0
- https://github.com/simogeo/Filemanager/releases/tag/v2.2.0
- https://github.com/simogeo/Filemanager/releases/tag/v2.3.0
- https://github.com/zakumini/CVE-List/blob/main/CVE-2025-46002/CVE-2025-46002.md
- https://www.exploit-db.com/exploits/38945
