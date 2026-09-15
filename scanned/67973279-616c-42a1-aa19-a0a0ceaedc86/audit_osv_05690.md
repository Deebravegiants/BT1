# [H] Infinite loop in HTTP/2 transport when given bad SETTINGS_MAX_FRAME_SIZE in net/http/internal/http2 in golang.org/x/net

## Summary
Severity: High
Advisory: BIT-golang-2026-33814
Aliases: CVE-2026-33814, GO-2026-4918
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-golang-2026-33814
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.3

## Details
When processing HTTP/2 SETTINGS frames, transport will enter an infinite loop of writing CONTINUATION frames if it receives a SETTINGS_MAX_FRAME_SIZE with a value of 0.

## References
- https://go.dev/cl/761581
- https://go.dev/cl/761640
- https://go.dev/issue/78476
- https://groups.google.com/g/golang-announce/c/qcCIEXso47M
- https://nvd.nist.gov/vuln/detail/CVE-2026-33814
- https://pkg.go.dev/vuln/GO-2026-4918
- https://access.redhat.com/errata/RHSA-2026:23262
- https://access.redhat.com/errata/RHSA-2026:23264
- https://access.redhat.com/errata/RHSA-2026:33120
- https://access.redhat.com/errata/RHSA-2026:33123
- https://access.redhat.com/errata/RHSA-2026:33142
- https://access.redhat.com/errata/RHSA-2026:33150
- https://access.redhat.com/errata/RHSA-2026:34342
- https://access.redhat.com/security/cve/CVE-2026-33814
- https://bugzilla.redhat.com/show_bug.cgi?id=2467815
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33814.json
- https://access.redhat.com/errata/RHSA-2026:37387
- https://access.redhat.com/errata/RHSA-2026:42644
- https://access.redhat.com/errata/RHSA-2026:43692
- https://access.redhat.com/errata/RHSA-2026:50205
