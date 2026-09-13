# [M] CVE-2024-23851

## Summary
Severity: Medium
Advisory: CVE-2024-23851
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2024-23851
Type: osv

## Details
copy_params in drivers/md/dm-ioctl.c in the Linux kernel through 6.7.1 can attempt to allocate more than INT_MAX bytes, and crash, because of a missing param_kernel->data_size check. This is related to ctl_ioctl.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZOU3745CWCDZ7EMKMXB2OEEIB5Q3IWM/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EZOU3745CWCDZ7EMKMXB2OEEIB5Q3IWM/
- https://www.spinics.net/lists/dm-devel/msg56574.html
- https://www.spinics.net/lists/dm-devel/msg56694.html
