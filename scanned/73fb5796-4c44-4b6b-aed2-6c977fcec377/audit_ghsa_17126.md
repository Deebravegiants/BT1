# [H] Apache Archiva Incorrect Authorization vulnerability

## Summary
Severity: High
Advisory: GHSA-rv4h-m4wc-v99w
CVE: CVE-2024-27138
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-03-01
Source: https://github.com/advisories/GHSA-rv4h-m4wc-v99w
Type: github-advisory

## Affected
- Maven: `org.apache.archiva:archiva` — affected >=0

## Details
** UNSUPPORTED WHEN ASSIGNED ** Incorrect Authorization vulnerability in Apache Archiva.

Apache Archiva has a setting to disable user registration, however this restriction can be bypassed. As Apache Archiva has been retired, we do not expect to release a version of Apache Archiva that fixes this issue. You are recommended to look into migrating to a different solution, or isolate your instance from any untrusted users.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27138
- https://github.com/apache/archiva
- https://lists.apache.org/thread/070qcpclcb3sqk1hn8j5lvzohp30k1m2
- http://www.openwall.com/lists/oss-security/2024/03/01/4
