# [H] urllib3 allows an unbounded number of links in the decompression chain

## Summary
Severity: High
Advisory: GHSA-gm62-xv2j-4w53
CVE: CVE-2025-66418
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-12-05
Source: https://github.com/advisories/GHSA-gm62-xv2j-4w53
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=1.24 <2.6.0

## Details
## Impact

urllib3 supports chained HTTP encoding algorithms for response content according to RFC 9110 (e.g., `Content-Encoding: gzip, zstd`).

However, the number of links in the decompression chain was unbounded allowing a malicious server to insert a virtually unlimited number of compression steps leading to high CPU usage and massive memory allocation for the decompressed data.


## Affected usages

Applications and libraries using urllib3 version 2.5.0 and earlier for HTTP requests to untrusted sources unless they disable content decoding explicitly.


## Remediation

Upgrade to at least urllib3 v2.6.0 in which the library limits the number of links to 5.

If upgrading is not immediately possible, use [`preload_content=False`](https://urllib3.readthedocs.io/en/2.5.0/advanced-usage.html#streaming-and-i-o) and ensure that `resp.headers["content-encoding"]` contains a safe number of encodings before reading the response content.

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-gm62-xv2j-4w53
- https://nvd.nist.gov/vuln/detail/CVE-2025-66418
- https://github.com/urllib3/urllib3/commit/24d7b67eac89f94e11003424bcf0d8f7b72222a8
- https://github.com/urllib3/urllib3
