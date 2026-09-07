# [M] Apache Felix Webconsole: XSS in services console

## Summary
Severity: Medium
Advisory: GHSA-4c37-7m5h-c8m9
CVE: CVE-2025-25247
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-02-10
Source: https://github.com/advisories/GHSA-4c37-7m5h-c8m9
Type: github-advisory

## Affected
- Maven: `org.apache.felix:org.apache.felix.webconsole` — affected >=4.0.0 <4.9.10
- Maven: `org.apache.felix:org.apache.felix.webconsole` — affected >=5.0.0 <5.0.10

## Details
Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in Apache Felix Webconsole.

This issue affects Apache Felix Webconsole 4.x up to 4.9.8 and 5.x up to 5.0.8.

Users are recommended to upgrade to version 4.9.10 or 5.0.10 or higher, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25247
- https://github.com/apache/felix-dev/commit/87513ea3533fdb79d9e2b251410bf2bfbd63941e
- https://github.com/apache/felix-dev
- https://lists.apache.org/thread/z47jbf0rbylzd0ktfzdw9c8b5fpyl24m
- http://www.openwall.com/lists/oss-security/2025/02/10/1
