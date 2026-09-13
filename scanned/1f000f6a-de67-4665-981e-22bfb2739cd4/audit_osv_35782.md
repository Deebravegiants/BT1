# [C] Imager versions before 1.033 for Perl treat unsigned EXIF IFD entry counts as signed

## Summary
Severity: Critical
Advisory: CVE-2026-14454
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-14454
Type: osv

## Details
Imager versions before 1.033 for Perl treat unsigned EXIF IFD entry counts as signed.

Imager mishandled large EXIF IFD entry count values, treating them as negative numbers.  This could lead to an attempt to allocate a block nearly the size of the address space, which fails and kills the process.

An attacker could craft an image with EXIF data that terminates a worker process.

## References
- http://www.openwall.com/lists/oss-security/2026/07/08/6
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14454.json
- https://metacpan.org/release/TONYC/Imager-1.033/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-14454
- https://github.com/tonycoz/imager/commit/06f01a5d0fd591259aeba589370d6888384a6b6d.patch
- https://github.com/tonycoz/imager
