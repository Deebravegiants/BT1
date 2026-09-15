# [H] ksmbd: fix use-after-free in __close_file_table_ids()

## Summary
Severity: High
Advisory: CVE-2026-74522
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74522
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in __close_file_table_ids()

A ksmbd_file can remain alive after logical close while another session
holds a temporary reference obtained through ksmbd_lookup_fd_inode().
ksmbd_close_fd() currently marks the file closed and drops the idr-owned
reference, but leaves the pointer published in the closing session's idr
until the final reference is dropped.

If the foreign holder performs the final ksmbd_fd_put(), __put_fd_final()
supplies the foreign session's file table to __ksmbd_close_fd(). The object
is then freed without being removed from its owner's idr, and the owner
session later dereferences the stale pointer during file-table teardown.

Remove the volatile id from the owner's idr while ksmbd_close_fd() still
holds that table's lock, and clear volatile_id before dropping
the idr-owned reference. A later foreign final put then only performs
physical destruction and cannot remove the object from the wrong table.

## References
- https://git.kernel.org/stable/c/0c3918c2cee62ec6c9de8d5c73ebfe6f833961ac
- https://git.kernel.org/stable/c/19bfd90d5aaf63217735d81964585c5306158e5f
- https://git.kernel.org/stable/c/67aaec2a1fdce3e1dde46c45b5d1ef8cf22f65cd
- https://git.kernel.org/stable/c/9be4a66f019ea90bd9deca70511f4f9ffebf5c6f
- https://git.kernel.org/stable/c/cffbdc86393b0235383a20c8c59bc32f16036459
- https://git.kernel.org/stable/c/e7188199eff46a636f3436356f0aae039be6dd66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74522.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74522
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
