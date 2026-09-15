# [H] tornado AsyncHTTPClient accumulates decompressed chunks without size limit (gzip bomb)

## Summary
Severity: High
Advisory: GHSA-mgf9-4vpg-hj56
CVE: CVE-2026-49855
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-mgf9-4vpg-hj56
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.6

## Details
Tornado's gzip decompression routines work in limited-size chunks, but have no overall limit for the total size of decompressed chunks that they will accumulate (There has always been a limit for the total *compressed* size). This allows a malicious server to consume effectively unlimited amounts of memory if it is accessed via SimpleAsyncHTTPClient in its default configuration. `HTTPServer` is not affected in its default configuration, but it is if `decompress_request=True` is set.

This bug is fixed in Tornado 6.5.6. `max_body_size` is now checked both for the compressed and cumulative decompressed size of the response.

Prior to upgrading, this issue can be mitigated by setting `decompress_response=False` or using `CurlAsyncHTTPClient`.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-mgf9-4vpg-hj56
- https://github.com/tornadoweb/tornado
