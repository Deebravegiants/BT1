# [C] Code execution vulnerability in SWIG code generation in cmd/go

## Summary
Severity: Critical
Advisory: BIT-golang-2026-27140
Aliases: CVE-2026-27140, GO-2026-4871
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-golang-2026-27140
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.2

## Details
SWIG file names containing 'cgo' and well-crafted payloads could lead to code smuggling and arbitrary code execution at build time due to trust layer bypass.

## References
- https://go.dev/cl/763768
- https://go.dev/issue/78335
- https://groups.google.com/g/golang-announce/c/0uYbvbPZRWU
- https://nvd.nist.gov/vuln/detail/CVE-2026-27140
- https://pkg.go.dev/vuln/GO-2026-4871
- https://access.redhat.com/errata/RHSA-2026:10217
- https://access.redhat.com/errata/RHSA-2026:10219
- https://access.redhat.com/errata/RHSA-2026:10704
- https://access.redhat.com/errata/RHSA-2026:16021
- https://access.redhat.com/errata/RHSA-2026:16024
- https://access.redhat.com/errata/RHSA-2026:16494
- https://access.redhat.com/errata/RHSA-2026:16497
- https://access.redhat.com/errata/RHSA-2026:16498
- https://access.redhat.com/errata/RHSA-2026:16694
- https://access.redhat.com/errata/RHSA-2026:16697
- https://access.redhat.com/errata/RHSA-2026:16698
- https://access.redhat.com/errata/RHSA-2026:23246
- https://access.redhat.com/errata/RHSA-2026:25182
- https://access.redhat.com/security/cve/CVE-2026-27140
- https://bugzilla.redhat.com/show_bug.cgi?id=2456341
