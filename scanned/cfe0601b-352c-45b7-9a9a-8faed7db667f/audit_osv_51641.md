# [H] CVE-2021-3739

## Summary
Severity: High
Advisory: CVE-2021-3739
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-3739
Type: osv

## Details
A NULL pointer dereference flaw was found in the btrfs_rm_device function in fs/btrfs/volumes.c in the Linux Kernel, where triggering the bug requires ‘CAP_SYS_ADMIN’. This flaw allows a local attacker to crash the system or leak kernel internal information. The highest threat from this vulnerability is to system availability.

## References
- https://security.netapp.com/advisory/ntap-20220407-0006/
- https://ubuntu.com/security/CVE-2021-3739
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e4571b8c5e9ffa1e85c0c671995bd4dcc5c75091
- https://github.com/torvalds/linux/commit/e4571b8c5e9ffa1e85c0c671995bd4dcc5c75091
- https://www.openwall.com/lists/oss-security/2021/08/25/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1997958
