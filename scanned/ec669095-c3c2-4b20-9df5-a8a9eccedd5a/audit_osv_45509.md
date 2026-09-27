# [H] JLSEC-2026-1253

## Summary
Severity: High
Advisory: JLSEC-2026-1253
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/JLSEC-2026-1253
Type: osv

## Affected
- Julia: `LibModbus_jll` — affected >=3.1.10+0 <3.1.12+0

## Details
libmodbus v3.1.10 is vulnerable to Buffer Overflow via the `modbus_write_bits` function. This issue can be triggered when the function is fed with specially crafted input, which leads to out-of-bounds read and can potentially cause a crash or other unintended behaviors.

## References
- https://github.com/stephane/libmodbus/issues/743
- https://github.com/stephane/libmodbus/issues/743
