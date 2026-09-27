# [H] Memory exhaustion in query parameter parsing in net/url

## Summary
Severity: High
Advisory: BIT-golang-2025-61726
Aliases: CVE-2025-61726, GO-2026-4341
Ecosystem: Bitnami
Published: 2026-01-31
Source: https://osv.dev/vulnerability/BIT-golang-2025-61726
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.6

## Details
The net/url package does not set a limit on the number of query parameters in a query. While the maximum size of query parameters in URLs is generally limited by the maximum request header size, the net/http.Request.ParseForm method can parse large URL-encoded forms. Parsing a large form containing many unique query parameters can cause excessive memory consumption.

## References
- https://go.dev/cl/736712
- https://go.dev/issue/77101
- https://groups.google.com/g/golang-announce/c/Vd2tYVM8eUc
- https://nvd.nist.gov/vuln/detail/CVE-2025-61726
- https://pkg.go.dev/vuln/GO-2026-4341
- https://access.redhat.com/errata/RHSA-2026:10096
- https://access.redhat.com/errata/RHSA-2026:10104
- https://access.redhat.com/errata/RHSA-2026:10184
- https://access.redhat.com/errata/RHSA-2026:10225
- https://access.redhat.com/errata/RHSA-2026:10250
- https://access.redhat.com/errata/RHSA-2026:11408
- https://access.redhat.com/errata/RHSA-2026:11414
- https://access.redhat.com/errata/RHSA-2026:11747
- https://access.redhat.com/errata/RHSA-2026:11749
- https://access.redhat.com/errata/RHSA-2026:12028
- https://access.redhat.com/errata/RHSA-2026:12029
- https://access.redhat.com/errata/RHSA-2026:12030
- https://access.redhat.com/errata/RHSA-2026:12031
- https://access.redhat.com/errata/RHSA-2026:12032
- https://access.redhat.com/errata/RHSA-2026:12033
