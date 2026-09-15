# [H] Missing hash/digest size and OID checks allow digests smaller than allowed when verifying ECDSA...

## Summary
Severity: High
Advisory: JLSEC-2026-716
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:H/SI:L/SA:L/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:Red)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-716
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Missing hash/digest size and OID checks allow digests smaller than allowed when verifying ECDSA certificates, or smaller than is appropriate for the relevant key type, to be accepted by signature verification functions. This could lead to reduced security of ECDSA certificate-based authentication if the public CA key used is also known. This affects ECDSA/ECC verification when EdDSA or ML-DSA is also enabled.

## References
- https://github.com/advisories/GHSA-f5h9-5q52-qrx7
- https://github.com/wolfSSL/wolfssl/pull/10131
- https://nvd.nist.gov/vuln/detail/CVE-2026-5194
- https://www.anthropic.com/research/glasswing-initial-update
