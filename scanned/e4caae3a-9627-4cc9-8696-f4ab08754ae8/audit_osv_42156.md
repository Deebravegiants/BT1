# [C] FreeRDP before 3.28.0 Heap Buffer Overflow via crypto_rsa_common

## Summary
Severity: Critical
Advisory: CVE-2026-64620
Aliases: GHSA-pjqx-v446-x7fc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64620
Type: osv

## Details
FreeRDP before 3.28.0 (affected <=3.27.1) contains a heap-based buffer overflow in crypto_rsa_common() (libfreerdp/crypto/crypto.c). The function writes the modular-exponentiation result into the caller's output buffer via BN_bn2bin() and only afterward checks output_length > out_length, so out-of-bounds bytes are written before the bounds check. On the server side, when a client selects RDP Standard Security, the encrypted client random is decrypted into a fixed 32-byte buffer. Because the server publishes its RSA public key, an unauthenticated attacker can forge a ciphertext whose decrypted value is up to the full modulus length (e.g. 256 bytes for RSA-2048), overflowing the 32-byte heap buffer by up to ~224 attacker-controlled bytes pre-authentication, resulting in denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64620.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-pjqx-v446-x7fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-64620
- https://www.vulncheck.com/advisories/freerdp-before-heap-buffer-overflow-via-crypto-rsa-common
- https://github.com/FreeRDP/FreeRDP/commit/1f7a716d39b5605bb8a83b0c3c97a6ce386609ef
