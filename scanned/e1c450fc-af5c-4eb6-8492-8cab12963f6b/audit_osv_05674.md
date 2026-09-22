# [H] Arbitrary file write using cgo pkg-config directive in cmd/go

## Summary
Severity: High
Advisory: BIT-golang-2025-61731
Aliases: CVE-2025-61731, GO-2026-4339
Ecosystem: Bitnami
Published: 2026-01-31
Source: https://osv.dev/vulnerability/BIT-golang-2025-61731
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.6

## Details
Building a malicious file with cmd/go can cause can cause a write to an attacker-controlled file with partial control of the file content. The "#cgo pkg-config:" directive in a Go source file provides command-line arguments to provide to the Go pkg-config command. An attacker can provide a "--log-file" argument to this directive, causing pkg-config to write to an attacker-controlled location.

## References
- https://go.dev/cl/736711
- https://go.dev/issue/77100
- https://groups.google.com/g/golang-announce/c/Vd2tYVM8eUc
- https://nvd.nist.gov/vuln/detail/CVE-2025-61731
- https://pkg.go.dev/vuln/GO-2026-4339
- https://access.redhat.com/errata/RHSA-2026:12118
- https://access.redhat.com/errata/RHSA-2026:12282
- https://access.redhat.com/errata/RHSA-2026:13736
- https://access.redhat.com/errata/RHSA-2026:14100
- https://access.redhat.com/errata/RHSA-2026:14774
- https://access.redhat.com/errata/RHSA-2026:15091
- https://access.redhat.com/errata/RHSA-2026:20088
- https://access.redhat.com/errata/RHSA-2026:21691
- https://access.redhat.com/errata/RHSA-2026:3556
- https://access.redhat.com/errata/RHSA-2026:3559
- https://access.redhat.com/errata/RHSA-2026:3855
- https://access.redhat.com/errata/RHSA-2026:4434
- https://access.redhat.com/errata/RHSA-2026:5133
- https://access.redhat.com/errata/RHSA-2026:5907
- https://access.redhat.com/errata/RHSA-2026:5941
