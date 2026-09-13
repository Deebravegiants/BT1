# [H] Case-sensitive excludedSubtrees name constraints cause Auth Bypass in crypto/x509

## Summary
Severity: High
Advisory: BIT-golang-2026-33810
Aliases: CVE-2026-33810, GO-2026-4866
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-golang-2026-33810
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.2

## Details
When verifying a certificate chain containing excluded DNS constraints, these constraints are not correctly applied to wildcard DNS SANs which use a different case than the constraint. This only affects validation of otherwise trusted certificate chains, issued by a root CA in the VerifyOptions.Roots CertPool, or in the system certificate pool.

## References
- https://go.dev/cl/763763
- https://go.dev/issue/78332
- https://groups.google.com/g/golang-announce/c/0uYbvbPZRWU
- https://nvd.nist.gov/vuln/detail/CVE-2026-33810
- https://pkg.go.dev/vuln/GO-2026-4866
- http://www.openwall.com/lists/oss-security/2026/04/19/4
- http://www.openwall.com/lists/oss-security/2026/04/20/1
- https://access.redhat.com/errata/RHSA-2026:10155
- https://access.redhat.com/errata/RHSA-2026:10158
- https://access.redhat.com/errata/RHSA-2026:13545
- https://access.redhat.com/errata/RHSA-2026:14391
- https://access.redhat.com/errata/RHSA-2026:19135
- https://access.redhat.com/errata/RHSA-2026:19144
- https://access.redhat.com/errata/RHSA-2026:19353
- https://access.redhat.com/errata/RHSA-2026:19719
- https://access.redhat.com/errata/RHSA-2026:19720
- https://access.redhat.com/errata/RHSA-2026:19721
- https://access.redhat.com/errata/RHSA-2026:21769
- https://access.redhat.com/errata/RHSA-2026:21772
- https://access.redhat.com/errata/RHSA-2026:22347
