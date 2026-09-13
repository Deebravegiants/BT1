# [H] Unexpected work during chain building in crypto/x509

## Summary
Severity: High
Advisory: BIT-golang-2026-32280
Aliases: CVE-2026-32280, GO-2026-4947
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-golang-2026-32280
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.2

## Details
During chain building, the amount of work that is done is not correctly limited when a large number of intermediate certificates are passed in VerifyOptions.Intermediates, which can lead to a denial of service. This affects both direct users of crypto/x509 and users of crypto/tls.

## References
- https://go.dev/cl/758320
- https://go.dev/issue/78282
- https://groups.google.com/g/golang-announce/c/0uYbvbPZRWU
- https://nvd.nist.gov/vuln/detail/CVE-2026-32280
- https://pkg.go.dev/vuln/GO-2026-4947
- https://access.redhat.com/errata/RHSA-2026:10217
- https://access.redhat.com/errata/RHSA-2026:10219
- https://access.redhat.com/errata/RHSA-2026:10704
- https://access.redhat.com/errata/RHSA-2026:11507
- https://access.redhat.com/errata/RHSA-2026:11514
- https://access.redhat.com/errata/RHSA-2026:11688
- https://access.redhat.com/errata/RHSA-2026:13545
- https://access.redhat.com/errata/RHSA-2026:13791
- https://access.redhat.com/errata/RHSA-2026:13826
- https://access.redhat.com/errata/RHSA-2026:13829
- https://access.redhat.com/errata/RHSA-2026:14020
- https://access.redhat.com/errata/RHSA-2026:14162
- https://access.redhat.com/errata/RHSA-2026:14200
- https://access.redhat.com/errata/RHSA-2026:14391
- https://access.redhat.com/errata/RHSA-2026:15980
