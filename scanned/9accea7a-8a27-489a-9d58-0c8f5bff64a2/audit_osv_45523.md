# [M] JLSEC-2026-1270

## Summary
Severity: Medium
Advisory: JLSEC-2026-1270
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/JLSEC-2026-1270
Type: osv

## Affected
- Julia: `capnproto_jll` — affected unspecified

## Details
Cap'n Proto is a data interchange format and capability-based RPC system. Prior to 1.4.0, when using Transfer-Encoding: chunked, if a chunk's size parsed to a value of 2^64 or larger, it would be truncated to a 64-bit integer. In theory, this bug could enable HTTP request/response smuggling. This vulnerability is fixed in 1.4.0.

## References
- https://capnproto.org/capnproto-c++-1.4.0.tar.gz
- https://capnproto.org/capnproto-c++-win32-1.4.0.zip
- https://github.com/capnproto/capnproto/commit/2744b3c012b4aa3c31cefb61ec656829fa5c0e36
- https://github.com/capnproto/capnproto/commit/e929f0ba7901a6b8f4b5ba9a4db00af43288cbb0
- https://github.com/capnproto/capnproto/security/advisories/GHSA-vpcq-mx5v-32wm
