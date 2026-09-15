# [M] CVE-2025-49601

## Summary
Severity: Medium
Advisory: CVE-2025-49601
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-49601
Type: osv

## Details
In MbedTLS 3.3.0 before 3.6.4, mbedtls_lms_import_public_key does not check that the input buffer is at least 4 bytes before reading a 32-bit field, allowing a possible out-of-bounds read on truncated input. Specifically, an out-of-bounds read in mbedtls_lms_import_public_key allows context-dependent attackers to trigger a crash or limited adjacent-memory disclosure by supplying a truncated LMS (Leighton-Micali Signature) public-key buffer under four bytes. An LMS public key starts with a 4-byte type indicator. The function mbedtls_lms_import_public_key reads this type indicator before validating the size of its input.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49601.json
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2025-06-4.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-49601
