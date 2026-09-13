# [H] CVE-2023-4389

## Summary
Severity: High
Advisory: CVE-2023-4389
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-08-16
Source: https://osv.dev/vulnerability/CVE-2023-4389
Type: osv

## Details
A flaw was found in btrfs_get_root_ref in fs/btrfs/disk-io.c in the btrfs filesystem in the Linux Kernel due to a double decrement of the reference count. This issue may allow a local attacker with user privilege to crash the system or may lead to leaked internal kernel information.

## References
- https://access.redhat.com/security/cve/CVE-2023-4389
- https://bugzilla.redhat.com/show_bug.cgi?id=2219271
- https://patchwork.kernel.org/project/linux-btrfs/patch/20220324134454.15192-1-baijiaju1990@gmail.com/
