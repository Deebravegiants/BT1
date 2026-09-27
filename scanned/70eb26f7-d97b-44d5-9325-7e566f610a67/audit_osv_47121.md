# [H] CVE-2015-8966

## Summary
Severity: High
Advisory: CVE-2015-8966
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/CVE-2015-8966
Type: osv

## Details
arch/arm/kernel/sys_oabi-compat.c in the Linux kernel before 4.4 allows local users to gain privileges via a crafted (1) F_OFD_GETLK, (2) F_OFD_SETLK, or (3) F_OFD_SETLKW command in an fcntl64 system call.

## References
- http://source.android.com/security/bulletin/2016-12-01.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=76cc404bfdc0d419c720de4daaf2584542734f42
- https://github.com/torvalds/linux/commit/76cc404bfdc0d419c720de4daaf2584542734f42
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=76cc404bfdc0d419c720de4daaf2584542734f42
- https://github.com/torvalds/linux/commit/76cc404bfdc0d419c720de4daaf2584542734f42
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=76cc404bfdc0d419c720de4daaf2584542734f42
- https://github.com/torvalds/linux/commit/76cc404bfdc0d419c720de4daaf2584542734f42
- http://www.securityfocus.com/bid/94673
