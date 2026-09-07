# [H] Cross-Site Request Forgery in JFinalCMS via the component /admin/friend_link/save

## Summary
Severity: High
Advisory: GHSA-r2wj-mxvh-wqfh
CVE: CVE-2023-49379
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-r2wj-mxvh-wqfh
Type: github-advisory

## Affected
- Maven: `com.jfinal:jfinal` — affected >=0

## Details
JFinalCMS v5.0.0 was discovered to contain a Cross-Site Request Forgery (CSRF) vulnerability via the component /admin/friend_link/save.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49379
- https://github.com/cui2shark/cms/blob/main/There%20is%20a%20CSRF%20in%20the%20new%20location%20of%20the%20friendship%20link.md
