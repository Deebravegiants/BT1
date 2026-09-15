# [H] urllib3: Decompression-bomb safeguards bypassed in parts of the streaming API

## Summary
Severity: High
Advisory: GHSA-mf9v-mfxr-j63j
CVE: CVE-2026-44432
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-mf9v-mfxr-j63j
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=2.6.0 <2.7.0

## Details
### Impact

urllib3's [streaming API](https://urllib3.readthedocs.io/en/2.7.0/advanced-usage.html#streaming-and-i-o) is designed for the efficient handling of large HTTP responses by reading the content in chunks, rather than loading the entire response body into memory at once.

urllib3 can perform decompression based on the HTTP `Content-Encoding` header (e.g., `gzip`, `deflate`, `br`, or `zstd`). When using the streaming API since version 2.6.0, the library decompresses only the necessary bytes, enabling partial content consumption.

However, urllib3 before version 2.7.0 could still decompress the whole response instead of the requested portion in two cases:
1. During the second `HTTPResponse.read(amt=N)` call when the response was decompressed using the official [Brotli](https://pypi.org/project/brotli/) library.
2. When `HTTPResponse.drain_conn()` was called after the response had been read and decompressed partially (compression algorithm did not matter here).

These issues could cause urllib3 to fully decode a small amount of highly compressed data in a single operation. This could result in excessive resource consumption (high CPU usage and massive memory allocation for the decompressed data; CWE-409) on the client side.


### Affected usages

Applications and libraries using urllib3 versions earlier than 2.7.0 may be affected when streaming compressed responses from untrusted sources in either of these cases, unless decompression is explicitly disabled:

1. A response encoded with `br` is read incrementally with at least two `HTTPResponse.read(amt=N)` or `HTTPResponse.stream(amt=N)` calls while using the official [Brotli](https://pypi.org/project/brotli/) library.
2. `HTTPResponse.drain_conn()` is called after response decompression has already started.


### Remediation

Upgrade to at least urllib3 version 2.7.0 in which the library:
1. Is more efficient for reads with Brotli.
2. Always skips decompression for `HTTPResponse.drain_conn()`.

If upgrading is not immediately possible, the following workarounds may reduce exposure in specific cases:
1. For the Brotli-specific issue only, switch from [brotli](https://pypi.org/project/brotli/) to [brotlicffi](https://pypi.org/project/brotlicffi/) until you can upgrade urllib3; the official Brotli package is affected because of https://github.com/google/brotli/issues/1396.
2. If your code explicitly calls `HTTPResponse.drain_conn()`, call `HTTPResponse.close()` instead when connection reuse is not important.


### Credits

The Brotli-specific issue was reported by @kimkou2024.
`HTTPResponse.drain_conn()` inefficiency was reported by @Cycloctane.

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-mf9v-mfxr-j63j
- https://nvd.nist.gov/vuln/detail/CVE-2026-44432
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2026-142.yaml
- https://github.com/urllib3/urllib3
