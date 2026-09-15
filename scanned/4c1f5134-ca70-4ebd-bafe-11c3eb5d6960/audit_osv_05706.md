# [H] Fix transparency log tile verification bypass in golang.org/x/mod/sumdb/tlog

## Summary
Severity: High
Advisory: BIT-golang-2026-56865
Aliases: CVE-2026-56865, GO-2026-6179
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-golang-2026-56865
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.27.0-0 <1.27.0

## Details
A malicious GOPROXY was previously capable of forging up to two sumdb tiles that allow for a requested module to bypass the GOSUMDB check and persist attacker-controlled module content to a local Go module cache. This attack allows for a malicious GOPROXY to serve malicious module content that cannot be detected by evaluating the transparency log. All tiles are now correctly verified against their parents. In order to determine if you have been affected: rm -r go.sum go.work.sum vendor/ && go mod tidy

## References
- https://go.dev/cl/814960
- https://go.dev/cl/815020
- https://go.dev/issue/80744
- https://groups.google.com/g/golang-announce/c/94pEornpRlI
- https://nvd.nist.gov/vuln/detail/CVE-2026-56865
- https://pkg.go.dev/vuln/GO-2026-6179
