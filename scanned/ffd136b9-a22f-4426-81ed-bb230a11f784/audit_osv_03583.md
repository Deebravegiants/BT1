# [H] ALPINE-CVE-2026-32877

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-32877
Ecosystem: Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-32877
Type: osv

## Affected
- Alpine:v3.24: `botan3` — affected >=0 <3.11.0-r0

## Details
Botan is a C++ cryptography library. From version 2.3.0 to before version 3.11.0, during SM2 decryption, the code that checked the authentication code value (C3) failed to check that the encoded value was of the expected length prior to comparison. An invalid ciphertext can cause a heap over-read of up to 31 bytes, resulting in a crash or potentially other undefined behavior. This issue has been patched in version 3.11.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-32877
