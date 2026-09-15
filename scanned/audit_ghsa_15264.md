# [M] Mage AI Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cgxv-795x-3vqr
CVE: CVE-2024-45189
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-23
Source: https://github.com/advisories/GHSA-cgxv-795x-3vqr
Type: github-advisory

## Affected
- PyPI: `mage-ai` — affected >=0

## Details
Mage AI allows remote users with the "Viewer" role to leak arbitrary files from the Mage server due to a path traversal in the "Git Content" request

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45189
- https://github.com/mage-ai/mage-ai
- https://research.jfrog.com/vulnerabilities/mage-ai-git-content-request-remote-arbitrary-file-leak-jfsa-2024-001039604
