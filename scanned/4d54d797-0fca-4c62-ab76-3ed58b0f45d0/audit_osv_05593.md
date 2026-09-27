# [H] BIT-golang-2022-27536

## Summary
Severity: High
Advisory: BIT-golang-2022-27536
Aliases: CVE-2022-27536, GO-2022-0434
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-27536
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.1

## Details
Certificate.Verify in crypto/x509 in Go 1.18.x before 1.18.1 can be caused to panic on macOS when presented with certain malformed certificates. This allows a remote TLS server to cause a TLS client to panic.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-744259.pdf
- https://groups.google.com/g/golang-announce
- https://groups.google.com/g/golang-announce/c/oecdBNLOml8
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20230309-0001/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27536
