# [M] ML-KEM-1024 x64 AVX2 incomplete cipher text comparison enables IND-CCA2 break and static private-key recovery

## Summary
Severity: Medium
Advisory: CVE-2026-10097
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-10097
Type: osv

## Details
wolfSSL's AVX2-optimized ML-KEM implementation (mlkem_cmp_avx2) compares only 1536 of the 1568 ciphertext bytes during the Fujisaki-Okamoto re-encryption check in ML-KEM-1024 decapsulation. Ciphertexts that differ from the expected re-encryption solely in bytes 1536-1567 bypass implicit rejection and are accepted as valid, breaking IND-CCA2 security. An attacker able to submit chosen ciphertexts to a decapsulation oracle that uses a static ML-KEM-1024 key, and to observe whether the genuine shared secret or the implicit-rejection secret was produced, can use this as a plaintext-checking oracle to recover the private key. A proof of concept recovered a full ML-KEM-1024 private key with approximately 98% success using roughly 350 chosen ciphertexts. The flaw is a deterministic logic error and does not rely on timing measurements.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10097.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10097
- https://github.com/wolfSSL/wolfssl/pull/10430
- https://github.com/wolfSSL/wolfssl
