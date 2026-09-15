# [H] afs: Fix the volume AFS_VOLUME_RM_TREE is set on

## Summary
Severity: High
Advisory: CVE-2026-72371
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72371
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix the volume AFS_VOLUME_RM_TREE is set on

Fix afs_insert_volume_into_cell() to set AFS_VOLUME_RM_TREE on the volume
replaced, not the new volume, as it's now removed from the cell's volume
tree.  This will cause the old volume to be removed from the tree twice and
the new volume never to be removed.

## References
- https://git.kernel.org/stable/c/158c5a0b1dfc0e6a419efe18404047a4d2dff59e
- https://git.kernel.org/stable/c/1607075220cf57161d9116512994c159eacefc0d
- https://git.kernel.org/stable/c/56b4e4b26f84411d880f968a539207b0a8889c8c
- https://git.kernel.org/stable/c/6fa9a8a73e16aa22fce6e41cc00d59c767f0a540
- https://git.kernel.org/stable/c/c421bc6b957e56e45e12dbaeaf70a60db20d6465
- https://git.kernel.org/stable/c/d0c8ad418b47891a03426c5e02ebb0537f8d68f8
- https://git.kernel.org/stable/c/d154c20837f379343f192d4b8d9dd4ef145562e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72371.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72371
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
