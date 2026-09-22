# [H] CVE-2015-8963

## Summary
Severity: High
Advisory: CVE-2015-8963
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2015-8963
Type: osv

## Details
Race condition in kernel/events/core.c in the Linux kernel before 4.4 allows local users to gain privileges or cause a denial of service (use-after-free) by leveraging incorrect handling of an swevent data structure during a CPU unplug operation.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=12ca6ad2e3a896256f086497a7c7406a547ee373
- http://source.android.com/security/bulletin/2016-11-01.html
- http://www.securityfocus.com/bid/94207
- https://github.com/torvalds/linux/commit/12ca6ad2e3a896256f086497a7c7406a547ee373
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=12ca6ad2e3a896256f086497a7c7406a547ee373
- https://github.com/torvalds/linux/commit/12ca6ad2e3a896256f086497a7c7406a547ee373
