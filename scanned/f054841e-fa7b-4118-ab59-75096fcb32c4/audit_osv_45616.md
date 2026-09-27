# [C] JLSEC-2026-1380

## Summary
Severity: Critical
Advisory: JLSEC-2026-1380
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/JLSEC-2026-1380
Type: osv

## Affected
- Julia: `Mongoose_jll` — affected unspecified

## Details
Mongoose is an embedded web server and network library. Prior to 7.22, a remote unauthenticated attacker can exploit an HTTP/1.0 reverse-proxy deployment by sending a request with Transfer-Encoding: chunked and conflicting framing. The `http_cb()` function in `src/http.c` tests hm.proto.len with an impossible greater-than-eight condition even though `mg_http_parse()` requires an eight-byte protocol string, so `is_http_1_0` is never set. Mongoose consequently processes chunked encoding that an HTTP/1.0 proxy can ignore, enabling request smuggling and unauthorized access or state changes. This issue is fixed in version 7.22.

## References
- https://github.com/cesanta/mongoose/commit/a9df523f76f43a38bd53b4232b9cfd4c16869e71
- https://github.com/cesanta/mongoose/pull/3611
- https://github.com/cesanta/mongoose/releases/tag/7.22
- https://github.com/cesanta/mongoose/security/advisories/GHSA-mgp5-rjrv-h5j3
