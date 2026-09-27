# [H] CVE-2019-11599

## Summary
Severity: High
Advisory: CVE-2019-11599
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-29
Source: https://osv.dev/vulnerability/CVE-2019-11599
Type: osv

## Details
The coredump implementation in the Linux kernel before 5.0.10 does not use locking or other mechanisms to prevent vma layout or vma flags changes while it runs, which allows local users to obtain sensitive information, cause a denial of service, or possibly have unspecified other impact by triggering a race condition with mmget_not_zero or get_task_mm calls. This is related to fs/userfaultfd.c, mm/mmap.c, fs/proc/task_mmu.c, and drivers/infiniband/core/uverbs_main.c.

## References
- https://lists.debian.org/debian-lts-announce/2019/06/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00025.html
- http://packetstormsecurity.com/files/153702/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://access.redhat.com/errata/RHSA-2020:0103
- https://access.redhat.com/errata/RHSA-2020:0179
- https://seclists.org/bugtraq/2019/Jun/26
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://access.redhat.com/errata/RHSA-2020:0543
- https://usn.ubuntu.com/4118-1/
- https://lists.debian.org/debian-lts-announce/2019/05/msg00042.html
- https://usn.ubuntu.com/4069-2/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://www.securityfocus.com/bid/108113
- https://access.redhat.com/errata/RHSA-2019:2029
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.37
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.10
- https://support.f5.com/csp/article/K51674118?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4095-1/
- http://www.openwall.com/lists/oss-security/2019/04/30/1
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.114
