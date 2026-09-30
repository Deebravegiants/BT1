# [M] CVE-2013-7490

## Summary
Severity: Medium
Advisory: CVE-2013-7490
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/CVE-2013-7490
Type: osv

## Details
An issue was discovered in the DBI module before 1.632 for Perl. Using many arguments to methods for Callbacks may lead to memory corruption.

## References
- https://github.com/perl5-dbi/dbi/commit/a8b98e988d6ea2946f5f56691d6d5ead53f65766
- https://metacpan.org/pod/distribution/DBI/Changes#Changes-in-DBI-1.632-9th-Nov-2014
- https://rt.cpan.org/Public/Bug/Display.html?id=86744#txn-1880941
- https://usn.ubuntu.com/4509-1/
- https://github.com/perl5-dbi/dbi/commit/a8b98e988d6ea2946f5f56691d6d5ead53f65766
