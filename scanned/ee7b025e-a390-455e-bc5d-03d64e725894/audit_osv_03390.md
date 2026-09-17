# [M] ALPINE-CVE-2025-69418

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-69418
Ecosystem: Alpine:v3.17, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-69418
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=1.1.1 <3.0.19-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1 <3.3.6-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1 <3.3.6-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1 <3.5.5-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1 <3.5.5-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1 <3.5.5-r0

## Details
Issue summary: When using the low-level OCB API directly with AES-NI or<br>other hardware-accelerated code paths, inputs whose length is not a multiple<br>of 16 bytes can leave the final partial block unencrypted and unauthenticated.<br><br>Impact summary: The trailing 1-15 bytes of a message may be exposed in<br>cleartext on encryption and are not covered by the authentication tag,<br>allowing an attacker to read or tamper with those bytes without detection.<br><br>The low-level OCB encrypt and decrypt routines in the hardware-accelerated<br>stream path process full 16-byte blocks but do not advance the input/output<br>pointers. The subsequent tail-handling code then operates on the original<br>base pointers, effectively reprocessing the beginning of the buffer while<br>leaving the actual trailing bytes unprocessed. The authentication checksum<br>also excludes the true tail bytes.<br><br>However, typical OpenSSL consumers using EVP are not affected because the<br>higher-level EVP and provider OCB implementations split inputs so that full<br>blocks and trailing partial blocks are processed in separate calls, avoiding<br>the problematic code path. Additionally, TLS does not use OCB ciphersuites.<br>The vulnerability only affects applications that call the low-level<br>CRYPTO_ocb128_encrypt() or CRYPTO_ocb128_decrypt() functions directly with<br>non-block-aligned lengths in a single call on hardware-accelerated builds.<br>For these reasons the issue was assessed as Low severity.<br><br>The FIPS modules in 3.6, 3.5, 3.4, 3.3, 3.2, 3.1 and 3.0 are not affected<br>by this issue, as OCB mode is not a FIPS-approved algorithm.<br><br>OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0 and 1.1.1 are vulnerable to this issue.<br><br>OpenSSL 1.0.2 is not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-69418
