# [M] Mongoose: Multipart boundary/header scan logic error in mg_http_next_multipart

## Summary
Severity: Medium
Advisory: CVE-2026-73258
Aliases: GHSA-cc55-8v3r-59p8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-73258
Type: osv

## Details
Mongoose is an embedded web server and network library. Prior to 7.22, a remote attacker can place a lone carriage return or line feed in multipart input processed by mg_http_next_multipart() in src/http.c. The loops comparing s[b] and s[b + 1], and s[h2] and s[h2 + 1], use an incorrect AND condition and stop when either character resembles part of a CRLF terminator. This truncates headers, filenames, or boundaries and can cause an application to accept dangerous content after seeing a misleading Content-Type value. This issue is fixed in version 7.22.

## References
- https://github.com/cesanta/mongoose/releases/tag/7.22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73258.json
- https://github.com/cesanta/mongoose/security/advisories/GHSA-cc55-8v3r-59p8
- https://nvd.nist.gov/vuln/detail/CVE-2026-73258
- https://github.com/cesanta/mongoose/commit/a9df523f76f43a38bd53b4232b9cfd4c16869e71
- https://github.com/cesanta/mongoose/pull/3611
