# [H] Botan: Heap Buffer Over-read in SM2 Decryption via Undersized C3 Hash Field

## Summary
Severity: High
Advisory: CVE-2026-32877
Aliases: GHSA-7jj6-4r42-w9h6
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-32877
Type: osv

## Details
Botan is a C++ cryptography library. From version 2.3.0 to before version 3.11.0, during SM2 decryption, the code that checked the authentication code value (C3) failed to check that the encoded value was of the expected length prior to comparison. An invalid ciphertext can cause a heap over-read of up to 31 bytes, resulting in a crash or potentially other undefined behavior. This issue has been patched in version 3.11.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32877.json
- https://github.com/randombit/botan/security/advisories/GHSA-7jj6-4r42-w9h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-32877
