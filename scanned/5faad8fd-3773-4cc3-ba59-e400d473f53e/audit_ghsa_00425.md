# [H] Deserialization of Untrusted Data in swagger-codegen

## Summary
Severity: High
Advisory: GHSA-vgvf-9jh3-fg75
CVE: CVE-2017-1000207
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-vgvf-9jh3-fg75
Type: github-advisory

## Affected
- Maven: `io.swagger:swagger-parser` — affected >=0 <1.0.31
- Maven: `io.swagger:swagger-codegen` — affected >=0 <2.2.2

## Details
A vulnerability in Swagger-Parser's version <= 1.0.30 and Swagger codegen version <= 2.2.2 yaml parsing functionality results in arbitrary code being executed when a maliciously crafted yaml Open-API specification is parsed. This in particular, affects the 'generate' and 'validate' command in swagger-codegen (<= 2.2.2) and can lead to arbitrary code being executed when these commands are used on a well-crafted yaml specification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000207
- https://github.com/swagger-api/swagger-parser/pull/481
- https://github.com/advisories/GHSA-vgvf-9jh3-fg75
- https://github.com/swagger-api/swagger-parser
- https://lgtm.com/blog/swagger_snakeyaml_CVE-2017-1000207_CVE-2017-1000208
