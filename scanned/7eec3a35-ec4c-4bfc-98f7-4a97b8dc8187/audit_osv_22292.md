# [H] SQL Injection in github.com/flipped-aurora/gin-vue-admin

## Summary
Severity: High
Advisory: CVE-2022-24844
Aliases: GHSA-5g92-6hpp-w425
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-13
Source: https://osv.dev/vulnerability/CVE-2022-24844
Type: osv

## Details
Gin-vue-admin is a backstage management system based on vue and gin, which separates the front and rear of the full stack. The problem occurs in the following code in server/service/system/sys_auto_code_pgsql.go, which means that PostgreSQL must be used as the database for this vulnerability to occur. Users must: Require JWT login） and be using PostgreSQL to be affected. This issue has been resolved in version 2.5.1. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24844.json
- https://github.com/flipped-aurora/gin-vue-admin/security/advisories/GHSA-5g92-6hpp-w425
- https://nvd.nist.gov/vuln/detail/CVE-2022-24844
- https://github.com/flipped-aurora/gin-vue-admin/pull/1024
