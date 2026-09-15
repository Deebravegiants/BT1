# [C] CVE-2017-20230

## Summary
Severity: Critical
Advisory: CVE-2017-20230
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2017-20230
Type: osv

## Details
Storable versions before 3.05 for Perl has a stack overflow.

The retrieve_hook function stored the length of the class name into a signed integer but in read operations treated the length as unsigned. This allowed an attacker to craft data that could trigger the overflow.

## References
- https://metacpan.org/release/RURBAN/Storable-3.05/changes
- https://www.nntp.perl.org/group/perl.perl5.porters/2017/01/msg242533.html
- https://www.nntp.perl.org/group/perl.perl5.porters/2017/01/msg242703.html
- https://github.com/Perl/perl5/issues/15831
- https://github.com/Perl/perl5/commit/a258c17c6937f79529c8319a829310e09cdbd216.patch
- http://www.openwall.com/lists/oss-security/2026/04/21/5
