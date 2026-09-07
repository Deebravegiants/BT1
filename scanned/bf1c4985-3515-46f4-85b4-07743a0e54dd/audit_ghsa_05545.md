# [H] Apache Linkis: Arbitrary File Read via Double URL Encoding Bypass

## Summary
Severity: High
Advisory: GHSA-c399-q49h-qwc8
CVE: CVE-2025-29847
CWE: CWE-177, CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-19
Source: https://github.com/advisories/GHSA-c399-q49h-qwc8
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis` — affected >=1.3.0 <1.8.0

## Details
A vulnerability in Apache Linkis.

Problem Description

When using the JDBC engine and data source functionality, if the URL parameter configured on the frontend has undergone multiple rounds of URL encoding, it may bypass the system's checks. This bypass can trigger a vulnerability that allows unauthorized access to system files via JDBC parameters.

Scope of Impact


This issue affects Apache Linkis: from 1.3.0 through 1.7.0.

Severity level


moderate
Solution
Continuously check if the connection information contains the "%" character; if it does, perform URL decoding.

Users are recommended to upgrade to version 1.8.0, which fixes the issue.




More questions about this vulnerability can be discussed here:  https://lists.apache.org/list?dev@linkis.apache.org:2025-9:cve

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-29847
- https://github.com/apache/linkis
- https://lists.apache.org/list?dev@linkis.apache.org:2025-9:cve
- https://lists.apache.org/thread/03l5rfkgdt022o75jp8x4tzpqxz8g057
- http://www.openwall.com/lists/oss-security/2025/09/19/2
