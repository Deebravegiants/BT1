# [H] go-resolver vulnerable to attacker-controlled domains due to unvalidated RRSIG RRs

## Summary
Severity: High
Advisory: GHSA-87mm-qxm5-cp3f
CVE: CVE-2022-3346
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-87mm-qxm5-cp3f
Type: github-advisory

## Affected
- Go: `github.com/peterzen/goresolver` — affected >=0

## Details
go-resolver's DNSSEC validation is not performed correctly. An attacker can cause this package to report successful validation for invalid, attacker-controlled records. The owner name of RRSIG RRs is not validated, permitting an attacker to present the RRSIG for an attacker-controlled domain in a response for any other domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3346
- https://github.com/peterzen/goresolver/issues/5
- https://github.com/peterzen/goresolver
- https://pkg.go.dev/vuln/GO-2022-0979
