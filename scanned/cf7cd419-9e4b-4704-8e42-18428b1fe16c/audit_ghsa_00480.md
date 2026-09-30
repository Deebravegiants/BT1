# [M] Apache Struts Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9gp7-jvm2-r4mx
CVE: CVE-2017-7672
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-9gp7-jvm2-r4mx
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.5.0 <2.5.12

## Details
If an application allows enter an URL in a form field and built-in URLValidator is used, it is possible to prepare a special URL which will be used to overload server process when performing validation of the URL. Solution is to upgrade to Apache Struts version 2.5.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7672
- https://github.com/apache/struts
- https://lists.apache.org/thread.html/3795c4dd46d9ec75f4a6eb9eca11c11edd3e796c6c1fd7b17b5dc50d@%3Cannouncements.struts.apache.org%3E
- https://security.netapp.com/advisory/ntap-20180706-0002
- https://web.archive.org/web/20170907215142/http://www.securitytracker.com/id/1039114
- https://web.archive.org/web/20200227144724/http://www.securityfocus.com/bid/99563
- http://struts.apache.org/docs/s2-047.html
- http://www.oracle.com/technetwork/security-advisory/alert-cve-2017-9805-3889403.html
