# [C] Apache HugeGraph-Server: Fixed JWT Token (Secret)

## Summary
Severity: Critical
Advisory: GHSA-f697-gm3h-xrf9
CVE: CVE-2024-43441
CWE: CWE-302
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-24
Source: https://github.com/advisories/GHSA-f697-gm3h-xrf9
Type: github-advisory

## Affected
- Maven: `org.apache.hugegraph:hugegraph-server` — affected >=1.0.0 <1.5.0

## Details
Authentication Bypass by Assumed-Immutable Data vulnerability in Apache HugeGraph-Server.

This issue affects Apache HugeGraph-Server: from 1.0.0 before 1.5.0.

Users are recommended to upgrade to version 1.5.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43441
- https://github.com/apache/incubator-hugegraph/commit/03b40a52446218c83e98cb43020e0593a744a246
- https://github.com/apache/incubator-hugegraph
- https://lists.apache.org/thread/h2607yv32wgcrywov960jpxhvsmmlf12
- http://www.openwall.com/lists/oss-security/2024/12/24/2
