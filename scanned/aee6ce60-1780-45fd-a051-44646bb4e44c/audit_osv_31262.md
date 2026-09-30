# [M] Calibre SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2024-7009
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-08-06
Source: https://osv.dev/vulnerability/CVE-2024-7009
Type: osv

## Details
Unsanitized user-input in Calibre <= 7.15.0 allow users with permissions to perform full-text searches to achieve SQL injection on the SQLite database.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7009.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7009
- https://starlabs.sg/advisories/24/24-7009/
- https://github.com/kovidgoyal/calibre/commit/d56574285e8859d3d715eb7829784ee74337b7d7
- https://github.com/kovidgoyal/calibre
