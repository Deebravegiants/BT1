# [M] CVE-2018-11508

## Summary
Severity: Medium
Advisory: CVE-2018-11508
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-05-28
Source: https://osv.dev/vulnerability/CVE-2018-11508
Type: osv

## Details
The compat_get_timex function in kernel/compat.c in the Linux kernel before 4.16.9 allows local users to obtain sensitive information from kernel memory via adjtimex.

## References
- https://usn.ubuntu.com/3695-2/
- https://usn.ubuntu.com/3697-1/
- https://usn.ubuntu.com/3697-2/
- http://www.securityfocus.com/bid/104292
- https://usn.ubuntu.com/3695-1/
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.9
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1574
- https://github.com/torvalds/linux/commit/0a0b98734479aa5b3c671d5190e86273372cab95
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0a0b98734479aa5b3c671d5190e86273372cab95
- https://www.exploit-db.com/exploits/46208/
