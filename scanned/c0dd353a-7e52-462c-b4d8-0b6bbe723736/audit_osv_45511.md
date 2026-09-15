# [M] JLSEC-2026-1256

## Summary
Severity: Medium
Advisory: JLSEC-2026-1256
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/JLSEC-2026-1256
Type: osv

## Affected
- Julia: `LibModbus_jll` — affected >=0 <3.1.10+0

## Details
An invalid pointer in the `modbus_receive()` function of libmodbus v3.1.6 allows attackers to cause a Denial of Service (DoS) via a crafted message sent to the unit-test-server.

## References
- https://github.com/stephane/libmodbus/issues/750
- https://github.com/stephane/libmodbus/issues/750
- https://lists.debian.org/debian-lts-announce/2025/03/msg00010.html
