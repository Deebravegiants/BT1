# [M] CVE-2020-25639

## Summary
Severity: Medium
Advisory: CVE-2020-25639
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-04
Source: https://osv.dev/vulnerability/CVE-2020-25639
Type: osv

## Details
A NULL pointer dereference flaw was found in the Linux kernel's GPU Nouveau driver functionality in versions prior to 5.12-rc1 in the way the user calls ioctl DRM_IOCTL_NOUVEAU_CHANNEL_ALLOC. This flaw allows a local user to crash the system.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HE4CT3NL6OEBRRBUKHIX63GLNVOWCVRW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SUCBCKRHWP3UD2AVVYQJE7BIJEMCMXW5/
- https://bugzilla.redhat.com/show_bug.cgi?id=1876995
