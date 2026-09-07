# [H] go-resolver's DNSSEC validation not performed correctly

## Summary
Severity: High
Advisory: GHSA-jr65-gpj5-cw74
CVE: CVE-2022-3347
CWE: CWE-345, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-jr65-gpj5-cw74
Type: github-advisory

## Affected
- Go: `github.com/peterzen/goresolver` — affected >=0

## Details
go-resolver's DNSSEC validation is not performed correctly. An attacker can cause this package to report successful validation for invalid, attacker-controlled records. Root DNSSEC public keys are not validated, permitting an attacker to present a self-signed root key and delegation chain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3347
- https://github.com/peterzen/goresolver/issues/5#issuecomment-1150214257
- https://github.com/peterzen/goresolver
- https://pkg.go.dev/vuln/GO-2022-1026
