# [M] CVE-2024-37879

## Summary
Severity: Medium
Advisory: CVE-2024-37879
CVSS: 4.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-09-20
Source: https://osv.dev/vulnerability/CVE-2024-37879
Type: osv

## Details
Improper input validation in /admin/config/save in User-friendly SVN (USVN) before v1.0.12 and below allows administrators to execute arbitrary code via the fields "siteTitle", "siteIco" and "siteLogo".

## References
- https://github.com/usvn/usvn/releases/tag/1.0.12
- https://www.usvn.info/2024/06/09/usvn-1.0.12
- https://www.usvn.info/news.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37879.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-37879
- https://github.com/usvn/usvn/commit/6b4678954fca9635154743b95ff9c8947cf5f46f
