# [H] NFSv4/pNFS: Clear NFS_INO_LAYOUTCOMMIT in pnfs_mark_layout_stateid_invalid

## Summary
Severity: High
Advisory: CVE-2025-68349
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68349
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4/pNFS: Clear NFS_INO_LAYOUTCOMMIT in pnfs_mark_layout_stateid_invalid

Fixes a crash when layout is null during this call stack:

write_inode
    -> nfs4_write_inode
        -> pnfs_layoutcommit_inode

pnfs_set_layoutcommit relies on the lseg refcount to keep the layout
around. Need to clear NFS_INO_LAYOUTCOMMIT otherwise we might attempt
to reference a null layout.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/084bebe82ad86f718a3af84f34761863e63164ed
- https://git.kernel.org/stable/c/104080582ae0aa6dce6c6d75ff89062efe84673b
- https://git.kernel.org/stable/c/38694f9aae00459ab443a7dc8b3949a6b33b560a
- https://git.kernel.org/stable/c/59947dff0fb7c19c09ce6dccbcd253fd542b6c25
- https://git.kernel.org/stable/c/b6e4e3a08c03200cc4b8067ec8ab3172a989d6fc
- https://git.kernel.org/stable/c/ca2e7fdad7c683b64821c94a58b9b68733214dad
- https://git.kernel.org/stable/c/e0f8058f2cb56de0b7572f51cd563ca5debce746
- https://git.kernel.org/stable/c/f718f9ea6094843b8c059b073af49ad61e9f49bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68349.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68349
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
