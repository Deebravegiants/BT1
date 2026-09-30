# [H] Excessive memory allocation in net/http and net/textproto

## Summary
Severity: High
Advisory: BIT-golang-2023-24534
Aliases: CVE-2023-24534, GO-2023-1704
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-24534
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.3

## Details
HTTP and MIME header parsing can allocate large amounts of memory, even when parsing small inputs, potentially leading to a denial of service. Certain unusual patterns of input data can cause the common function used to parse HTTP and MIME headers to allocate substantially more memory than required to hold the parsed headers. An attacker can exploit this behavior to cause an HTTP server to allocate large amounts of memory from a small request, potentially leading to memory exhaustion and a denial of service. With fix, header parsing now correctly allocates only the memory required to hold parsed headers.

## References
- https://go.dev/cl/481994
- https://go.dev/issue/58975
- https://groups.google.com/g/golang-announce/c/Xdv6JL9ENs8
- https://pkg.go.dev/vuln/GO-2023-1704
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20230526-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2023-24534
