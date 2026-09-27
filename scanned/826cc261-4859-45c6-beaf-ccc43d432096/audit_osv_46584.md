# [M] CVE-2013-7491

## Summary
Severity: Medium
Advisory: CVE-2013-7491
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/CVE-2013-7491
Type: osv

## Details
An issue was discovered in the DBI module before 1.628 for Perl. Stack corruption occurs when a user-defined function requires a non-trivial amount of memory and the Perl stack gets reallocated.

## References
- https://github.com/perl5-dbi/dbi/commit/401f1221311c71f760e21c98772f0f7e3cbead1d
- https://metacpan.org/pod/distribution/DBI/Changes#Changes-in-DBI-1.628-22nd-July-2013
- https://rt.cpan.org/Public/Bug/Display.html?id=85562
- https://github.com/perl5-dbi/dbi/commit/401f1221311c71f760e21c98772f0f7e3cbead1d
