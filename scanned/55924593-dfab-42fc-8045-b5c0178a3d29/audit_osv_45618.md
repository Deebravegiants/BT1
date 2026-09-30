# [M] JLSEC-2026-1382

## Summary
Severity: Medium
Advisory: JLSEC-2026-1382
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/JLSEC-2026-1382
Type: osv

## Affected
- Julia: `Mongoose_jll` — affected unspecified

## Details
Mongoose is an embedded web server and network library. Prior to 7.22, a remote attacker can place a lone carriage return or line feed in multipart input processed by `mg_http_next_multipart()` in `src/http.c`. The loops comparing s[b] and s[b + 1], and s[h2] and s[h2 + 1], use an incorrect AND condition and stop when either character resembles part of a CRLF terminator. This truncates headers, filenames, or boundaries and can cause an application to accept dangerous content after seeing a misleading Content-Type value. This issue is fixed in version 7.22.

## References
- https://github.com/cesanta/mongoose/commit/a9df523f76f43a38bd53b4232b9cfd4c16869e71
- https://github.com/cesanta/mongoose/pull/3611
- https://github.com/cesanta/mongoose/releases/tag/7.22
- https://github.com/cesanta/mongoose/security/advisories/GHSA-cc55-8v3r-59p8
