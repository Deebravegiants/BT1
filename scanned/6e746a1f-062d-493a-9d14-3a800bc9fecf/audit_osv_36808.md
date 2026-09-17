# [C] Crypt::NaCl::Sodium versions through 2.001 for Perl has an integer overflow flaw on 32-bit systems

## Summary
Severity: Critical
Advisory: CVE-2026-2588
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-02-22
Source: https://osv.dev/vulnerability/CVE-2026-2588
Type: osv

## Details
Crypt::NaCl::Sodium versions through 2.001 for Perl has an integer overflow flaw on 32-bit systems.

Sodium.xs casts a STRLEN (size_t) to unsigned long long when passing a length pointer to libsodium functions.  On 32-bit systems size_t is typically 32-bits while an unsigned long long is at least 64-bits.

## References
- https://cpan.org/modules
- https://metacpan.org/release/TIMLEGGE/Crypt-NaCl-Sodium-2.001/source/Sodium.xs#L2119
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2588.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2588
- https://github.com/cpan-authors/crypt-nacl-sodium/commit/557388bdb4da416a56663cda0154b80cd524395c.patch
- https://github.com/cpan-authors/crypt-nacl-sodium/commit/8cf7f66ba922443e131c9deae1ee00fafe4f62e4.patch
- https://github.com/cpan-authors/crypt-nacl-sodium
