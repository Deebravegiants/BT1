# [M] Fault injection attack with ML-DSA and ML-KEM on ARM

## Summary
Severity: Medium
Advisory: CVE-2026-3503
CVSS: 6.0 (CVSS:4.0/AV:P/AC:H/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:L/SI:L/SA:N/U:Amber)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-3503
Type: osv

## Details
Protection mechanism failure in wolfCrypt post-quantum implementations (ML-KEM and ML-DSA) in wolfSSL on ARM Cortex-M microcontrollers allows a physical attacker to compromise key material and/or cryptographic outcomes via induced transient faults that corrupt or redirect seed/pointer values during Keccak-based expansion.




This issue affects wolfSSL (wolfCrypt): commit hash d86575c766e6e67ef93545fa69c04d6eb49400c6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3503.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3503
- https://github.com/wolfSSL/wolfssl/pull/9734
- https://github.com/wolfSSL/wolfssl
