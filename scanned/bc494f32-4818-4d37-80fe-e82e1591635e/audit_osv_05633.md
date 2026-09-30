# [M] Denial of service via chunk extensions in net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2023-39326
Aliases: CVE-2023-39326, GO-2023-2382
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-39326
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.21.0-0 <1.21.5

## Details
A malicious HTTP sender can use chunk extensions to cause a receiver reading from a request or response body to read many more bytes from the network than are in the body. A malicious HTTP client can further exploit this to cause a server to automatically read a large amount of data (up to about 1GiB) when a handler fails to read the entire body of a request. Chunk extensions are a little-used HTTP feature which permit including additional metadata in a request or response body sent using the chunked encoding. The net/http chunked encoding reader discards this metadata. A sender can exploit this by inserting a large metadata segment with each byte transferred. The chunk reader now produces an error if the ratio of real body to encoded bytes grows too small.

## References
- https://go.dev/cl/547335
- https://go.dev/issue/64433
- https://groups.google.com/g/golang-dev/c/6ypN5EjibjM/m/KmLVYH_uAgAJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UIU6HOGV6RRIKWM57LOXQA75BGZSIH6G/
- https://pkg.go.dev/vuln/GO-2023-2382
- https://nvd.nist.gov/vuln/detail/CVE-2023-39326
