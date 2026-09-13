# [H] Quadratic string concatentation in consumeComment in net/mail

## Summary
Severity: High
Advisory: BIT-golang-2026-39820
Aliases: CVE-2026-39820, GO-2026-4986
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-golang-2026-39820
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.3

## Details
Well-crafted inputs reaching ParseAddress, ParseAddressList, and ParseDate were able to trigger excessive CPU exhaustion and memory allocations.

## References
- https://go.dev/cl/759940
- https://go.dev/issue/78566
- https://groups.google.com/g/golang-announce/c/qcCIEXso47M
- https://nvd.nist.gov/vuln/detail/CVE-2026-39820
- https://pkg.go.dev/vuln/GO-2026-4986
- https://access.redhat.com/errata/RHSA-2026:33120
- https://access.redhat.com/errata/RHSA-2026:33123
- https://access.redhat.com/errata/RHSA-2026:33142
- https://access.redhat.com/errata/RHSA-2026:33150
- https://access.redhat.com/errata/RHSA-2026:33574
- https://access.redhat.com/errata/RHSA-2026:34364
- https://access.redhat.com/security/cve/CVE-2026-39820
- https://bugzilla.redhat.com/show_bug.cgi?id=2467820
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-39820.json
- https://access.redhat.com/errata/RHSA-2026:36319
- https://access.redhat.com/errata/RHSA-2026:36625
- https://access.redhat.com/errata/RHSA-2026:36754
- https://access.redhat.com/errata/RHSA-2026:36797
- https://access.redhat.com/errata/RHSA-2026:23262
- https://access.redhat.com/errata/RHSA-2026:23264
