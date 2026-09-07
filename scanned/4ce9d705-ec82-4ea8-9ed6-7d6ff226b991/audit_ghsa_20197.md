# [H] Path traversal in CureKit

## Summary
Severity: High
Advisory: GHSA-m9vj-44f3-78xw
CVE: CVE-2022-23082
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-01
Source: https://github.com/advisories/GHSA-m9vj-44f3-78xw
Type: github-advisory

## Affected
- Maven: `io.whitesource:curekit` — affected >=1.0.1 <1.1.4

## Details
CureKit versions v1.0.1 through v1.1.3 are vulnerable to path traversal as the function `isFileOutsideDir` fails to sanitize the user input which may lead to path traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23082
- https://github.com/whitesource/CureKit/commit/af35e870ed09411d2f1fae6db1b04598cd1a31b6
- https://github.com/whitesource/CureKit
- https://www.mend.io/vulnerability-database/CVE-2022-23082
