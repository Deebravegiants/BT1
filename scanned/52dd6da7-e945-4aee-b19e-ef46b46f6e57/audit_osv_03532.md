# [H] ALPINE-CVE-2026-27135

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-27135
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27135
Type: osv

## Affected
- Alpine:v3.21: `nghttp2` — affected >=0 <1.68.1
- Alpine:v3.22: `nghttp2` — affected >=0 <1.68.1
- Alpine:v3.23: `nghttp2` — affected >=0 <1.68.1
- Alpine:v3.24: `nghttp2` — affected >=0 <1.68.1

## Details
nghttp2 is an implementation of the Hypertext Transfer Protocol version 2 in C. Prior to version 1.68.1, the nghttp2 library stops reading the incoming data when user facing public API `nghttp2_session_terminate_session` or `nghttp2_session_terminate_session2` is called by the application. They might be called internally by the library when it detects the situation that is subject to connection error. Due to the missing internal state validation, the library keeps reading the rest of the data after one of those APIs is called. Then receiving a malformed frame that causes FRAME_SIZE_ERROR causes assertion failure. nghttp2 v1.68.1 adds missing state validation to avoid assertion failure. No known workarounds are available.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27135
