# [M] Crypt::Argon2 versions from 0.017 before 0.031 for Perl perform a heap out-of-bounds read in argon2_verify on empty encoded input

## Summary
Severity: Medium
Advisory: CVE-2026-8463
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-8463
Type: osv

## Details
Crypt::Argon2 versions from 0.017 before 0.031 for Perl perform a heap out-of-bounds read in argon2_verify on empty encoded input.

The auto-detect form of argon2_verify passes encoded_len - 1 as the length argument to memchr without checking that encoded_len is non-zero. When the encoded string is empty, the size_t subtraction underflows to SIZE_MAX and memchr scans adjacent heap memory looking for a '$' separator byte.

A caller that invokes argon2_verify against a stored hash that may legitimately be empty (for example a placeholder row or a NULL column materialised as an empty string) reads out-of-bounds heap memory, which can crash the process or leak the position of an adjacent '$' byte into subsequent parsing.

## References
- http://www.openwall.com/lists/oss-security/2026/05/13/4
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8463.json
- https://metacpan.org/release/LEONT/Crypt-Argon2-0.031/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-8463
- https://github.com/Leont/crypt-argon2/commit/92eac03ce63d541e0ead7ea5a89b9b67ce0c0e64.patch
- https://github.com/Leont/crypt-argon2
