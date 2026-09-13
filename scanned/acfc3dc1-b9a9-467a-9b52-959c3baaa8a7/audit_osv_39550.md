# [H] isofs: validate block number from NFS file handle in isofs_export_iget

## Summary
Severity: High
Advisory: CVE-2026-46124
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46124
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.15.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

isofs: validate block number from NFS file handle in isofs_export_iget

isofs_fh_to_dentry() and isofs_fh_to_parent() pass an attacker-
controlled block number (ifid->block or ifid->parent_block) from
the NFS file handle to isofs_export_iget(), which only rejects
block == 0 before calling isofs_iget() and ultimately sb_bread().
A crafted file handle with fh_len sufficient to pass the check
added by commit 0405d4b63d08 ("isofs: Prevent the use of too small
fid") can still drive the server to read any in-range block on the
backing device as if it were an iso_directory_record.  That earlier
fix was assigned CVE-2025-37780.

sb_bread() on an out-of-range block returns NULL cleanly via the
EIO path, so there is no memory-safety violation.  For in-range
reads of adjacent-partition data on the same block device, the
unrelated bytes end up in iso_inode_info fields that reach the NFS
client as dentry metadata.  The deployment surface (isofs exported
over NFS from loop-mounted images) is narrow and requires an
authenticated NFS peer, but the malformed-file-handle class is
reportable as hardening next to the existing CVE-2025-37780 fix.

Reject block >= ISOFS_SB(sb)->s_nzones in isofs_export_iget() so
the check covers both isofs_fh_to_dentry() and isofs_fh_to_parent()
call sites with a single line.

## References
- https://git.kernel.org/stable/c/0a1af74ae2177bda3aee0837a0546309aa539d0d
- https://git.kernel.org/stable/c/24376458138387fb251e782e624c7776e9826796
- https://git.kernel.org/stable/c/31dbb4ba0f719ae7774e4c0c95172c9bf81692f5
- https://git.kernel.org/stable/c/4c721a1d9b3c4fcaf59cc9b2281e3ec5a043e1a6
- https://git.kernel.org/stable/c/908a76f0b1038035e6ebb4f2293ce079f92e0a02
- https://git.kernel.org/stable/c/afbafeddf23db13fe2edb2d5c0bf4bbb13d7881b
- https://git.kernel.org/stable/c/bb0988ed4f2e26d59bbb58f644cb3a55b7521e21
- https://git.kernel.org/stable/c/ee0024f5a7e3c73aa253869fae9650ae054093ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46124.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46124
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
