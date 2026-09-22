# [H] CVE-2020-13974

## Summary
Severity: High
Advisory: CVE-2020-13974
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-09
Source: https://osv.dev/vulnerability/CVE-2020-13974
Type: osv

## Details
An issue was discovered in the Linux kernel 4.4 through 5.7.1. drivers/tty/vt/keyboard.c has an integer overflow if k_ascii is called several times in a row, aka CID-b86dab054059. NOTE: Members in the community argue that the integer overflow does not lead to a security issue in this case.

## References
- https://usn.ubuntu.com/4439-1/
- https://usn.ubuntu.com/4440-1/
- https://usn.ubuntu.com/4485-1/
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00008.html
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=dad0bf9ce93fa40b667eccd3306783f4db4b932b
- https://lists.debian.org/debian-lts-announce/2020/08/msg00019.html
- https://usn.ubuntu.com/4427-1/
- https://usn.ubuntu.com/4483-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b86dab054059b970111b5516ae548efaae5b3aae
- https://lkml.org/lkml/2020/3/22/482
