# [H] Incorrect enforcement of email constraints in crypto/x509

## Summary
Severity: High
Advisory: BIT-golang-2026-27137
Aliases: CVE-2026-27137, GO-2026-4599
Ecosystem: Bitnami
Published: 2026-03-10
Source: https://osv.dev/vulnerability/BIT-golang-2026-27137
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.1

## Details
When verifying a certificate chain which contains a certificate containing multiple email address constraints which share common local portions but different domain portions, these constraints will not be properly applied, and only the last constraint will be considered.

## References
- https://go.dev/cl/752182
- https://go.dev/issue/77952
- https://groups.google.com/g/golang-announce/c/EdhZqrQ98hk
- https://nvd.nist.gov/vuln/detail/CVE-2026-27137
- https://pkg.go.dev/vuln/GO-2026-4599
- https://access.redhat.com/errata/RHSA-2026:10125
- https://access.redhat.com/errata/RHSA-2026:10158
- https://access.redhat.com/errata/RHSA-2026:10169
- https://access.redhat.com/errata/RHSA-2026:10175
- https://access.redhat.com/errata/RHSA-2026:10184
- https://access.redhat.com/errata/RHSA-2026:10225
- https://access.redhat.com/errata/RHSA-2026:10250
- https://access.redhat.com/errata/RHSA-2026:10929
- https://access.redhat.com/errata/RHSA-2026:11800
- https://access.redhat.com/errata/RHSA-2026:13545
- https://access.redhat.com/errata/RHSA-2026:14879
- https://access.redhat.com/errata/RHSA-2026:19022
- https://access.redhat.com/errata/RHSA-2026:19049
- https://access.redhat.com/errata/RHSA-2026:19132
- https://access.redhat.com/errata/RHSA-2026:19181
