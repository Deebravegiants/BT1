# [H] ksmbd: add a WRITE_DAC/WRITE_OWNER check to SMB2 SET_INFO SECURITY

## Summary
Severity: High
Advisory: CVE-2026-64394
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64394
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: add a WRITE_DAC/WRITE_OWNER check to SMB2 SET_INFO SECURITY

commit cc57232cae23 ("ksmbd: fix FSCTL permission bypass by adding a
permission check for FSCTL_SET_SPARSE") added a fp->daccess gate to
fsctl_set_sparse and noted that "similar handle-level checks exist in other
functions but are missing here." The SMB2 SET_INFO SECURITY arm is one of
the missing ones, and the most security-relevant: smb2_set_info_sec() calls
set_info_sec() with no per-handle access check.

set_info_sec() (fs/smb/server/smbacl.c) re-permissions the file: it
rewrites owner/group/mode via notify_change(), rewrites the POSIX ACL via
set_posix_acl(), and on KSMBD_SHARE_FLAG_ACL_XATTR shares removes and
rewrites the Windows security descriptor via ksmbd_vfs_set_sd_xattr().
Every other persistent-mutation arm of the sibling handler
smb2_set_info_file() checks fp->daccess first (FILE_WRITE_DATA /
FILE_DELETE / FILE_WRITE_EA / FILE_WRITE_ATTRIBUTES); the SECURITY arm —
which mutates the access control itself — is the only one with no gate.

A client can therefore open a handle with FILE_WRITE_ATTRIBUTES only (no
FILE_WRITE_DAC / FILE_WRITE_OWNER) and use SMB2_SET_INFO with InfoType
SMB2_O_INFO_SECURITY to rewrite the file's DACL and owner, granting itself
access the handle's daccess never carried. Unlike the FSCTL data arms this
is a metadata/xattr operation, so there is no FMODE_WRITE VFS backstop —
the missing fp->daccess check is the entire gate.

Setting a security descriptor is the WRITE_DAC / WRITE_OWNER operation, so
require at least one of those on the handle before re-permissioning the
file. -EACCES is mapped to STATUS_ACCESS_DENIED by smb2_set_info().

## References
- https://git.kernel.org/stable/c/0848b1d8b403f530878195dcbe241a2fddb9d0e1
- https://git.kernel.org/stable/c/44df157a1183a7f746caa970c169255da5ac61f8
- https://git.kernel.org/stable/c/9ab2ffd3ed3d4ca1667c52de27026ddabc11e537
- https://git.kernel.org/stable/c/aae600cdaffc6d9ce97645f129799a103a97d06d
- https://git.kernel.org/stable/c/e6aa731f1b4b3e08caebf66a99f04b22bdab2e99
- https://git.kernel.org/stable/c/f56535db508ead8dec1c481ad93d7d8acd8f8f1e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64394.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64394
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
