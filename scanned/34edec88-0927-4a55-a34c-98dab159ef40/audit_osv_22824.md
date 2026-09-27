# [H] Ree6 vulnerable to SQL Injection

## Summary
Severity: High
Advisory: CVE-2022-39303
Aliases: GHSA-69xv-xjfw-4pv8
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-13
Source: https://osv.dev/vulnerability/CVE-2022-39303
Type: osv

## Details
Ree6 is a moderation bot. This vulnerability allows manipulation of SQL queries. This issue has been patched in version 1.7.0 by using Javas PreparedStatements, which allow object setting without the risk of SQL injection. There are currently no known workarounds.

## References
- https://github.com/Ree6-Applications/Ree6/compare/1.6.4...1.7.
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39303.json
- https://github.com/Ree6-Applications/Ree6/security/advisories/GHSA-69xv-xjfw-4pv8
- https://nvd.nist.gov/vuln/detail/CVE-2022-39303
