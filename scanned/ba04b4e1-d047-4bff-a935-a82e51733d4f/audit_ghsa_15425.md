# [H] Apache Linkis arbitrary file deletion vulnerability

## Summary
Severity: High
Advisory: GHSA-j6vx-r77h-44wc
CVE: CVE-2024-27182
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-08-02
Source: https://github.com/advisories/GHSA-j6vx-r77h-44wc
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis` — affected >=0 <1.6.0

## Details
In Apache Linkis <= 1.5.0, Arbitrary file deletion in Basic management services on a user with an administrator account could delete any file accessible by the Linkis system user. Users are recommended to upgrade to version 1.6.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27182
- https://github.com/apache/linkis
- https://lists.apache.org/thread/2of1p433h8rbq2bx525rtftnk19oz38h
- http://www.openwall.com/lists/oss-security/2024/08/02/4
