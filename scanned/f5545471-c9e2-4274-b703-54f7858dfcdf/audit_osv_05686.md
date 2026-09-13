# [H] Unauthenticated TLS 1.3 KeyUpdate record can cause persistent connection retention and DoS in crypto/tls

## Summary
Severity: High
Advisory: BIT-golang-2026-32283
Aliases: CVE-2026-32283, GO-2026-4870
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-golang-2026-32283
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.2

## Details
If one side of the TLS connection sends multiple key update messages post-handshake in a single record, the connection can deadlock, causing uncontrolled consumption of resources. This can lead to a denial of service. This only affects TLS 1.3.

## References
- https://go.dev/cl/763767
- https://go.dev/issue/78334
- https://groups.google.com/g/golang-announce/c/0uYbvbPZRWU
- https://nvd.nist.gov/vuln/detail/CVE-2026-32283
- https://pkg.go.dev/vuln/GO-2026-4870
- https://access.redhat.com/errata/RHSA-2026:10217
- https://access.redhat.com/errata/RHSA-2026:10219
- https://access.redhat.com/errata/RHSA-2026:10704
- https://access.redhat.com/errata/RHSA-2026:11507
- https://access.redhat.com/errata/RHSA-2026:11514
- https://access.redhat.com/errata/RHSA-2026:11704
- https://access.redhat.com/errata/RHSA-2026:11711
- https://access.redhat.com/errata/RHSA-2026:11712
- https://access.redhat.com/errata/RHSA-2026:11863
- https://access.redhat.com/errata/RHSA-2026:11881
- https://access.redhat.com/errata/RHSA-2026:14162
- https://access.redhat.com/errata/RHSA-2026:14200
- https://access.redhat.com/errata/RHSA-2026:14391
- https://access.redhat.com/errata/RHSA-2026:15980
- https://access.redhat.com/errata/RHSA-2026:16021
