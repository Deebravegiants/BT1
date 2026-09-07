# [M] Mage AI incorrectly gives privileges to users with deleted accounts

## Summary
Severity: Medium
Advisory: GHSA-jg95-r9xh-xw9c
CVE: CVE-2024-45187
CWE: CWE-266, CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-23
Source: https://github.com/advisories/GHSA-jg95-r9xh-xw9c
Type: github-advisory

## Affected
- PyPI: `mage-ai` — affected >=0

## Details
Guest users in the Mage AI framework that remain logged in after their accounts are deleted, are mistakenly given high privileges and specifically given access to remotely execute arbitrary code through the Mage AI terminal server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45187
- https://github.com/mage-ai/mage-ai
- https://research.jfrog.com/vulnerabilities/mage-ai-deleted-users-rce-jfsa-2024-001039602
