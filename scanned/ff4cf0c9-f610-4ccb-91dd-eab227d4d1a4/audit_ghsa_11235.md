# [M] Apache Livy: Unauthorized directory access

## Summary
Severity: Medium
Advisory: GHSA-h84f-4ff9-8hc3
CVE: CVE-2025-66249
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-h84f-4ff9-8hc3
Type: github-advisory

## Affected
- Maven: `org.apache.livy:livy-server` — affected >=0.3.0-incubating <0.9.0-incubating

## Details
Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') vulnerability in Apache Livy.

This issue affects Apache Livy: from 0.3.0 before 0.9.0.

The vulnerability can only be exploited with non-default Apache Livy Server settings. If the configuration value "livy.file.local-dir-whitelist" is set to a non-default value, the directory checking can be bypassed.

Users are recommended to upgrade to version 0.9.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66249
- https://github.com/apache/incubator-livy
- https://lists.apache.org/thread/1xwphsfn4jbtym4k4o0zlvwfogwqwwc3
- http://www.openwall.com/lists/oss-security/2026/03/12/2
