# [M] h2o is vulnerable to heap overrun

## Summary
Severity: Medium
Advisory: CVE-2026-44452
Aliases: GHSA-w68q-rqwx-7wvq
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-44452
Type: osv

## Details
h2o is an HTTP server with support for HTTP/1.x, HTTP/2 and HTTP/3. Prior to commit 8dc37cb, when h2o receives a ClientHello message over TLS or QUIC and it contains a zero-length SNI extension, the h2o server runs over the zero-length hostname while trying to copy the hostname, assuming that it is NULL-terminated. This is a potential denial-of-service attack vector in sense that it might trigger segmentation violation. This issue has been fixed by commit 8dc37cb.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44452.json
- https://github.com/h2o/h2o/security/advisories/GHSA-w68q-rqwx-7wvq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44452
- https://github.com/h2o/h2o/commit/8dc37cb1e6171f7f772667618ea440696fed82c3
