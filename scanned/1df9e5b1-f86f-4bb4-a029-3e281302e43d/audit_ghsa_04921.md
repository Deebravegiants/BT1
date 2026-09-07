# [M] Apache Answer has an Improper Neutralization of Alternate XSS Syntax vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hmr2-99jm-8x45
CVE: CVE-2026-25688
CWE: CWE-87
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-hmr2-99jm-8x45
Type: github-advisory

## Affected
- Go: `github.com/apache/incubator-answer` — affected >=0 <1.7.2-0.20260525024654-2746bf5b455f

## Details
Improper Neutralization of Alternate XSS Syntax vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.0.

AI-generated response content was rendered in the browser without proper sanitization, allowing malicious scripts to be executed when the content was viewed.
Users are recommended to upgrade to version 2.0.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25688
- https://github.com/apache/answer
- https://lists.apache.org/thread/x42joj43rqb38ms5q60f7bgq3qbo7t5q
- http://www.openwall.com/lists/oss-security/2026/06/09/7
