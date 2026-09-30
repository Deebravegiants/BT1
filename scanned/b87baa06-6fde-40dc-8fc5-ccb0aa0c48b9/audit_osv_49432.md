# [H] CVE-2019-11810

## Summary
Severity: High
Advisory: CVE-2019-11810
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-07
Source: https://osv.dev/vulnerability/CVE-2019-11810
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.7. A NULL pointer dereference can occur when megasas_create_frame_pool() fails in megasas_alloc_cmds() in drivers/scsi/megaraid/megaraid_sas_base.c. This causes a Denial of Service, related to a use-after-free.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00056.html
- https://access.redhat.com/errata/RHSA-2019:2736
- https://access.redhat.com/errata/RHSA-2020:0036
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.7
- https://lists.debian.org/debian-lts-announce/2019/06/msg00010.html
- https://security.netapp.com/advisory/ntap-20190719-0003/
- https://access.redhat.com/errata/RHSA-2019:1959
- https://access.redhat.com/errata/RHSA-2019:2837
- https://usn.ubuntu.com/4005-1/
- https://usn.ubuntu.com/4008-1/
- https://usn.ubuntu.com/4008-3/
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4118-1/
- http://www.securityfocus.com/bid/108286
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://access.redhat.com/errata/RHSA-2019:1971
- https://access.redhat.com/errata/RHSA-2019:3217
- https://support.f5.com/csp/article/K50484570
