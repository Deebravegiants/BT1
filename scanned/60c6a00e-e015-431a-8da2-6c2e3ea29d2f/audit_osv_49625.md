# [H] CVE-2019-14835

## Summary
Severity: High
Advisory: CVE-2019-14835
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-17
Source: https://osv.dev/vulnerability/CVE-2019-14835
Type: osv

## Details
A buffer overflow flaw was found, in versions from 2.6.34 to 5.2.x, in the way Linux kernel's vhost functionality that translates virtqueue buffers to IOVs, logged the buffer descriptors during migration. A privileged guest user able to pass descriptors with invalid length to the host when migration is underway, could use this flaw to increase their privileges on the host.

## References
- https://access.redhat.com/errata/RHSA-2019:2827
- https://access.redhat.com/errata/RHSA-2019:2854
- https://access.redhat.com/errata/RHSA-2019:2862
- https://access.redhat.com/errata/RHSA-2019:2864
- https://security.netapp.com/advisory/ntap-20191031-0005/
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- http://www.huawei.com/en/psirt/security-advisories/huawei-sa-20200115-01-qemu-en
- https://access.redhat.com/errata/RHSA-2019:2828
- https://access.redhat.com/errata/RHSA-2019:2863
- https://access.redhat.com/errata/RHSA-2019:2924
- https://usn.ubuntu.com/4135-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://access.redhat.com/errata/RHSA-2019:2899
- http://www.openwall.com/lists/oss-security/2019/10/09/7
- https://access.redhat.com/errata/RHSA-2019:2830
- https://access.redhat.com/errata/RHSA-2019:2867
- https://access.redhat.com/errata/RHSA-2019:2889
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- https://access.redhat.com/errata/RHSA-2019:2900
- https://lists.debian.org/debian-lts-announce/2019/10/msg00000.html
