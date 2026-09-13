# [H] Apache Kyuubi Server vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-f8r6-6222-9pvc
CVE: CVE-2025-66518
CWE: CWE-22, CWE-27
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:L/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-f8r6-6222-9pvc
Type: github-advisory

## Affected
- Maven: `org.apache.kyuubi:kyuubi-server_2.12` — affected >=1.6.0 <1.10.3

## Details
Any client who can access to Apache Kyuubi Server via Kyuubi frontend protocols can bypass server-side config kyuubi.session.local.dir.allow.list and use local files which are not listed in the config.

This issue affects Apache Kyuubi: from 1.6.0 through 1.10.2.

Users are recommended to upgrade to version 1.10.3 or upper, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66518
- https://github.com/apache/kyuubi
- https://lists.apache.org/thread/xp460bwbyzdhho34ljd4nchyt2fmhodl
- http://www.openwall.com/lists/oss-security/2026/01/05/1
