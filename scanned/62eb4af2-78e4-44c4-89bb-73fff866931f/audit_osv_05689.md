# [H] Crash when handling long CNAME response in net

## Summary
Severity: High
Advisory: BIT-golang-2026-33811
Aliases: CVE-2026-33811, GO-2026-4981
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-golang-2026-33811
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.3

## Details
When using LookupCNAME with the cgo DNS resolver, a very long CNAME response can trigger a double-free of C memory and a crash.

## References
- https://go.dev/cl/767860
- https://go.dev/issue/78803
- https://groups.google.com/g/golang-announce/c/qcCIEXso47M
- https://nvd.nist.gov/vuln/detail/CVE-2026-33811
- https://pkg.go.dev/vuln/GO-2026-4981
- https://access.redhat.com/errata/RHSA-2026:23262
- https://access.redhat.com/errata/RHSA-2026:23264
- https://access.redhat.com/errata/RHSA-2026:33120
- https://access.redhat.com/errata/RHSA-2026:33123
- https://access.redhat.com/errata/RHSA-2026:33142
- https://access.redhat.com/errata/RHSA-2026:33150
- https://access.redhat.com/errata/RHSA-2026:33574
- https://access.redhat.com/errata/RHSA-2026:34357
- https://access.redhat.com/errata/RHSA-2026:34359
- https://access.redhat.com/errata/RHSA-2026:34364
- https://access.redhat.com/security/cve/CVE-2026-33811
- https://bugzilla.redhat.com/show_bug.cgi?id=2467822
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33811.json
- https://access.redhat.com/errata/RHSA-2026:35832
- https://access.redhat.com/errata/RHSA-2026:35993
