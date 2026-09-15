# [M] Apache StreamPark LDAP Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pjfj-qvqw-3f6v
CVE: CVE-2022-45801
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-01
Source: https://github.com/advisories/GHSA-pjfj-qvqw-3f6v
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=1.0.0 <2.0.0

## Details
Apache StreamPark versions 1.0.0 to 2.0.0 have an LDAP injection vulnerability. LDAP Injection is an attack used to exploit web based applications that construct LDAP statements based on user input. When an application fails to properly sanitize user input, it's possible to modify LDAP statements through techniques similar to SQL Injection. LDAP injection attacks could result in the granting of permissions to unauthorized queries, and content modification inside the LDAP tree. This risk may only occur when the user logs in with ldap, and the user name and password login will not be affected, Users of the affected versions should upgrade to Apache StreamPark 2.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45801
- https://github.com/apache/incubator-streampark
- https://lists.apache.org/thread/xbkwwpkp3n2rs2wcxg8l26mhsftxwwr9
