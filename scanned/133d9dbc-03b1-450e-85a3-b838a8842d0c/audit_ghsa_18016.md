# [H] Apache Seata: Deserialization of untrusted Data in Apache Seata Server

## Summary
Severity: High
Advisory: GHSA-g358-g2pq-c46j
CVE: CVE-2025-53606
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-g358-g2pq-c46j
Type: github-advisory

## Affected
- Maven: `org.apache.seata:seata-serializer-fury` — affected >=2.4.0 <2.5.0

## Details
Deserialization of Untrusted Data vulnerability in Apache Seata (incubating).

This issue affects Apache Seata (incubating): 2.4.0.

Users are recommended to upgrade to version 2.5.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53606
- https://github.com/apache/incubator-seata/commit/d2a18aef82c08535e4134642070c39d98654f0f6
- https://github.com/apache/incubator-seata
- https://lists.apache.org/thread/ggfd72vvvxjozs81zbcls45zxg64pphx
- http://www.openwall.com/lists/oss-security/2025/08/07/1
