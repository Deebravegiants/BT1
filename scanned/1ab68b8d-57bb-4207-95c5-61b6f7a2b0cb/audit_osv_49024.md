# [M] CVE-2018-20510

## Summary
Severity: Medium
Advisory: CVE-2018-20510
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-30
Source: https://osv.dev/vulnerability/CVE-2018-20510
Type: osv

## Details
The print_binder_transaction_ilocked function in drivers/android/binder.c in the Linux kernel 4.14.90 allows local users to obtain sensitive address information by reading "*from *code *flags" lines in a debugfs file.

## References
- http://www.securityfocus.com/bid/108125
- https://github.com/Yellow-Pay/CVE/blob/master/CVE-2018-20510
