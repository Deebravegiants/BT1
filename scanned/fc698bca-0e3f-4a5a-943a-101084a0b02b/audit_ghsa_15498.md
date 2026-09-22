# [C] Apache Seata Deserialization of Untrusted Data vulnerability

## Summary
Severity: Critical
Advisory: GHSA-3xq2-w6j4-c99r
CVE: CVE-2024-22399
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-3xq2-w6j4-c99r
Type: github-advisory

## Affected
- Maven: `org.apache.seata:seata-core` — affected >=2.0.0 <2.1.0
- Maven: `org.apache.seata:seata-core` — affected >=1.0.0 <1.8.1

## Details
Deserialization of Untrusted Data vulnerability in Apache Seata. 

When developers disable authentication on the Seata-Server and do not use the Seata client SDK dependencies, they may construct uncontrolled serialized malicious requests by directly sending bytecode based on the Seata private protocol.

This issue affects Apache Seata: 2.0.0, from 1.0.0 through 1.8.0.

Users are recommended to upgrade to version 2.1.0/1.8.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22399
- https://github.com/apache/incubator-seata
- https://lists.apache.org/thread/91nzzlxyj4nmks85gbzwkkjtbmnmlkc4
