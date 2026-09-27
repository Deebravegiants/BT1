# [H] CVE-2019-6974

## Summary
Severity: High
Advisory: CVE-2019-6974
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-15
Source: https://osv.dev/vulnerability/CVE-2019-6974
Type: osv

## Details
In the Linux kernel before 4.20.8, kvm_ioctl_create_device in virt/kvm/kvm_main.c mishandles reference counting because of a race condition, leading to a use-after-free.

## References
- https://support.f5.com/csp/article/K11186236?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/3930-2/
- https://usn.ubuntu.com/3931-1/
- https://access.redhat.com/errata/RHBA-2019:0959
- https://access.redhat.com/errata/RHSA-2019:3967
- https://access.redhat.com/errata/RHSA-2020:0103
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.99
- https://usn.ubuntu.com/3931-2/
- https://usn.ubuntu.com/3932-1/
- https://usn.ubuntu.com/3933-2/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00002.html
- https://support.f5.com/csp/article/K11186236
- https://access.redhat.com/errata/RHSA-2019:0818
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.156
- https://usn.ubuntu.com/3930-1/
- https://usn.ubuntu.com/3932-2/
- https://usn.ubuntu.com/3933-1/
- http://www.securityfocus.com/bid/107127
