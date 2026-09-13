# [H] Payload size limit bypass via gzip decompression in ContentReader (streaming) allows oversized request bodies in cpp-httplib

## Summary
Severity: High
Advisory: CVE-2026-28435
Aliases: GHSA-xvfx-w463-6fpp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-28435
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. Prior to 0.35.0, cpp-httplib (httplib.h) does not enforce Server::set_payload_max_length() on the decompressed request body when using HandlerWithContentReader (streaming ContentReader) with Content-Encoding: gzip (or other supported encodings). A small compressed payload can expand beyond the configured payload limit and be processed by the application, enabling a payload size limit bypass and potential denial of service (CPU/memory exhaustion). This vulnerability is fixed in 0.35.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28435.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-xvfx-w463-6fpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-28435
- https://github.com/yhirose/cpp-httplib/commit/c99d7472b5cf4869d3897b9afc9792063a3d15a8
