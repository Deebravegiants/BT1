# [C] MyBatis-Plus vulnerable to SQL injection via TenantPlugin

## Summary
Severity: Critical
Advisory: GHSA-32qq-m9fh-f74w
CVE: CVE-2023-25330
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-32qq-m9fh-f74w
Type: github-advisory

## Affected
- Maven: `com.baomidou:mybatis-plus` — affected >=0 <3.5.3.1

## Details
MyBatis-Plus below 3.5.3.1 is vulnerable to SQL injection via the tenant ID value. This may allow remote attackers to execute arbitrary SQL commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25330
- https://baomidou.com/reference/about-cve
- https://github.com/FCncdn/MybatisPlusTenantPluginSQLInjection-POC/blob/master/Readme.en.md
- https://github.com/baomidou/mybatis-plus
