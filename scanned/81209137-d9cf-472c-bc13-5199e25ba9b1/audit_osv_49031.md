# [C] CVE-2018-20784

## Summary
Severity: Critical
Advisory: CVE-2018-20784
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-22
Source: https://osv.dev/vulnerability/CVE-2018-20784
Type: osv

## Details
In the Linux kernel before 4.20.2, kernel/sched/fair.c mishandles leaf cfs_rq's, which allows attackers to cause a denial of service (infinite loop in update_blocked_averages) or possibly have unspecified other impact by inducing a high load.

## References
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4211-2/
- https://access.redhat.com/errata/RHSA-2019:1959
- https://access.redhat.com/errata/RHSA-2019:1971
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.2
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4211-1/
- https://github.com/torvalds/linux/commit/c40f7d74c741a907cfaeb73a7697081881c497d0
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c40f7d74c741a907cfaeb73a7697081881c497d0
