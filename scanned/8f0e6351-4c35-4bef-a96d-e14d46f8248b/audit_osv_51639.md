# [M] CVE-2021-3732

## Summary
Severity: Medium
Advisory: CVE-2021-3732
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-3732
Type: osv

## Details
A flaw was found in the Linux kernel's OverlayFS subsystem in the way the user mounts the TmpFS filesystem with OverlayFS. This flaw allows a local user to gain access to hidden files that should not be accessible.

## References
- https://ubuntu.com/security/CVE-2021-3732
- https://bugzilla.redhat.com/show_bug.cgi?id=1995249
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=427215d85e8d1476da1a86b8d67aceb485eb3631
- https://github.com/torvalds/linux/commit/427215d85e8d1476da1a86b8d67aceb485eb3631
