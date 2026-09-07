# [C] MyBatis PageHelper vulnerable to time-blind SQL injection via orderBy parameter

## Summary
Severity: Critical
Advisory: GHSA-w559-623p-vfg8
CVE: CVE-2022-28111
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-w559-623p-vfg8
Type: github-advisory

## Affected
- Maven: `com.github.pagehelper:pagehelper` — affected >=3.5.0 <5.3.1

## Details
MyBatis PageHelper versions 3.5.x through 5.3.x were discovered to contain a time-blind SQL injection vulnerability via the orderBy parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28111
- https://github.com/pagehelper/Mybatis-PageHelper/issues/674
- https://github.com/pagehelper/Mybatis-PageHelper/commit/554a524af2d2b30d09505516adc412468a84d8fa
- https://github.com/pagehelper/Mybatis-PageHelper
- https://github.com/pagehelper/Mybatis-PageHelper.git
- https://github.com/yangfar/CVE/blob/main/CVE-2022-42227.md
- https://pagehelper.github.io
- https://www.cnblogs.com/secload/articles/16061420.html
