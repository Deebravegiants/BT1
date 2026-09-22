# [M] Memory exhaustion in multipart form parsing in net/textproto and net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2023-45290
Aliases: CVE-2023-45290, GO-2024-2599
Ecosystem: Bitnami
Published: 2024-03-12
Source: https://osv.dev/vulnerability/BIT-golang-2023-45290
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.22.0-0 <1.22.1

## Details
When parsing a multipart form (either explicitly with Request.ParseMultipartForm or implicitly with Request.FormValue, Request.PostFormValue, or Request.FormFile), limits on the total size of the parsed form were not applied to the memory consumed while reading a single form line. This permits a maliciously crafted input containing very long lines to cause allocation of arbitrarily large amounts of memory, potentially leading to memory exhaustion. With fix, the ParseMultipartForm function now correctly limits the maximum size of form lines.

## References
- https://go.dev/cl/569341
- https://go.dev/issue/65383
- https://groups.google.com/g/golang-announce/c/5pwGVUPoMbg
- https://pkg.go.dev/vuln/GO-2024-2599
- https://security.netapp.com/advisory/ntap-20240329-0004/
- http://www.openwall.com/lists/oss-security/2024/03/08/4
- https://nvd.nist.gov/vuln/detail/CVE-2023-45290
