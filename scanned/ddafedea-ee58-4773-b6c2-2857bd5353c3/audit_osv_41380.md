# [M] SiYuan: Publish-mode Reader can exfiltrate private saved-search Criteria via /api/storage/getCriteria (missing publish-access filter)

## Summary
Severity: Medium
Advisory: CVE-2026-59853
Aliases: GHSA-px3c-cf92-9g83
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59853
Type: osv

## Details
SiYuan is an open-source personal knowledge management system. Prior to 3.7.1, the /api/storage/getCriteria endpoint returns saved search criteria from data/storage/criteria.json without the publish-access filtering used by sibling storage endpoints, allowing a publish-mode Reader to read private document paths, notebook, document, and block IDs, and search and replace keywords for unpublished documents. This issue is fixed in versions 3.7.1.

## References
- https://github.com/siyuan-note/siyuan/releases/tag/v3.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59853.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-px3c-cf92-9g83
- https://nvd.nist.gov/vuln/detail/CVE-2026-59853
- https://github.com/siyuan-note/siyuan/commit/0049d0f04ffe9837760d29248b9ef31605077d36
