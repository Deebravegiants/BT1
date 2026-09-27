# [H] In wolfSSL's EVP layer, the ChaCha20-Poly1305 AEAD decryption path in `wolfSSL_EVP_CipherFinal` (and...

## Summary
Severity: High
Advisory: JLSEC-2026-728
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-728
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
In wolfSSL's EVP layer, the ChaCha20-Poly1305 AEAD decryption path in `wolfSSL_EVP_CipherFinal` (and related EVP cipher finalization functions) fails to verify the authentication tag before returning plaintext to the caller. When an application uses the EVP API to perform ChaCha20-Poly1305 decryption, the implementation computes or accepts the tag but does not compare it against the expected value.

## References
- https://github.com/advisories/GHSA-3xr8-r75g-g9c6
- https://github.com/wolfSSL/wolfssl/pull/10102
- https://nvd.nist.gov/vuln/detail/CVE-2026-5479
