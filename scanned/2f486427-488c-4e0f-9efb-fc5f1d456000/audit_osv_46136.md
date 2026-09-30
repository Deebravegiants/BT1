# [M] JLSEC-2026-717

## Summary
Severity: Medium
Advisory: JLSEC-2026-717
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:L/VA:N/SC:H/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-717
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
URI nameConstraints from constrained intermediate CAs are parsed but not enforced during certificate chain verification in `wolfcrypt/src/asn.c`. A compromised or malicious sub-CA could issue leaf certificates with URI SAN entries that violate the nameConstraints of the issuing CA, and wolfSSL would accept them as valid.

## References
- https://github.com/wolfSSL/wolfssl/pull/10048
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2410
