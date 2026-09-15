# [H] Decompression-bomb safeguards bypassed when following HTTP redirects (streaming API)

## Summary
Severity: High
Advisory: GHSA-38jv-5279-wg99
CVE: CVE-2026-21441
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-38jv-5279-wg99
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=1.22 <2.6.3

## Details
### Impact

urllib3's [streaming API](https://urllib3.readthedocs.io/en/2.6.2/advanced-usage.html#streaming-and-i-o) is designed for the efficient handling of large HTTP responses by reading the content in chunks, rather than loading the entire response body into memory at once.

urllib3 can perform decoding or decompression based on the HTTP `Content-Encoding` header (e.g., `gzip`, `deflate`, `br`, or `zstd`). When using the streaming API, the library decompresses only the necessary bytes, enabling partial content consumption.

However, for HTTP redirect responses, the library would read the entire response body to drain the connection and decompress the content unnecessarily. This decompression occurred even before any read methods were called, and configured read limits did not restrict the amount of decompressed data. As a result, there was no safeguard against decompression bombs. A malicious server could exploit this to trigger excessive resource consumption on the client (high CPU usage and large memory allocations for decompressed data; CWE-409).

### Affected usages

Applications and libraries using urllib3 version 2.6.2 and earlier to stream content from untrusted sources by setting `preload_content=False` when they do not disable redirects.


### Remediation

Upgrade to at least urllib3 v2.6.3 in which the library does not decode content of redirect responses when `preload_content=False`.

If upgrading is not immediately possible, disable [redirects](https://urllib3.readthedocs.io/en/2.6.2/user-guide.html#retrying-requests) by setting `redirect=False` for requests to untrusted source.

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-38jv-5279-wg99
- https://nvd.nist.gov/vuln/detail/CVE-2026-21441
- https://github.com/urllib3/urllib3/commit/8864ac407bba8607950025e0979c4c69bc7abc7b
- https://github.com/urllib3/urllib3
- https://lists.debian.org/debian-lts-announce/2026/01/msg00017.html
