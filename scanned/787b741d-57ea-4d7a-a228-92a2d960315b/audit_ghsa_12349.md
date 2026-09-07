# [H] Cross-Site Request Forgery in JFinalCMS via /admin/category/delete

## Summary
Severity: High
Advisory: GHSA-mwvq-gc5w-m78f
CVE: CVE-2023-49398
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-mwvq-gc5w-m78f
Type: github-advisory

## Affected
- Maven: `com.jfinal:jfinal` — affected >=0

## Details
JFinalCMS v5.0.0 was discovered to contain a Cross-Site Request Forgery (CSRF) vulnerability via /admin/category/delete.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49398
- https://github.com/nightcloudos/new_cms/blob/main/CSRF%20exists%20at%20the%20deletion%20point%20of%20column%20management.md
