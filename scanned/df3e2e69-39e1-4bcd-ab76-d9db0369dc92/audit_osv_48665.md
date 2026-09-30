# [M] CVE-2018-10882

## Summary
Severity: Medium
Advisory: CVE-2018-10882
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2018-10882
Type: osv

## Details
A flaw was found in the Linux kernel's ext4 filesystem. A local user can cause an out-of-bound write in in fs/jbd2/transaction.c code, a denial of service, and a system crash by unmounting a crafted ext4 filesystem image.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3753-2/
- https://usn.ubuntu.com/3871-1/
- https://usn.ubuntu.com/3871-4/
- https://usn.ubuntu.com/3871-5/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://usn.ubuntu.com/3753-1/
- https://usn.ubuntu.com/3871-3/
- http://www.securityfocus.com/bid/106503
- https://bugzilla.kernel.org/show_bug.cgi?id=200069
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10882
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c37e9e013469521d9adb932d17a1795c139b36db
