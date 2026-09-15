# [C] GD versions before 2.86 for Perl allow OS command injection and file overwrite via a 2-arg open() of filename arguments in _make_filehandle

## Summary
Severity: Critical
Advisory: CVE-2026-11526
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-14
Source: https://osv.dev/vulnerability/CVE-2026-11526
Type: osv

## Details
GD versions before 2.86 for Perl allow OS command injection and file overwrite via a 2-arg open() of filename arguments in _make_filehandle.

GD::Image::_make_filehandle opens a filename argument with Perl's 2-arg open(), so a filename that begins or ends with a pipe ("| cmd", "cmd |") or begins with a redirect ("> path", ">> path") is run as a command or redirect rather than opened as a file. _make_filehandle is the single open path behind every filename-accepting constructor (new, newFromPng, newFromJpeg, and the rest); the in-memory *Data variants do not open a path and are unaffected.

Any caller that forwards untrusted input to one of these constructors as a pathname can run an arbitrary command or truncate a file under the process UID.

## References
- http://www.openwall.com/lists/oss-security/2026/06/14/4
- https://cpan.org/modules
- https://lists.debian.org/debian-lts-announce/2026/06/msg00027.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11526.json
- https://metacpan.org/release/RURBAN/GD-2.86/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-11526
- https://github.com/lstein/Perl-GD/commit/67b163713c6c78dfeb693da0978ae934e5cd8210.patch
- https://github.com/lstein/Perl-GD
