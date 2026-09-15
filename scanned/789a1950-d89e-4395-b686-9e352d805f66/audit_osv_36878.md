# [M] Memory Exhaustion via Malformed PSD File Upload

## Summary
Severity: Medium
Advisory: CVE-2026-26246
Aliases: GHSA-44mv-jq72-gj49, GO-2026-4727
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-26246
Type: osv

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to bound memory allocation when processing PSD image files which allows an authenticated attacker to cause server memory exhaustion and denial of service via uploading a specially crafted PSD file. Mattermost Advisory ID: MMSA-2026-00572

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26246.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-26246
