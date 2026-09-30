# [M] CVE-2018-1108

## Summary
Severity: Medium
Advisory: CVE-2018-1108
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-05-21
Source: https://osv.dev/vulnerability/CVE-2018-1108
Type: osv

## Details
kernel drivers before version 4.17-rc1 are vulnerable to a weakness in the Linux kernel's implementation of random seed data. Programs, early in the boot sequence, could use the data allocated for the seed before it was sufficiently generated.

## References
- https://usn.ubuntu.com/3718-2/
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-3/
- http://www.securityfocus.com/bid/104055
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://usn.ubuntu.com/3718-1/
- https://usn.ubuntu.com/3752-2/
- https://www.debian.org/security/2018/dsa-4188
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1108
