# [H] Use of a Broken or Risky Cryptographic Algorithm in Max Mazurov Maddy

## Summary
Severity: High
Advisory: GHSA-5r5w-h76p-m726
CVE: CVE-2021-42583
CWE: CWE-327
Ecosystem: Go
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-5r5w-h76p-m726
Type: github-advisory

## Affected
- Go: `github.com/foxcpp/maddy` — affected >=0 <0.5.2

## Details
A Broken or Risky Cryptographic Algorithm exists in Max Mazurov Maddy before 0.5.2, which is an unnecessary risk that may result in the exposure of sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42583
- https://github.com/foxcpp/maddy
- https://github.com/foxcpp/maddy/blob/df40dce1284cd0fd0a9e8e7894029553d653d0a5/internal/auth/shadow/verify.go
- https://github.com/foxcpp/maddy/releases/tag/v0.5.2
