# [M] JLSEC-2026-708

## Summary
Severity: Medium
Advisory: JLSEC-2026-708
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:H/SC:L/SI:L/SA:L/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-708
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Heap Overflow in TLS 1.3 ECH parsing. An integer underflow existed in ECH extension parsing logic when calculating a buffer length, which resulted in writing beyond the bounds of an allocated buffer. Note that in wolfSSL, ECH is off by default, and the ECH standard is still evolving.

## References
- https://github.com/wolfSSL/wolfssl/pull/9817
