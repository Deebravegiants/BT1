# [M] janino vulnerable to denial of service due to stack overflow

## Summary
Severity: Medium
Advisory: GHSA-gcg6-xv4f-f749
CVE: CVE-2023-33546
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-01
Source: https://github.com/advisories/GHSA-gcg6-xv4f-f749
Type: github-advisory

## Affected
- Maven: `org.codehaus.janino:janino-parent` — affected >=0

## Details
janino 3.1.9 and earlier is subject to denial of service (DOS) attacks when using the expression `evaluator.guess` parameter name method. If the parser runs on user-supplied input, an attacker could supply content that causes the parser to crash due to a stack overflow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33546
- https://github.com/janino-compiler/janino/issues/201
- https://github.com/janino-compiler/janino
- https://janino-compiler.github.io/janino/#security
