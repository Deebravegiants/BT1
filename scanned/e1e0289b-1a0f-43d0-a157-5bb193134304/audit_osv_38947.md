# [H] xfs: remove xfs_attr_leaf_hasname

## Summary
Severity: High
Advisory: CVE-2026-43153
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43153
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: remove xfs_attr_leaf_hasname

The calling convention of xfs_attr_leaf_hasname() is problematic, because
it returns a NULL buffer when xfs_attr3_leaf_read fails, a valid buffer
when xfs_attr3_leaf_lookup_int returns -ENOATTR or -EEXIST, and a
non-NULL buffer pointer for an already released buffer when
xfs_attr3_leaf_lookup_int fails with other error values.

Fix this by simply open coding xfs_attr_leaf_hasname in the callers, so
that the buffer release code is done by each caller of
xfs_attr3_leaf_read.

## References
- https://git.kernel.org/stable/c/2fbc8421d1db102c0e5458607e042a23a03648b1
- https://git.kernel.org/stable/c/3a65ea768b8094e4699e72f9ab420eb9e0f3f568
- https://git.kernel.org/stable/c/457121c01f609b9934addbb04d5c1ef638c71c61
- https://git.kernel.org/stable/c/530082df991903f3330354e99e0cb7b05debfa86
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43153.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43153
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
