# [H] Spring AOP functionality (Struts) vulnerable to DoS attack

## Summary
Severity: High
Advisory: GHSA-8mr5-h28g-36qx
CVE: CVE-2017-9787
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-8mr5-h28g-36qx
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.3.7 <2.3.33
- Maven: `org.apache.struts:struts2-core` — affected >=2.5.0 <2.5.12

## Details
When using a Spring AOP functionality to secure Struts actions it is possible to perform a DoS attack. Solution is to upgrade to Apache Struts version 2.5.12 or 2.3.33.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9787
- https://github.com/apache/struts/commit/086b63735527d4bb0c1dd0d86a7c0374b825ff2
- https://github.com/apache/struts/commit/0d6442bab5b44d93c4c2e63c5335f0a331333b9
- https://lists.apache.org/thread.html/3795c4dd46d9ec75f4a6eb9eca11c11edd3e796c6c1fd7b17b5dc50d@%3Cannouncements.struts.apache.org%3E
- https://lists.apache.org/thread.html/de3d325f0433cd3b42258b6a302c0d7a72b69eedc1480ed561d3b065@%3Cannouncements.struts.apache.org%3E
- https://security.netapp.com/advisory/ntap-20180706-0002
- https://web.archive.org/web/20170910013819/http://www.securitytracker.com/id/1039115
- https://web.archive.org/web/20200227144723/http://www.securityfocus.com/bid/99562
- http://struts.apache.org/docs/s2-049.html
- http://www.oracle.com/technetwork/security-advisory/alert-cve-2017-9805-3889403.html
