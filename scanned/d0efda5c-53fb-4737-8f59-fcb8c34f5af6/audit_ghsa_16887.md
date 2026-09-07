# [M] Apache HugeGraph-Hubble: SSRF in Hubble connection page

## Summary
Severity: Medium
Advisory: GHSA-77x4-55q7-4vmj
CVE: CVE-2024-27347
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-22
Source: https://github.com/advisories/GHSA-77x4-55q7-4vmj
Type: github-advisory

## Affected
- Maven: `org.apache.hugegraph:hugegraph-hubble` — affected >=1.0.0 <1.3.0

## Details
Server-Side Request Forgery (SSRF) vulnerability in Apache HugeGraph-Hubble. This issue affects Apache HugeGraph-Hubble: from 1.0.0 before 1.3.0.

Users are recommended to upgrade to version 1.3.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27347
- https://github.com/apache/incubator-hugegraph-toolchain
- https://lists.apache.org/thread/z0v71148slfkw60hsp35pl7ddjyvg01l
- http://www.openwall.com/lists/oss-security/2024/04/22/2
