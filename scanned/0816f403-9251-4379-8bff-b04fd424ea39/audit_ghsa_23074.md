# [H] Apache Struts RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-876p-4wgc-75rx
CVE: CVE-2016-0785
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-876p-4wgc-75rx
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.3.20.3
- Maven: `org.apache.struts:struts2-core` — affected >=2.3.24 <2.3.24.3

## Details
Apache Struts 2.x before 2.3.20.3, 2.3.24.3, and 2.3.28 allows remote attackers to execute arbitrary code via a `%{}` sequence in a tag attribute, aka forced double OGNL evaluation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0785
- https://github.com/apache/struts/commit/15857a69e7baf3675804495a5954cd0756ac8364
- https://github.com/apache/struts
- https://web.archive.org/web/20210123095715/http://www.securityfocus.com/bid/85066
- https://web.archive.org/web/20220118185853/http://www.securitytracker.com/id/1035271
- http://struts.apache.org/docs/s2-029.html
