# [M] VeraCryp: wolfCrypt backend bypasses VeraCrypt PBKDF2 iteration count (non-default WOLFCRYPT=1 builds)

## Summary
Severity: Medium
Advisory: CVE-2026-53762
Aliases: GHSA-94c6-mgmv-mqc5
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-53762
Type: osv

## Details
VeraCrypt provides disk encryption with strong security based on TrueCrypt. Prior to 1.26.29, non-default builds created with WOLFCRYPT=1 and WOLFCRYPT_BACKEND route SHA-256 and SHA-512 volume-header key derivation through derive_key_sha256 and derive_key_sha512 in src/Crypto/wolfCrypt.c, where the configured iterations value is discarded and wc_HKDF is used instead of PBKDF2-HMAC. Changing the PIM or iteration count therefore does not increase derivation cost, allowing an attacker with an affected container, disk image, or volume header to perform substantially cheaper offline password guesses. Official precompiled VeraCrypt binaries and normal distribution packages use the standard PBKDF2 backend and are not affected. Volumes created by an affected WOLFCRYPT=1 build require backup and recreation because corrected builds derive different keys. This issue is fixed in version 1.26.29.

## References
- https://github.com/veracrypt/VeraCrypt/releases/tag/VeraCrypt_1.26.29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53762.json
- https://github.com/veracrypt/VeraCrypt/security/advisories/GHSA-94c6-mgmv-mqc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53762
- https://github.com/veracrypt/VeraCrypt/commit/39f93910075e1cf492fcf4a9f99a53c7d0b96b87
