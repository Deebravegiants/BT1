# [M] ML-KEM-1024 x64 AVX2 implicit rejection failure in the Fujisaki-Okamoto transform breaks IND-CCA2...

## Summary
Severity: Medium
Advisory: JLSEC-2026-693
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-693
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.7.2+0 <5.9.2+0

## Details
wolfSSL's AVX2-optimized ML-KEM implementation (`mlkem_cmp_avx2`) compares only 1536 of the 1568 ciphertext bytes during the Fujisaki-Okamoto re-encryption check in ML-KEM-1024 decapsulation. Ciphertexts that differ from the expected re-encryption solely in bytes 1536-1567 bypass implicit rejection and are accepted as valid, breaking IND-CCA2 security. An attacker able to submit chosen ciphertexts to a decapsulation oracle that uses a static ML-KEM-1024 key, and to observe whether the genuine shared secret or the implicit-rejection secret was produced, can use this as a plaintext-checking oracle to recover the private key. A proof of concept recovered a full ML-KEM-1024 private key with approximately 98% success using roughly 350 chosen ciphertexts. The flaw is a deterministic logic error and does not rely on timing measurements.

## References
- https://github.com/advisories/GHSA-hcgc-hfp6-58v4
- https://github.com/wolfSSL/wolfssl/pull/10430
- https://nvd.nist.gov/vuln/detail/CVE-2026-10097
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
