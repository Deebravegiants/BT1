# [C] ksmbd: add permission checks for FSCTL_DUPLICATE_EXTENTS_TO_FILE

## Summary
Severity: Critical
Advisory: CVE-2026-64399
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64399
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: add permission checks for FSCTL_DUPLICATE_EXTENTS_TO_FILE

The FSCTL_DUPLICATE_EXTENTS_TO_FILE arm of smb2_ioctl() overwrites the
destination file's data via vfs_clone_file_range() with neither the
share-level KSMBD_TREE_CONN_FLAG_WRITABLE check nor a per-handle
fp->daccess check that the other write-bearing arms carry. A client can
overwrite destination data on a read-only share, or from a handle opened
with only FILE_WRITE_ATTRIBUTES (which still yields an FMODE_WRITE filp).
FILE_WRITE_ATTRIBUTES-only destination handle overwrote the file's data via
the clone. Add both checks, matching the FSCTL_SET_SPARSE permission fix;
require FILE_WRITE_DATA since this writes data.

## References
- https://git.kernel.org/stable/c/388e4139db27a9e3612c9d356b826f5b1ff6a9e3
- https://git.kernel.org/stable/c/620d133d469295ee7c017ca6aafac335f65c4a5a
- https://git.kernel.org/stable/c/9b9cf7e65cbeaae1b6636144bacee611cdd7a5d6
- https://git.kernel.org/stable/c/baae7b39673ec21073a25e3d14f8feaada01d5df
- https://git.kernel.org/stable/c/bf460ad5958d506492de4524a656439da3f99c51
- https://git.kernel.org/stable/c/c917e4522d251071dde9871b9142d8ea1186ebfe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64399.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64399
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
