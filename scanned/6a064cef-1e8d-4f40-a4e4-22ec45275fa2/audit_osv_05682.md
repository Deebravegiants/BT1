# [H] Inefficient candidate hostname parsing in crypto/x509

## Summary
Severity: High
Advisory: BIT-golang-2026-27145
Aliases: CVE-2026-27145, GO-2026-5037
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-golang-2026-27145
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.4

## Details
(*x509.Certificate).VerifyHostname previously called matchHostnames in a loop over all DNS Subject Alternative Name (SAN) entries. This caused strings.Split(host, ".") to execute repeatedly on the same input hostname. With a large DNS SAN list, verification costs scaled quadratically based on the number of SAN entries multiplied by the hostname's label count. Because x509.Verify validates hostnames before building the certificate chain, this overhead occurred even for untrusted certificates.

## References
- https://go.dev/cl/783621
- https://go.dev/issue/79694
- https://groups.google.com/g/golang-announce/c/tKs3rmcBcKw
- https://nvd.nist.gov/vuln/detail/CVE-2026-27145
- https://pkg.go.dev/vuln/GO-2026-5037
- https://access.redhat.com/errata/RHSA-2026:33574
- https://access.redhat.com/errata/RHSA-2026:34357
- https://access.redhat.com/errata/RHSA-2026:34359
- https://access.redhat.com/security/cve/CVE-2026-27145
- https://bugzilla.redhat.com/show_bug.cgi?id=2484207
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27145.json
- https://access.redhat.com/errata/RHSA-2026:35832
- https://access.redhat.com/errata/RHSA-2026:36317
- https://access.redhat.com/errata/RHSA-2026:36648
- https://access.redhat.com/errata/RHSA-2026:29981
- https://access.redhat.com/errata/RHSA-2026:36797
- https://access.redhat.com/errata/RHSA-2026:38995
- https://access.redhat.com/errata/RHSA-2026:39005
- https://access.redhat.com/errata/RHSA-2026:39573
- https://access.redhat.com/errata/RHSA-2026:23262
