# [H] Path Traversal in github.com/flipped-aurora/gin-vue-admin

## Summary
Severity: High
Advisory: CVE-2022-24843
Aliases: GHSA-32gq-gj42-mw43
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-13
Source: https://osv.dev/vulnerability/CVE-2022-24843
Type: osv

## Details
Gin-vue-admin is a backstage management system based on vue and gin, which separates the front and rear of the full stack. Gin-vue-admin 2.50 has arbitrary file read vulnerability due to a lack of parameter validation. This has been resolved in version 2.5.1. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24843.json
- https://github.com/flipped-aurora/gin-vue-admin/security/advisories/GHSA-32gq-gj42-mw43
- https://nvd.nist.gov/vuln/detail/CVE-2022-24843
- https://github.com/flipped-aurora/gin-vue-admin/issues/1002
- https://github.com/flipped-aurora/gin-vue-admin/pull/1024
