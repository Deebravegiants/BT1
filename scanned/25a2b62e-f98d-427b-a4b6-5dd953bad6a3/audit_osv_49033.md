# [H] CVE-2018-20856

## Summary
Severity: High
Advisory: CVE-2018-20856
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-26
Source: https://osv.dev/vulnerability/CVE-2018-20856
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.18.7. In block/blk-core.c, there is an __blk_drain_queue() use-after-free because a certain error case is mishandled.

## References
- http://packetstormsecurity.com/files/154408/Kernel-Live-Patch-Security-Notice-LSN-0055-1.html
- https://seclists.org/bugtraq/2019/Aug/18
- https://usn.ubuntu.com/4116-1/
- https://usn.ubuntu.com/4118-1/
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://seclists.org/bugtraq/2019/Aug/26
- https://support.f5.com/csp/article/K14673240?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4094-1/
- http://packetstormsecurity.com/files/154059/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://access.redhat.com/errata/RHSA-2019:3076
- https://access.redhat.com/errata/RHSA-2019:3089
- https://access.redhat.com/errata/RHSA-2020:0100
- https://access.redhat.com/errata/RHSA-2020:0103
- https://access.redhat.com/errata/RHSA-2020:0664
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.7
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://access.redhat.com/errata/RHSA-2019:3055
- https://access.redhat.com/errata/RHSA-2019:3217
- https://access.redhat.com/errata/RHSA-2020:0543
