# [H] ksmbd: add a permission check for FSCTL_SET_ZERO_DATA

## Summary
Severity: High
Advisory: CVE-2026-64398
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64398
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: add a permission check for FSCTL_SET_ZERO_DATA

FSCTL_SET_ZERO_DATA in smb2_ioctl() destroys file data via
ksmbd_vfs_zero_data() -> vfs_fallocate(PUNCH_HOLE/ZERO_RANGE) after
checking only the share-level KSMBD_TREE_CONN_FLAG_WRITABLE, with no
per-handle access check. A handle opened with only FILE_WRITE_ATTRIBUTES
still yields an FMODE_WRITE filp (FILE_WRITE_ATTRIBUTES is part of
FILE_WRITE_DESIRE_ACCESS_LE, so smb2_create_open_flags() opens it
O_WRONLY), so the vfs_fallocate FMODE_WRITE check does not stop it; only
the missing fp->daccess gate would. Reproduced on mainline 7.1-rc7 with
KASAN by an authenticated SMB client: a FILE_WRITE_ATTRIBUTES-only handle
zeroed 4096 bytes of file data it had no FILE_WRITE_DATA right to
(6/6; a FILE_READ_DATA-only handle was correctly denied).

This is the unfixed sibling of commit cc57232cae23 ("ksmbd: fix FSCTL
permission bypass by adding a permission check for FSCTL_SET_SPARSE").
Because SET_ZERO_DATA writes data (not an attribute), require
FILE_WRITE_DATA.

## References
- https://git.kernel.org/stable/c/25377f369688dd0bd814dc8965ed26d44238ecaa
- https://git.kernel.org/stable/c/3072d82461f498c85daea8766e9d8bfbada31605
- https://git.kernel.org/stable/c/3320ba068198adc144c89d6661b805acce01735b
- https://git.kernel.org/stable/c/57f2042fd87d7ce8fc3ac8b6c176e554df68b1a7
- https://git.kernel.org/stable/c/ca53bb17f4e8232cfaece3953d3cef62c559b039
- https://git.kernel.org/stable/c/deffa929086d7902e30918adf3dd27ccfe9c08b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64398.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64398
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
