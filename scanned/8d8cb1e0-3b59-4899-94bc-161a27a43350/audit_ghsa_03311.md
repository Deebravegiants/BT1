# [H] Uncaught Exception leading to Denial of Service in json-sanitizer

## Summary
Severity: High
Advisory: GHSA-8rf5-92jh-3vc9
CVE: CVE-2021-23900
CWE: CWE-248
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-13
Source: https://github.com/advisories/GHSA-8rf5-92jh-3vc9
Type: github-advisory

## Affected
- Maven: `com.mikesamuel:json-sanitizer` — affected >=0 <1.2.2

## Details
OWASP json-sanitizer before 1.2.2 can output invalid JSON or throw an undeclared exception for crafted input. This may lead to denial of service if the application is not prepared to handle these situations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23900
- https://github.com/OWASP/json-sanitizer/commit/a37f594f7378a1c76b3283e0dab9e1ab1dc0247e
- https://github.com/OWASP/json-sanitizer/compare/v1.2.1...v1.2.2
- https://groups.google.com/g/json-sanitizer-support/c/dAW1AeNMoA0
