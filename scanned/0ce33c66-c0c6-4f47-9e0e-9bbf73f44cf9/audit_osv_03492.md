# [H] ALPINE-CVE-2026-21441

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-21441
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-21441
Type: osv

## Affected
- Alpine:v3.20: `py3-urllib3` — affected >=0 <1.26.18-r2
- Alpine:v3.21: `py3-urllib3` — affected >=0 <1.26.20-r1
- Alpine:v3.22: `py3-urllib3` — affected >=0 <1.26.20-r1
- Alpine:v3.23: `py3-urllib3` — affected >=0 <2.6.3-r0
- Alpine:v3.24: `py3-urllib3` — affected >=0 <2.6.3-r0

## Details
urllib3 is an HTTP client library for Python. urllib3's streaming API is designed for the efficient handling of large HTTP responses by reading the content in chunks, rather than loading the entire response body into memory at once. urllib3 can perform decoding or decompression based on the HTTP `Content-Encoding` header (e.g., `gzip`, `deflate`, `br`, or `zstd`). When using the streaming API, the library decompresses only the necessary bytes, enabling partial content consumption. Starting in version 1.22 and prior to version 2.6.3, for HTTP redirect responses, the library would read the entire response body to drain the connection and decompress the content unnecessarily. This decompression occurred even before any read methods were called, and configured read limits did not restrict the amount of decompressed data. As a result, there was no safeguard against decompression bombs. A malicious server could exploit this to trigger excessive resource consumption on the client. Applications and libraries are affected when they stream content from untrusted sources by setting `preload_content=False` when they do not disable redirects. Users should upgrade to at least urllib3 v2.6.3, in which the library does not decode content of redirect responses when `preload_content=False`. If upgrading is not immediately possible, disable redirects by setting `redirect=False` for requests to untrusted source.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-21441
