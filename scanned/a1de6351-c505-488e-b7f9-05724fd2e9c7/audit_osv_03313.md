# [M] ALPINE-CVE-2025-49601

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-49601
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-49601
Type: osv

## Affected
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.4-r0

## Details
In MbedTLS 3.3.0 before 3.6.4, mbedtls_lms_import_public_key does not check that the input buffer is at least 4 bytes before reading a 32-bit field, allowing a possible out-of-bounds read on truncated input. Specifically, an out-of-bounds read in mbedtls_lms_import_public_key allows context-dependent attackers to trigger a crash or limited adjacent-memory disclosure by supplying a truncated LMS (Leighton-Micali Signature) public-key buffer under four bytes. An LMS public key starts with a 4-byte type indicator. The function mbedtls_lms_import_public_key reads this type indicator before validating the size of its input.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-49601
