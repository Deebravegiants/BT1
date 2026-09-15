# [C] ALPINE-CVE-2026-75803

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-75803
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-75803
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.8-r0

## Details
Issue summary: ChaCha20-Poly1305 and AES-OCB decryption with an empty
ciphertext can report success without verifying the supplied authentication
tag when the operation is finalized by calling the EVP_Cipher() function.

Impact summary: Applications calling EVP_Cipher() on an empty ciphertext and
expecting the call to check the AEAD tag may accept forged messages.

CWE: CWE-354 (Improper Validation of Integrity Check Value)

Description: The EVP_Cipher() API call for AEAD ciphers behaves like a one
shot encryption and decryption call. It also verifies the AEAD tag after the
decryption operation. However for AES-OCB and ChaCha20-Poly1305 ciphers
it skipped the AEAD tag verification when an empty ciphertext was passed to
the function. The callers of this function might believe that a successful
return indicates a valid AEAD tag for these ciphers, even when that has not
truly been validated in this case.

FIPS impact: no
The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this CVE
as the affected algorithms are not FIPS approved and thus not implemented
in the FIPS module.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-75803
