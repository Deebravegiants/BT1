# [M] Apache SkyWalking has a stored XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v6x2-4q87-rf82
CVE: CVE-2025-54057
CWE: CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-27
Source: https://github.com/advisories/GHSA-v6x2-4q87-rf82
Type: github-advisory

## Affected
- Maven: `org.apache.skywalking:apm-webapp` — affected >=0

## Details
There is an Improper Neutralization of Script-Related HTML Tags in a Web Page (Basic XSS) vulnerability in Apache SkyWalking.

This issue affects Apache SkyWalking versions <= 10.2.0.

Users are recommended to upgrade to version 10.3.0, which fixes the issue. Version 10.3.0 has not been uploaded to the Maven registry at time of publish, please see [release notes](https://github.com/apache/skywalking/releases/tag/v10.3.0) for download instructions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54057
- https://github.com/apache/skywalking
- https://lists.apache.org/thread/sl2x2tx8y007x0mo746yddx2lvnv9tcr
- http://www.openwall.com/lists/oss-security/2025/11/27/1
- http://www.openwall.com/lists/oss-security/2026/04/13/3
