# [M] CVE-2018-20509

## Summary
Severity: Medium
Advisory: CVE-2018-20509
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-30
Source: https://osv.dev/vulnerability/CVE-2018-20509
Type: osv

## Details
The print_binder_ref_olocked function in drivers/android/binder.c in the Linux kernel 4.14.90 allows local users to obtain sensitive address information by reading " ref *desc *node" lines in a debugfs file.

## References
- https://www.mail-archive.com/debian-security-tracker%40lists.debian.org/msg03902.html
- https://github.com/Yellow-Pay/CVE/blob/master/CVE-2018-20509.md
- https://security.netapp.com/advisory/ntap-20190517-0002/
