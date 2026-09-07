# [H] Apache Neethi does not properly detect circular references in policy definitions.

## Summary
Severity: High
Advisory: GHSA-2hfh-9h53-qc24
CVE: CVE-2026-42403
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-01
Source: https://github.com/advisories/GHSA-2hfh-9h53-qc24
Type: github-advisory

## Affected
- Maven: `org.apache.neethi:neethi` — affected >=0 <3.2.2

## Details
Apache Neethi does not properly detect circular references in policy definitions. When a WS-Policy document contains circular policy references (where Policy A references Policy B which references Policy A), the policy normalization process can enter an infinite loop or cause excessive recursion, leading to a stack overflow or application hang. An attacker can craft malicious policy documents with circular references to cause a Denial of Service condition

Users are recommended to upgrade to version 3.2.2, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42403
- https://github.com/apache/ws-neethi
- https://lists.apache.org/thread/zm6t8skkkskjwk1881l4m4n0l7dqclzo
- http://www.openwall.com/lists/oss-security/2026/05/01/7
