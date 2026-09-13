# [H] Ignore unrelated, unauthenticated hashes in Lookup in golang.org/x/mod/sumdb

## Summary
Severity: High
Advisory: BIT-golang-2026-56864
Aliases: CVE-2026-56864, GO-2026-6180
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-golang-2026-56864
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.27.0-0 <1.27.0

## Details
A malicious GOSUMDB was capable of serving arbitrary module content not contained within the transparency log. This attack allows for a coordinating GOPROXY and GOSUMDB to serve a client malicious module content that cannot be detected by evaluating the transparency log. In order to determine if you have been affected: rm -r go.sum go.work.sum vendor/ && go mod tidy

## References
- https://go.dev/cl/815000
- https://go.dev/cl/815020
- https://go.dev/issue/80745
- https://groups.google.com/g/golang-announce/c/94pEornpRlI
- https://nvd.nist.gov/vuln/detail/CVE-2026-56864
- https://pkg.go.dev/vuln/GO-2026-6180
