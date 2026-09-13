# [H] Apache StreamPark contains an Incorrect Execution-Assigned Permissions vulnerability

## Summary
Severity: High
Advisory: GHSA-6wwv-6mm3-pp76
CVE: CVE-2025-30001
CWE: CWE-279
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-6wwv-6mm3-pp76
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=0

## Details
Incorrect Execution-Assigned Permissions vulnerability in Apache StreamPark. This issue affects Apache StreamPark: from 2.1.4 before 2.1.6. Users are recommended to upgrade to version 2.1.6, which fixes the issue. Version 2.1.6 has yet to be published in the Maven registry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30001
- https://github.com/apache/streampark
- https://lists.apache.org/thread/xfmsvhkcnr1831n0w5ovy3p44lsmfb7m
- http://www.openwall.com/lists/oss-security/2025/09/04/1
