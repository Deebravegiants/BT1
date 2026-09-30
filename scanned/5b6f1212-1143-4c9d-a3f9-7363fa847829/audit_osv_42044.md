# [H] ksmbd: require source read access for duplicate extents

## Summary
Severity: High
Advisory: CVE-2026-64395
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64395
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: require source read access for duplicate extents

FSCTL_DUPLICATE_EXTENTS_TO_FILE passes the source file directly to
vfs_clone_file_range() or vfs_copy_file_range() without checking the SMB
access mask granted to the source handle. A handle opened with attribute
access can consequently be used to copy file contents into an
attacker-readable destination.

Require FILE_READ_DATA on the source handle before either VFS operation,
matching other ksmbd data-copy paths.

## References
- https://git.kernel.org/stable/c/2d2ab6983620c2d60ce7db72133984ca3873b929
- https://git.kernel.org/stable/c/67bdad9cf01b25030e3bf00bbce6c309319d6663
- https://git.kernel.org/stable/c/a10942af27832c2761d020863a46e79bebe0567d
- https://git.kernel.org/stable/c/b0d4d5cb846a1ddb7aaab9adfb5986e4540e6e5f
- https://git.kernel.org/stable/c/cedff600f1642aa982178503552f0d007bc829c8
- https://git.kernel.org/stable/c/db231af842868268839f9f9619c68cb27830d8be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64395.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64395
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
