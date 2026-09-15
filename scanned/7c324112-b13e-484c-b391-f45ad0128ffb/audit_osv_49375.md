# [H] CVE-2019-11487

## Summary
Severity: High
Advisory: CVE-2019-11487
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2019-11487
Type: osv

## Details
The Linux kernel before 5.1-rc5 allows page->_refcount reference count overflow, with resultant use-after-free issues, if about 140 GiB of RAM exists. This is related to fs/fuse/dev.c, fs/pipe.c, fs/splice.c, include/linux/mm.h, include/linux/pipe_fs_i.h, kernel/trace/trace.c, mm/gup.c, and mm/hugetlb.c. It can occur with FUSE requests.

## References
- https://security.netapp.com/advisory/ntap-20190517-0005/
- https://support.f5.com/csp/article/K14255532
- http://www.securityfocus.com/bid/108054
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00040.html
- https://access.redhat.com/errata/RHSA-2019:2741
- https://usn.ubuntu.com/4069-2/
- https://access.redhat.com/errata/RHSA-2019:2703
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://usn.ubuntu.com/4069-1/
- https://usn.ubuntu.com/4115-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00048.html
- http://www.openwall.com/lists/oss-security/2019/04/29/1
- https://access.redhat.com/errata/RHSA-2020:0174
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00039.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4145-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f958d7b528b1b40c44cfda5eabe2d82760d868c3
- https://github.com/torvalds/linux/commit/8fde12ca79aff9b5ba951fce1a2641901b8d8e64
