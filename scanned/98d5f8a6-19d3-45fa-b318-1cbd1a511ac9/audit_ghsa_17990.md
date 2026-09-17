# [M] Apache Zeppelin: Missing Origin Validation in WebSockets vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xg8j-j6vp-6h5w
CVE: CVE-2024-51775
CWE: CWE-1385
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-03
Source: https://github.com/advisories/GHSA-xg8j-j6vp-6h5w
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-shell` — affected >=0.11.1 <0.12.0

## Details
Missing Origin Validation in WebSockets vulnerability in Apache Zeppelin.

The attacker could access the Zeppelin server from another origin without any restriction, and get internal information about paragraphs. 
This issue affects Apache Zeppelin: from 0.11.1 before 0.12.0.

Users are recommended to upgrade to version 0.12.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-51775
- https://github.com/apache/zeppelin/pull/4823
- https://github.com/apache/zeppelin
- http://www.openwall.com/lists/oss-security/2025/08/03/5
