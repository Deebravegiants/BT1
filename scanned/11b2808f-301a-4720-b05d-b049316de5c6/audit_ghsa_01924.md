# [C] Arbitrary code injection in json-sanitizer

## Summary
Severity: Critical
Advisory: GHSA-mm8j-9x84-m9cv
CVE: CVE-2021-23899
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-mm8j-9x84-m9cv
Type: github-advisory

## Affected
- Maven: `com.mikesamuel:json-sanitizer` — affected >=0 <1.2.2

## Details
OWASP json-sanitizer before 1.2.2 may emit closing SCRIPT tags and CDATA section delimiters for crafted input. This allows an attacker to inject arbitrary HTML or XML into embedding documents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23899
- https://github.com/OWASP/json-sanitizer/commit/a37f594f7378a1c76b3283e0dab9e1ab1dc0247e
- https://github.com/OWASP/json-sanitizer/compare/v1.2.1...v1.2.2
- https://groups.google.com/g/json-sanitizer-support/c/dAW1AeNMoA0
