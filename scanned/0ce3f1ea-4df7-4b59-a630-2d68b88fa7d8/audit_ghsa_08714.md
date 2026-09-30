# [H] Apache Ignite REST API Has a Relative Path Traversal Vulnerability

## Summary
Severity: High
Advisory: GHSA-v45h-mqf4-6939
CVE: CVE-2025-48977
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-v45h-mqf4-6939
Type: github-advisory

## Affected
- Maven: `org.apache.ignite:ignite-core` — affected >=2.0.0 <2.18.0

## Details
Relative Path Traversal vulnerability in Apache Ignite REST API.

Authenticated REST API users can read any file on the server with "cmd=log" command and a log path crafted in a certain way.
This issue affects Apache Ignite: from 2.0.0 through 2.17.0.

Users are recommended to upgrade to version 2.18.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48977
- https://github.com/apache/ignite/commit/5c42c7a303937844179ad470edb35c1ad1cee6ab
- https://github.com/apache/ignite
- https://lists.apache.org/thread/hgct6918sowd8l58yjohryhpxx81t4n1
- http://www.openwall.com/lists/oss-security/2026/05/28/3
