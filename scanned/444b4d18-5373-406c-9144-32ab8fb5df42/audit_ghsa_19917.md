# [M] Apache Felix HTTP Webconsole Plugin:  XSS in HTTP Webconsole Plugin 

## Summary
Severity: Medium
Advisory: GHSA-2cv6-4f2r-jq2c
CVE: CVE-2025-27867
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-2cv6-4f2r-jq2c
Type: github-advisory

## Affected
- Maven: `org.apache.felix:org.apache.felix.http.webconsoleplugin` — affected >=0 <1.2.2

## Details
Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in Apache Felix HTTP Webconsole Plugin.

This issue affects Apache Felix HTTP Webconsole Plugin: from Version 1.X through 1.2.0.

Users are recommended to upgrade to version 1.2.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27867
- https://github.com/apache/felix-dev
- https://lists.apache.org/thread/y83f2rvm8bccr5ctgv7mzxd69p6f77dp
- http://www.openwall.com/lists/oss-security/2025/03/12/3
