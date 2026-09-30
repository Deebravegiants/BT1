# [H] CVE-2018-7480

## Summary
Severity: High
Advisory: CVE-2018-7480
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-25
Source: https://osv.dev/vulnerability/CVE-2018-7480
Type: osv

## Details
The blkcg_init_queue function in block/blk-cgroup.c in the Linux kernel before 4.11 allows local users to cause a denial of service (double free) or possibly have unspecified other impact by triggering a creation failure.

## References
- https://www.debian.org/security/2018/dsa-4188
- https://usn.ubuntu.com/3654-1/
- https://usn.ubuntu.com/3654-2/
- https://usn.ubuntu.com/3656-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9b54d816e00425c3a517514e0d677bb3cec49258
- https://github.com/torvalds/linux/commit/9b54d816e00425c3a517514e0d677bb3cec49258
