# [M] Apache Santuario - XML Security for Java are vulnerable to private key disclosure

## Summary
Severity: Medium
Advisory: GHSA-xfrj-6vvc-3xm2
CVE: CVE-2023-44483
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-20
Source: https://github.com/advisories/GHSA-xfrj-6vvc-3xm2
Type: github-advisory

## Affected
- Maven: `org.apache.santuario:xmlsec` — affected >=2.3.0 <2.3.4
- Maven: `org.apache.santuario:xmlsec` — affected >=0 <2.2.6
- Maven: `org.apache.santuario:xmlsec` — affected >=3.0.0 <3.0.3

## Details
All versions of Apache Santuario - XML Security for Java prior to 2.2.6, 2.3.4, and 3.0.3, when using the JSR 105 API, are vulnerable to an issue where a private key may be disclosed in log files when generating an XML Signature and logging with debug level is enabled. Users are recommended to upgrade to version 2.2.6, 2.3.4, or 3.0.3, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44483
- https://github.com/apache/santuario-java
- https://lists.apache.org/thread/vmqbp9mfxtrf0kmbnnmbn3h9j6dr9q55
- https://santuario.apache.org/secadv.data/CVE-2023-44483.txt.asc?version=1&modificationDate=1697782758000&api=v2
- https://security.netapp.com/advisory/ntap-20241108-0002
- http://www.openwall.com/lists/oss-security/2023/10/20/5
