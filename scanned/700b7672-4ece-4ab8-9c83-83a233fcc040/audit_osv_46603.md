# [M] CVE-2014-10402

## Summary
Severity: Medium
Advisory: CVE-2014-10402
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2014-10402
Type: osv

## Details
An issue was discovered in the DBI module through 1.643 for Perl. DBD::File drivers can open files from folders other than those specifically passed via the f_dir attribute in the data source name (DSN). NOTE: this issue exists because of an incomplete fix for CVE-2014-10401.

## References
- https://rt.cpan.org/Public/Bug/Display.html?id=99508#txn-1911590
- https://rt.cpan.org/Public/Bug/Display.html?id=99508#txn-1911590
- https://rt.cpan.org/Public/Bug/Display.html?id=99508#txn-1911590
- https://lists.debian.org/debian-lts-announce/2022/05/msg00046.html
