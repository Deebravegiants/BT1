# [C] CVE-2025-32461

## Summary
Severity: Critical
Advisory: CVE-2025-32461
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-09
Source: https://osv.dev/vulnerability/CVE-2025-32461
Type: osv

## Details
wikiplugin_includetpl in lib/wiki-plugins/wikiplugin_includetpl.php in Tiki before 28.3 mishandles input to an eval. The fixed versions are 21.12, 24.8, 27.2, and 28.3.

## References
- http://seclists.org/fulldisclosure/2025/Jul/11
- https://tiki.org/article517
- https://tiki.org/article518
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32461.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32461
- https://gitlab.com/tikiwiki/tiki/-/commit/406bea4f6c379a23903ecfd55e538d90fd669ab0
- https://gitlab.com/tikiwiki/tiki/-/commit/801ed912390c2aa6caf12b7b953e200f5d4bc0b1
- https://gitlab.com/tikiwiki/tiki/-/commit/9ffb4ab21bd86837370666ecd6afd868f3d7877a
- https://gitlab.com/tikiwiki/tiki/-/commit/be8dc1aa220fbceb07a7a5dc36416243afccd358
- https://gitlab.com/tikiwiki/tiki/-/commit/f3f36c1ac702479209acfcaec5789d2fd1f996bc
