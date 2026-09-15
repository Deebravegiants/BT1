# [C] SiYuan before v3.8.2 Read-Only Boundary Bypass via fullTextSearchBlock

## Summary
Severity: Critical
Advisory: CVE-2026-87808
Aliases: GHSA-4qwm-3p58-vh67
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87808
Type: osv

## Details
SiYuan versions <= 3.8.1 contain an incomplete fix for CVE-2026-32767 (GHSA-j7wh-x834-p3r7). The prior fix (commit d5e2d0bc) added an administrator check for SQL mode (method=2) in POST /api/search/fullTextSearchBlock, but the endpoint still does not enforce the application's read-only boundary: for method=2 it forwards caller-supplied SQL to the blocks database query path without calling model.CheckReadonly or CheckReadonlyStatementInBox. As a result, when a workspace runs in read-only mode (--readonly=true), an authenticated administrator can submit arbitrary SQL through /api/search/fullTextSearchBlock and obtain raw read access to the blocks database, even though the dedicated /api/query/sql endpoint is blocked in that mode. Fixed in v3.8.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87808.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-4qwm-3p58-vh67
- https://nvd.nist.gov/vuln/detail/CVE-2026-87808
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-read-only-boundary-bypass-via-fulltextsearchblock
- https://github.com/siyuan-note/siyuan/commit/d5e2d0bce0dffef5f61bd8066954bc2d41181fc5
