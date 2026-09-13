# [H] Perl versions before 5.40.5-RC1, from 5.41.0 before 5.42.3-RC1, from 5.43.0 before 5.43.11 have an integer overflow in S_measure_struct leading to an out-of-bounds heap read in pack and unpack

## Summary
Severity: High
Advisory: CVE-2026-57432
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-57432
Type: osv

## Details
Perl versions before 5.40.5-RC1, from 5.41.0 before 5.42.3-RC1, from 5.43.0 before 5.43.11 have an integer overflow in S_measure_struct leading to an out-of-bounds heap read in pack and unpack.

S_measure_struct adds each item's size times its repeat count to a running total with no overflow check, so a large repeat count in a pack or unpack template wraps the signed SSize_t total negative. The @, X, and x position codes then guard their moves with a signed length comparison that passes when the length is negative, advancing the buffer pointer out of bounds.

A template derived from untrusted input can read heap memory past the buffer and return it to the caller.

## References
- http://www.openwall.com/lists/oss-security/2026/07/13/6
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57432.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57432
- https://github.com/Perl/perl5/commit/40754edc72dd3e513d758153c0e2f0215897740e.patch
- https://github.com/Perl/perl5/commit/5f7eb6bbbe0510964e3fb1d6bb691e5445913e55.patch
- https://github.com/Perl/perl5
