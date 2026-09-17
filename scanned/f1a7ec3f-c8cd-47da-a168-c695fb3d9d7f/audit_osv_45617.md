# [C] JLSEC-2026-1381

## Summary
Severity: Critical
Advisory: JLSEC-2026-1381
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/JLSEC-2026-1381
Type: osv

## Affected
- Julia: `Mongoose_jll` — affected unspecified

## Details
Mongoose is an embedded web server and network library. Priro to version 7.22, a remote unauthenticated attacker can send an HTTP request containing both Content-Length and Transfer-Encoding: chunked. The `cl_count` and `te_count` checks in the `mg_http_parse()` and `http_cb()` paths in `src/http.c` accept both headers and prioritize chunked encoding, while a Content-Length-preferring reverse proxy can use a different request boundary. This CL.TE desynchronization can inject requests that access or modify resources in another user context. This issue is fixed in version 7.22.

## References
- https://github.com/cesanta/mongoose/commit/a9df523f76f43a38bd53b4232b9cfd4c16869e71
- https://github.com/cesanta/mongoose/pull/3611
- https://github.com/cesanta/mongoose/releases/tag/7.22
- https://github.com/cesanta/mongoose/security/advisories/GHSA-5wfq-r6mr-wqp6
