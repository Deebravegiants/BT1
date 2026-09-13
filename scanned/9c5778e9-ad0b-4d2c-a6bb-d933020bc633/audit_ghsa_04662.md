# [M] Apache Answer has an Exposure of Private Personal Information to an Unauthorized Actor vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w754-5646-xq9j
CVE: CVE-2026-25699
CWE: CWE-359
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-w754-5646-xq9j
Type: github-advisory

## Affected
- Go: `github.com/apache/incubator-answer` — affected >=0 <1.7.2-0.20260206073245-92994b49976b

## Details
Exposure of Private Personal Information to an Unauthorized Actor vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.0.

Timeline-related APIs lacked proper authorization checks, allowing regular authenticated users to access deleted, private, or unapproved content and its revision history.
Users are recommended to upgrade to version 2.0.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25699
- https://github.com/apache/answer/commit/92994b49976b6206a7000d045d924ec4fd5be1be
- https://github.com/apache/answer
- https://github.com/apache/answer/releases/tag/v2.0.1
- https://lists.apache.org/thread/c36k4hzwhncqo0qfn5fg57f1gkjhyfv8
- http://www.openwall.com/lists/oss-security/2026/06/09/6
