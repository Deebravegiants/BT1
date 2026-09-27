# [H] Apache StreamPark uses a Weak Encryption Algorithm

## Summary
Severity: High
Advisory: GHSA-749j-2hp6-8cxm
CVE: CVE-2025-54981
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-749j-2hp6-8cxm
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=2.0.0 <2.1.7

## Details
Weak Encryption Algorithm in StreamPark, The use of an AES cipher in ECB mode and a weak random number generator for encrypting sensitive data, including JWT tokens, may have risked exposing sensitive authentication data

This issue affects Apache StreamPark: from 2.0.0 before 2.1.7.

Users are recommended to upgrade to version 2.1.7, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54981
- https://github.com/apache/streampark/commit/39034db0c806168afa82e58e4f376e1e3c3b73e4
- https://github.com/apache/streampark
- https://lists.apache.org/thread/9rbvdvwg5fdhzjdgyrholgso53r26998
- http://www.openwall.com/lists/oss-security/2025/12/12/4
