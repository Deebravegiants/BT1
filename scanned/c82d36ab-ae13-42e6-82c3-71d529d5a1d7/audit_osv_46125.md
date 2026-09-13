# [M] Protection mechanism failure in wolfCrypt post-quantum implementations (ML-KEM and ML-DSA) in...

## Summary
Severity: Medium
Advisory: JLSEC-2026-705
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:P/AC:H/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:L/SI:L/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:Amber)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-705
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
Protection mechanism failure in wolfCrypt post-quantum implementations (ML-KEM and ML-DSA) in wolfSSL on ARM Cortex-M microcontrollers allows a physical attacker to compromise key material and/or cryptographic outcomes via induced transient faults that corrupt or redirect seed/pointer values during Keccak-based expansion.

This issue affects wolfSSL (wolfCrypt): commit hash d86575c766e6e67ef93545fa69c04d6eb49400c6.

## References
- https://github.com/advisories/GHSA-pgc5-r6cv-2825
- https://github.com/wolfSSL/wolfssl/pull/9734
- https://nvd.nist.gov/vuln/detail/CVE-2026-3503
