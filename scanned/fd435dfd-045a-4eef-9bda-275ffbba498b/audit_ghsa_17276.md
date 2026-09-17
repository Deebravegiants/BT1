# [H] urllib3 streaming API improperly handles highly compressed data

## Summary
Severity: High
Advisory: GHSA-2xpw-w6gg-jr37
CVE: CVE-2025-66471
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-12-05
Source: https://github.com/advisories/GHSA-2xpw-w6gg-jr37
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=1.0 <2.6.0

## Details
### Impact

urllib3's [streaming API](https://urllib3.readthedocs.io/en/2.5.0/advanced-usage.html#streaming-and-i-o) is designed for the efficient handling of large HTTP responses by reading the content in chunks, rather than loading the entire response body into memory at once.

When streaming a compressed response, urllib3 can perform decoding or decompression based on the HTTP `Content-Encoding` header (e.g., `gzip`, `deflate`, `br`, or `zstd`). The library must read compressed data from the network and decompress it until the requested chunk size is met. Any resulting decompressed data that exceeds the requested amount is held in an internal buffer for the next read operation.

The decompression logic could cause urllib3 to fully decode a small amount of highly compressed data in a single operation. This can result in excessive resource consumption (high CPU usage and massive memory allocation for the decompressed data; CWE-409) on the client side, even if the application only requested a small chunk of data.


### Affected usages

Applications and libraries using urllib3 version 2.5.0 and earlier to stream large compressed responses or content from untrusted sources.

`stream()`, `read(amt=256)`, `read1(amt=256)`, `read_chunked(amt=256)`, `readinto(b)` are examples of `urllib3.HTTPResponse` method calls using the affected logic unless decoding is disabled explicitly.


### Remediation

Upgrade to at least urllib3 v2.6.0 in which the library avoids decompressing data that exceeds the requested amount.

If your environment contains a package facilitating the Brotli encoding, upgrade to at least Brotli 1.2.0 or brotlicffi 1.2.0.0 too. These versions are enforced by the `urllib3[brotli]` extra in the patched versions of urllib3.


### Credits

The issue was reported by @Cycloctane.
Supplemental information was provided by @stamparm during a security audit performed by [7ASecurity](https://7asecurity.com/) and facilitated by [OSTIF](https://ostif.org/).

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-2xpw-w6gg-jr37
- https://nvd.nist.gov/vuln/detail/CVE-2025-66471
- https://github.com/urllib3/urllib3/commit/c19571de34c47de3a766541b041637ba5f716ed7
- https://github.com/urllib3/urllib3
