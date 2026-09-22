# [H] JLSEC-2026-1255

## Summary
Severity: High
Advisory: JLSEC-2026-1255
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/JLSEC-2026-1255
Type: osv

## Affected
- Julia: `LibModbus_jll` — affected >=0 <3.1.10+0

## Details
libmodbus v3.1.6 was discovered to contain a use-after-free via the ctx->backend pointer. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted message sent to the unit-test-server.

## References
- https://github.com/stephane/libmodbus/issues/749
- https://github.com/stephane/libmodbus/issues/749
- https://lists.debian.org/debian-lts-announce/2025/03/msg00010.html
