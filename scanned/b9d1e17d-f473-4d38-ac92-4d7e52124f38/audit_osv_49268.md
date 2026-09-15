# [M] CVE-2018-7995

## Summary
Severity: Medium
Advisory: CVE-2018-7995
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2018-7995
Type: osv

## Details
Race condition in the store_int_with_restart() function in arch/x86/kernel/cpu/mcheck/mce.c in the Linux kernel through 4.15.7 allows local users to cause a denial of service (panic) by leveraging root access to write to the check_interval file in a /sys/devices/system/machinecheck/machinecheck<cpu number> directory. NOTE: a third party has indicated that this report is not security relevant

## References
- https://usn.ubuntu.com/3654-2/
- http://www.securityfocus.com/bid/103356
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3656-1/
- https://www.debian.org/security/2018/dsa-4187
- https://www.debian.org/security/2018/dsa-4188
- https://usn.ubuntu.com/3654-1/
- https://bugzilla.suse.com/show_bug.cgi?id=1084755
- https://lkml.org/lkml/2018/3/2/970
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=b3b7c4795ccab5be71f080774c45bbbcc75c2aaf
